"""
Payments routes - Alias for transactions routes
Maps /api/payments/* to transaction functionality for Flutter app compatibility
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Transaction, DailyClosing, Branch
from app.models.transaction import PaymentMethod, TransactionType, net_amount
from app.utils import (
    success_response, error_response, get_current_user, role_required,
    paginate, format_pagination_response, get_accessible_branch_ids,
    scope_query_to_branches
)
from app.models.user import UserRole, FINANCE_READ_ROLES
from app.extensions import db
from app.schemas import TransactionSchema, DailyClosingSchema
from datetime import datetime, date, timedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payments_bp.route('', methods=['GET'])
@jwt_required()
@role_required(*FINANCE_READ_ROLES)
def get_payments():
    """
    Get all payments/transactions with filtering
    
    Query params:
        - branch_id: Filter by branch
        - payment_method: cash, card, online
        - date_from: Start date (YYYY-MM-DD)
        - date_to: End date (YYYY-MM-DD)
        - page: Page number
        - limit: Items per page
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', request.args.get('per_page', 20), type=int)
    branch_id = request.args.get('branch_id', type=int)
    payment_method = request.args.get('payment_method')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    current_user = get_current_user()
    
    # Build query
    query = Transaction.query
    
    # Role-based filtering
    query = scope_query_to_branches(query, Transaction.branch_id, current_user, branch_id)
    
    # Payment method filter
    if payment_method:
        try:
            method_enum = PaymentMethod(payment_method.lower())
            query = query.filter(Transaction.payment_method == method_enum)
        except ValueError:
            pass
    
    # Date range filter.
    #
    # On transaction_date, the business date, which is what daily closing and
    # every report already use — filtering on created_at here meant the same
    # day could total differently depending on which screen you asked.
    #
    # date_to is inclusive of the whole day: parsed as midnight and compared
    # with <=, a from/to of the same date matched nothing, so asking for one
    # day's takings returned an empty list.
    if date_from:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Transaction.transaction_date >= start_date)
        except ValueError:
            pass

    if date_to:
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Transaction.transaction_date < end_date)
        except ValueError:
            pass

    # Order by most recent
    query = query.order_by(Transaction.transaction_date.desc())

    # The total for the whole filtered range, computed in SQL, net of discount.
    # It used to sum the gross `amount` of the rows on the current page only —
    # so it read high by exactly the discounts given, and shrank as you paged,
    # while sitting next to a `total` count covering everything.
    #
    # order_by(None) matters: Postgres rejects an aggregate select that still
    # carries an ORDER BY on a non-grouped column, and SQLite does not — so
    # leaving it on passes every local test and 500s in production.
    total_amount = float(
        query.order_by(None)
        .with_entities(func.coalesce(func.sum(net_amount()), 0))
        .scalar() or 0
    )

    # Paginate
    items, total, pages, current_page = paginate(query, page, per_page)

    # Format response
    schema = TransactionSchema()
    response_data = format_pagination_response(items, total, pages, current_page, schema)
    response_data['total_amount'] = total_amount

    return success_response(response_data)


@payments_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
@role_required(*FINANCE_READ_ROLES)
def get_payment(payment_id):
    """Get payment by ID"""
    transaction = db.session.get(Transaction, payment_id)
    
    if not transaction:
        return error_response("Payment not found", 404)
    
    # Check access
    current_user = get_current_user()
    accessible = get_accessible_branch_ids(current_user)
    if accessible is not None and transaction.branch_id not in accessible:
        return error_response("Access denied", 403)

    schema = TransactionSchema()
    return success_response(schema.dump(transaction))


