"""
Finance routes - Financial management and reporting
Maps /api/finance/* for Flutter app compatibility
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Expense, DailyClosing, Transaction
from app.models.expense import ExpenseStatus, ExpenseCategory
from app.utils import (
    success_response, error_response, get_current_user, role_required,
    paginate, format_pagination_response, scope_query_to_branches
)
from app.models.user import UserRole, FINANCE_READ_ROLES
from app.extensions import db
from app.schemas import ExpenseSchema, DailyClosingSchema
from datetime import datetime
from sqlalchemy import and_, func

finance_bp = Blueprint('finance', __name__, url_prefix='/api/finance')


@finance_bp.route('/expenses', methods=['GET'])
@jwt_required()
@role_required(*FINANCE_READ_ROLES)
def get_expenses():
    """
    Get expenses with filtering
    
    Query params:
        - branch_id: Filter by branch
        - status: pending, approved, rejected
        - date_from: Start date (YYYY-MM-DD)
        - date_to: End date (YYYY-MM-DD)
        - category: Filter by expense category
        - page: Page number
        - limit: Items per page
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', request.args.get('per_page', 20), type=int)
    branch_id = request.args.get('branch_id', type=int)
    status = request.args.get('status')
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    current_user = get_current_user()
    
    # Build query
    query = Expense.query
    
    # Role-based filtering
    query = scope_query_to_branches(query, Expense.branch_id, current_user, branch_id)
    
    # Status filter
    if status:
        try:
            expense_status = ExpenseStatus(status)
            query = query.filter(Expense.status == expense_status)
        except ValueError:
            pass

    # Category filter
    if category:
        try:
            query = query.filter(Expense.category == ExpenseCategory.parse(category))
        except ValueError as e:
            return error_response(str(e), 400)

    # Date range filter, on expense_date — the date the money was spent, which
    # is what an accountant means by "expenses in March". Filtering created_at
    # answered "expenses *entered* in March" instead, so a receipt filed late
    # landed in the wrong month.
    #
    # date_to covers the whole day; as a bare <= against midnight it excluded
    # the final day of every range.
    if date_from:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Expense.expense_date >= start_date)
        except ValueError:
            pass

    if date_to:
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Expense.expense_date <= end_date)
        except ValueError:
            pass

    # Order by most recent
    query = query.order_by(Expense.created_at.desc())

    # Totals for the whole filtered set, computed in SQL. Summing `items` added
    # up only the rows on the current page, so the reported totals shrank as
    # the user paged through them.
    # order_by(None): Postgres rejects an aggregate select that still carries
    # an ORDER BY on a non-grouped column, while SQLite tolerates it.
    def _total_for(status):
        return float(
            query.order_by(None)
            .with_entities(func.coalesce(func.sum(Expense.amount), 0))
            .filter(Expense.status == status)
            .scalar() or 0
        )

    pending_total = _total_for(ExpenseStatus.PENDING)
    approved_total = _total_for(ExpenseStatus.APPROVED)

    # Paginate
    items, total, pages, current_page = paginate(query, page, per_page)

    # Format response
    schema = ExpenseSchema()
    response_data = format_pagination_response(items, total, pages, current_page, schema)
    response_data['total_pending'] = pending_total
    response_data['total_approved'] = approved_total
    
    return success_response(response_data)


@finance_bp.route('/cash-differences', methods=['GET'])
@jwt_required()
@role_required([UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT, UserRole.ACCOUNTANT, UserRole.BRANCH_MANAGER])
def get_cash_differences():
    """
    Get cash difference records from daily closings
    
    Query params:
        - branch_id: Filter by branch
        - date_from: Start date (YYYY-MM-DD)
        - date_to: End date (YYYY-MM-DD)
    """
    branch_id = request.args.get('branch_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    current_user = get_current_user()
    
    # Build query for daily closings
    query = DailyClosing.query
    
    # Role-based filtering
    query = scope_query_to_branches(query, DailyClosing.branch_id, current_user, branch_id)
    
    # Date range filter
    if date_from:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(DailyClosing.closing_date >= start_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(DailyClosing.closing_date <= end_date)
        except ValueError:
            pass
    
    # Order by most recent
    query = query.order_by(DailyClosing.closing_date.desc())
    
    closings = query.all()
    
    # Format as cash differences
    cash_differences = []
    total_difference = 0.0
    
    for closing in closings:
        cash_differences.append({
            'id': closing.id,
            'branch_id': closing.branch_id,
            'branch_name': closing.branch.name if closing.branch else 'N/A',
            'date': closing.closing_date.isoformat(),
            'expected_cash': float(closing.expected_cash) if closing.expected_cash else 0.0,
            'actual_cash': float(closing.actual_cash) if closing.actual_cash else 0.0,
            'difference': float(closing.cash_difference) if closing.cash_difference else 0.0,
            'notes': closing.notes,
            'recorded_by': closing.closed_by_user.username if closing.closed_by_user else 'N/A'
        })
        
        total_difference += float(closing.cash_difference) if closing.cash_difference else 0.0

    return success_response({
        'data': cash_differences,
        'total_difference': total_difference
    })


@finance_bp.route('/daily-sales', methods=['GET'])
@jwt_required()
@role_required(*FINANCE_READ_ROLES)
def get_daily_sales():
    """
    Get daily sales summary
    
    Query params:
        - date: Specific date (YYYY-MM-DD, default: today)
        - branch_id: Filter by branch
    """
    date_str = request.args.get('date')
    branch_id = request.args.get('branch_id', type=int)
    
    if date_str:
        try:
            report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return error_response('Invalid date format. Use YYYY-MM-DD', 400)
    else:
        report_date = datetime.utcnow().date()
    
    current_user = get_current_user()
    
    # Build query for transactions on this date, on transaction_date so this
    # agrees with the daily closing for the same day.
    start_datetime = datetime.combine(report_date, datetime.min.time())
    end_datetime = datetime.combine(report_date, datetime.max.time())

    query = Transaction.query.filter(
        and_(
            Transaction.transaction_date >= start_datetime,
            Transaction.transaction_date <= end_datetime
        )
    )

    # Branch scope. The hand-rolled version exempted owners and accountants
    # from any filter unless they passed ?branch_id, so a gym owner asking for
    # today's sales was shown every gym on the platform added together.
    query = scope_query_to_branches(query, Transaction.branch_id, current_user, branch_id)

    transactions = query.all()
    
    # Calculate totals by payment method
    cash_total = 0.0
    network_total = 0.0
    transfer_total = 0.0

    for t in transactions:
        net_amount = float(t.amount) - float(t.discount or 0)
        if t.payment_method.value == 'cash':
            cash_total += net_amount
        elif t.payment_method.value == 'network':
            network_total += net_amount
        elif t.payment_method.value == 'transfer':
            transfer_total += net_amount

    total_sales = cash_total + network_total + transfer_total

    return success_response({
        'date': report_date.isoformat(),
        'total_sales': total_sales,
        'cash_sales': cash_total,
        'network_sales': network_total,
        'transfer_sales': transfer_total,
        'card_sales': network_total,
        'online_sales': transfer_total,
        'transaction_count': len(transactions)
    })
