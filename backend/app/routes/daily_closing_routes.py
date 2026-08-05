"""
Daily Closing routes - End of shift cash reconciliation
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from app.services.business_time import day_bounds_utc, gym_id_for_branch, gym_today
from app.models.daily_closing import DailyClosing
from app.models.transaction import Transaction, PaymentMethod
from app.utils import (
    success_response, error_response, role_required,
    paginate, format_pagination_response, get_current_user,
    get_accessible_branch_ids, scope_query_to_branches
)
from app.models.user import UserRole, FINANCE_READ_ROLES
from app.extensions import db

daily_closing_bp = Blueprint('daily_closing', __name__, url_prefix='/api/daily-closings')


def _totals_by_payment_method(branch_id, closing_date):
    """Sum a branch's takings for one day, split by payment method.

    Amounts are net of discount, matching how revenue is computed everywhere
    else (reports, finance, branch performance, the client's payment list).
    This module used to total the gross `amount`, so expected cash came out
    high by exactly the discounts given — and the reconciliation then reported
    a cash shortage of that size on every day anyone discounted anything.

    The day is the *gym's* day. Comparing on UTC dates put anything taken after
    local midnight into the next day's closing, so a branch trading late was
    reliably short on the night and over the next morning.
    """
    gym_id = gym_id_for_branch(branch_id)
    start_utc, end_utc = day_bounds_utc(gym_id, closing_date)

    transactions = Transaction.query.filter(
        and_(
            Transaction.branch_id == branch_id,
            Transaction.transaction_date >= start_utc,
            Transaction.transaction_date < end_utc,
        )
    ).all()

    totals = {PaymentMethod.CASH: 0.0, PaymentMethod.NETWORK: 0.0,
              PaymentMethod.TRANSFER: 0.0}
    for txn in transactions:
        net = float(txn.amount) - float(txn.discount or 0)
        if txn.payment_method in totals:
            totals[txn.payment_method] += net

    return (
        totals[PaymentMethod.CASH],
        totals[PaymentMethod.NETWORK],
        totals[PaymentMethod.TRANSFER],
        len(transactions),
    )


def parse_actual_cash(raw):
    """The physical cash count, or (None, error).

    Typed by a human at the end of a shift, so it arrives as whatever the form
    sent. Unchecked, ``float(raw)`` on a non-numeric value raised straight out
    of the handler as a 500, and a negative count was stored as-is — producing
    a cash difference that reads like a huge shortfall.
    """
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None, error_response('actual_cash must be numeric', 400)
    if value != value or value in (float('inf'), float('-inf')):
        return None, error_response('actual_cash must be a real number', 400)
    if value < 0:
        return None, error_response('actual_cash cannot be negative', 400)
    return value, None


@daily_closing_bp.route('', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT, UserRole.BRANCH_MANAGER)
def get_daily_closings():
    """Get all daily closings (paginated)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    branch_id = request.args.get('branch_id', type=int)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    
    user = get_current_user()
    
    query = DailyClosing.query
    
    # Branch filtering based on role
    query = scope_query_to_branches(query, DailyClosing.branch_id, user, branch_id)
    
    # Date filtering
    if start_date:
        query = query.filter(DailyClosing.closing_date >= start_date)
    if end_date:
        query = query.filter(DailyClosing.closing_date <= end_date)
    
    query = query.order_by(DailyClosing.closing_date.desc())
    
    items, total, pages, current_page = paginate(query, page, per_page)
    
    return success_response({
        'items': [item.to_dict() for item in items],
        'pagination': {
            'total': total,
            'pages': pages,
            'current_page': current_page,
            'per_page': per_page
        }
    })


@daily_closing_bp.route('/<int:closing_id>', methods=['GET'])
@jwt_required()
@role_required(*FINANCE_READ_ROLES)
def get_daily_closing(closing_id):
    """Get daily closing by ID"""
    closing = db.session.get(DailyClosing, closing_id)
    
    if not closing:
        return error_response("Daily closing not found", 404)
    
    # Check branch access
    user = get_current_user()
    accessible = get_accessible_branch_ids(user)
    if accessible is not None and closing.branch_id not in accessible:
        return error_response("Access denied", 403)

    return success_response(closing.to_dict())


@daily_closing_bp.route('/calculate', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK, UserRole.CENTRAL_ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT, UserRole.ACCOUNTANT)
def calculate_expected_cash():
    """Calculate expected cash for a given date and branch"""
    data = request.json
    
    if not data or 'branch_id' not in data:
        return error_response("branch_id is required", 400)
    
    branch_id = data['branch_id']
    closing_date_str = data.get('date') or gym_today(
        gym_id_for_branch(data.get('branch_id'))).isoformat()
    
    try:
        closing_date = datetime.strptime(closing_date_str, '%Y-%m-%d').date()
    except ValueError:
        return error_response("Invalid date format. Use YYYY-MM-DD", 400)
    
    user = get_current_user()

    # Check branch access
    _accessible = get_accessible_branch_ids(user)
    if _accessible is not None and branch_id not in _accessible:
        return error_response("Access denied to this branch", 403)

    cash_total, network_total, transfer_total, txn_count = _totals_by_payment_method(
        branch_id, closing_date
    )

    return success_response({
        'branch_id': branch_id,
        'closing_date': closing_date.isoformat(),
        'expected_cash': cash_total,
        'network_total': network_total,
        'transfer_total': transfer_total,
        'total_revenue': cash_total + network_total + transfer_total,
        'transaction_count': txn_count
    })


@daily_closing_bp.route('', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK, UserRole.CENTRAL_ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT, UserRole.ACCOUNTANT)
def create_daily_closing():
    """Create daily closing (end of shift)"""
    data = request.json
    
    if not data:
        return error_response("Request body is required", 400)
    
    required_fields = ['branch_id', 'actual_cash']
    for field in required_fields:
        if field not in data:
            return error_response(f"{field} is required", 400)
    
    branch_id = data['branch_id']
    actual_cash, cash_error = parse_actual_cash(data['actual_cash'])
    if cash_error:
        return cash_error
    closing_date_str = data.get('date') or gym_today(
        gym_id_for_branch(data.get('branch_id'))).isoformat()
    notes = data.get('notes', '')
    
    try:
        closing_date = datetime.strptime(closing_date_str, '%Y-%m-%d').date()
    except ValueError:
        return error_response("Invalid date format. Use YYYY-MM-DD", 400)
    
    user = get_current_user()

    # Check branch access
    _accessible = get_accessible_branch_ids(user)
    if _accessible is not None and branch_id not in _accessible:
        return error_response("Access denied to this branch", 403)

    # Check if closing already exists for this date and branch
    existing = DailyClosing.query.filter(
        and_(
            DailyClosing.branch_id == branch_id,
            DailyClosing.closing_date == closing_date
        )
    ).first()
    
    if existing:
        return error_response("Daily closing already exists for this date", 400)
    
    # Calculate expected values
    expected_cash, network_total, transfer_total, _ = _totals_by_payment_method(
        branch_id, closing_date
    )

    total_revenue = expected_cash + network_total + transfer_total
    cash_difference = actual_cash - expected_cash

    # Create closing
    closing = DailyClosing(
        branch_id=branch_id,
        closing_date=closing_date,
        expected_cash=expected_cash,
        actual_cash=actual_cash,
        cash_difference=cash_difference,
        network_total=network_total,
        transfer_total=transfer_total,
        total_revenue=total_revenue,
        closed_by=user.id,
        notes=notes
    )

    db.session.add(closing)
    try:
        db.session.commit()
    except IntegrityError:
        # Lost the race against another till closing the same day. The check
        # above cannot prevent this; the unique constraint can, and this turns
        # it into the same answer the check would have given.
        db.session.rollback()
        return error_response("Daily closing already exists for this date", 409)

    return success_response(
        closing.to_dict(),
        "Daily closing created successfully",
        201
    )


@daily_closing_bp.route('/today', methods=['GET'])
@jwt_required()
@role_required(*FINANCE_READ_ROLES)
def get_today_status():
    """Check if today's closing has been done for user's branch"""
    user = get_current_user()
    
    if not user.branch_id:
        return error_response("User not assigned to a branch", 403)
    
    today = gym_today(gym_id_for_branch(user.branch_id))

    # Check if closing exists for today
    closing = DailyClosing.query.filter(
        and_(
            DailyClosing.branch_id == user.branch_id,
            DailyClosing.closing_date == today
        )
    ).first()
    
    cash_total, _, _, txn_count = _totals_by_payment_method(user.branch_id, today)

    return success_response({
        'branch_id': user.branch_id,
        'date': today.isoformat(),
        'is_closed': closing is not None,
        'closing': closing.to_dict() if closing else None,
        'expected_cash': cash_total,
        'transaction_count': txn_count
    })