@payments_bp.route('/record', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK, UserRole.CENTRAL_ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT, UserRole.ACCOUNTANT])
def record_payment():
    """
    Record a new payment/transaction
    
    Request body:
        - subscription_id: Subscription ID
        - amount: Payment amount
        - discount: Discount amount (optional)
        - payment_method: cash, card, online
        - notes: Optional notes
    """
    data = request.get_json()
    
    if not data:
        return error_response('Request body is required', 400)
    
    required_fields = ['subscription_id', 'amount', 'payment_method']
    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', 400)
    
    # Get subscription to determine branch
    from app.models import Subscription
    subscription = db.session.get(Subscription, data['subscription_id'])
    
    if not subscription:
        return error_response('Subscription not found', 404)
    
    # Verify branch access
    current_user = get_current_user()
    accessible = get_accessible_branch_ids(current_user)
    if accessible is not None and subscription.branch_id not in accessible:
        return error_response('Access denied', 403)
    
    # Create transaction
    try:
        payment_method_enum = PaymentMethod(data['payment_method'].lower())
    except ValueError:
        return error_response('Invalid payment method. Use: cash, card, or online', 400)
    
    try:
        amount = float(data['amount'])
        discount = float(data.get('discount', 0))
    except (TypeError, ValueError):
        return error_response('amount and discount must be numeric', 400)

    if amount < 0 or discount < 0:
        return error_response('amount and discount cannot be negative', 400)
    if discount > amount:
        return error_response('discount cannot exceed the amount', 400)

    # transaction_type is NOT NULL and has no server default, so leaving it
    # unset made every call to this endpoint fail with an IntegrityError —
    # surfacing as a 500. A payment against an existing subscription is a
    # renewal unless the caller says otherwise.
    try:
        transaction_type = TransactionType(
            (data.get('transaction_type') or 'renewal').lower()
        )
    except ValueError:
        return error_response('Invalid transaction_type', 400)

    transaction = Transaction(
        subscription_id=subscription.id,
        customer_id=subscription.customer_id,
        branch_id=subscription.branch_id,
        amount=amount,
        discount=discount,
        transaction_type=transaction_type,
        payment_method=payment_method_enum,
        notes=data.get('notes'),
        created_by=current_user.id
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    schema = TransactionSchema()
    return success_response(schema.dump(transaction), 'Payment recorded successfully', 201)


@payments_bp.route('/daily-closing', methods=['POST'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK, UserRole.CENTRAL_ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT, UserRole.ACCOUNTANT])
def daily_closing():
    """
    Create daily closing record
    
    Request body:
        - branch_id: Branch ID
        - date: Closing date (YYYY-MM-DD)
        - expected_cash: Expected cash amount
        - actual_cash: Actual cash amount
        - cash_difference: Difference (actual - expected)
        - notes: Optional notes
    """
    data = request.get_json()
    
    if not data:
        return error_response('Request body is required', 400)
    
    # `expected_cash` is deliberately NOT accepted from the caller — see below.
    # `closing_date` is honoured alongside `date` because that is the key the
    # reception app has always sent, which made this endpoint reject every
    # request it received with "date is required".
    for field in ['branch_id', 'actual_cash']:
        if field not in data:
            return error_response(f'{field} is required', 400)

    branch_id = data['branch_id']
    closing_date = data.get('date') or data.get('closing_date') or date.today().isoformat()

    # Verify branch access. Comparing against current_user.branch_id directly
    # exempted owners entirely and skipped regional managers, who have none.
    current_user = get_current_user()
    accessible = get_accessible_branch_ids(current_user)
    if accessible is not None and branch_id not in accessible:
        return error_response('Access denied', 403)
    
    # Check if already closed for this date
    try:
        date_obj = datetime.strptime(closing_date, '%Y-%m-%d').date()
    except ValueError:
        return error_response('Invalid date format. Use YYYY-MM-DD', 400)
    
    existing = DailyClosing.query.filter_by(
        branch_id=branch_id,
        closing_date=date_obj
    ).first()
    
    if existing:
        return error_response('Daily closing already exists for this date', 409)
    
    # Expected cash and the resulting difference are computed from the
    # transactions on record, never taken from the request. Accepting them
    # from the caller — as this endpoint used to — meant whoever closed the
    # till could paper over a shortfall by sending numbers that agreed.
    from app.routes.daily_closing_routes import (
        _totals_by_payment_method, parse_actual_cash,
    )

    expected_cash, network_total, transfer_total, _ = _totals_by_payment_method(
        branch_id, date_obj
    )

    actual_cash, cash_error = parse_actual_cash(data['actual_cash'])
    if cash_error:
        return cash_error

    closing = DailyClosing(
        branch_id=branch_id,
        closing_date=date_obj,
        expected_cash=expected_cash,
        actual_cash=actual_cash,
        cash_difference=actual_cash - expected_cash,
        network_total=network_total,
        transfer_total=transfer_total,
        total_revenue=expected_cash + network_total + transfer_total,
        notes=data.get('notes'),
        closed_by=current_user.id
    )
    
    db.session.add(closing)
    try:
        db.session.commit()
    except IntegrityError:
        # Two tills closing the same day at once both clear the check above;
        # the unique constraint is what stops the second one landing.
        db.session.rollback()
        return error_response('Daily closing already exists for this date', 409)

    schema = DailyClosingSchema()
    return success_response(schema.dump(closing), 'Daily closing recorded successfully', 201)
