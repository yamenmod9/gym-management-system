"""
Validation routes - For gate scanners and reception to validate entries
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.models import EntryLog, EntryType, EntryStatus, Subscription, SubscriptionStatus, Customer
from app.services.qr_service import QRService
from app.utils import (
    success_response, error_response, get_current_user, role_required,
    scope_query_to_branches,
)
from app.models.user import UserRole
from app.services.gym_rules import gym_rule
from app.extensions import db

validation_bp = Blueprint('validation', __name__, url_prefix='/api/validation')


def _entry_subscription(customer):
    """The member's subscription that grants gym entry, honouring gym rules.

    A member may hold several at once; metering a private-training package at
    the door would consume sessions the captain never delivered.
    """
    return Subscription.entry_subscription_for(
        customer.id,
        allow_non_entry=gym_rule(
            customer.branch.gym_id if customer.branch else None,
            'pt_only_members_may_enter',
        ),
    )


@validation_bp.route('/qr', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def validate_qr_code():
    """
    Validate QR code and process entry
    
    Request body:
        - qr_token: JWT token from client's QR code
        - branch_id: Branch where scan occurred (optional, uses staff branch)
    
    Returns:
        - entry: Entry log data
        - customer: Customer brief info
        - subscription: Subscription brief info
    """
    data = request.get_json()
    
    if not data or 'qr_token' not in data:
        return error_response('QR token is required', 400)
    
    qr_token = data['qr_token']
    
    # Get current staff user
    staff_user = get_current_user()
    branch_id = data.get('branch_id', staff_user.branch_id)
    
    # Validate QR token
    payload = QRService.validate_qr_token(qr_token)
    
    if not payload:
        # Create denied entry log
        return error_response('Invalid or expired QR code', 401)
    
    customer_id = payload.get('customer_id')
    subscription_id = payload.get('subscription_id')
    
    # Validate entry permissions
    is_valid, reason, subscription, coins_to_deduct = QRService.validate_entry(
        customer_id=customer_id,
        subscription_id=subscription_id,
        branch_id=branch_id
    )
    
    if not is_valid:
        # Create denied entry log
        entry = EntryLog.create_denied_entry(
            customer_id=customer_id,
            branch_id=branch_id,
            entry_type=EntryType.QR_SCAN,
            denial_reason=reason,
            subscription_id=subscription_id,
            processed_by_user_id=staff_user.id
        )
        db.session.commit()
        
        return error_response(reason, 403, {
            'entry_id': entry.id,
            'status': 'denied'
        })
    
    # Deduct entry if needed
    if coins_to_deduct > 0 and subscription:
        QRService.deduct_entry(subscription, coins_to_deduct)
    
    # Create approved entry log
    entry = EntryLog.create_entry(
        customer_id=customer_id,
        branch_id=branch_id,
        entry_type=EntryType.QR_SCAN,
        subscription_id=subscription_id,
        validation_token=qr_token[:50],  # Store truncated token
        coins_deducted=coins_to_deduct,
        processed_by_user_id=staff_user.id
    )
    
    db.session.commit()
    
    return success_response({
        'entry': entry.to_dict(),
        'customer': {
            'id': entry.customer.id,
            'full_name': entry.customer.full_name,
            'qr_code': entry.customer.qr_code
        },
        'subscription': {
            'id': subscription.id,
            'remaining_visits': subscription.remaining_visits,
            'remaining_classes': subscription.remaining_classes,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None
        } if subscription else None
    }, 'Entry approved')


@validation_bp.route('/barcode', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def validate_barcode():
    """
    Validate static barcode (customer's QR code) and process entry
    
    Request body:
        - barcode: Customer's barcode (e.g., GYM-123)
        - branch_id: Branch where scan occurred (optional, uses staff branch)
    
    Returns:
        - entry: Entry log data
        - customer: Customer data
        - subscription: Active subscription data
    """
    data = request.get_json()
    
    if not data or 'barcode' not in data:
        return error_response('Barcode is required', 400)
    
    barcode = data['barcode']
    
    # Get current staff user
    staff_user = get_current_user()
    branch_id = data.get('branch_id', staff_user.branch_id)
    
    # Validate barcode
    customer, error = QRService.validate_barcode(barcode)
    
    if error:
        return error_response(error, 400)
    
    # The subscription that grants entry — not just any the member holds.
    subscription = _entry_subscription(customer)

    if not subscription:
        # Create denied entry
        entry = EntryLog.create_denied_entry(
            customer_id=customer.id,
            branch_id=branch_id,
            entry_type=EntryType.BARCODE,
            denial_reason='No active subscription',
            processed_by_user_id=staff_user.id
        )
        db.session.commit()
        
        return error_response('No active subscription found', 403, {
            'entry_id': entry.id,
            'customer': customer.to_dict(include_temp_password=True)
        })
    
    # Validate entry
    is_valid, reason, subscription, coins_to_deduct = QRService.validate_entry(
        customer_id=customer.id,
        subscription_id=subscription.id,
        branch_id=branch_id
    )
    
    if not is_valid:
        # Create denied entry
        entry = EntryLog.create_denied_entry(
            customer_id=customer.id,
            branch_id=branch_id,
            entry_type=EntryType.BARCODE,
            denial_reason=reason,
            subscription_id=subscription.id,
            processed_by_user_id=staff_user.id
        )
        db.session.commit()
        
        return error_response(reason, 403, {
            'entry_id': entry.id,
            'customer': customer.to_dict(include_temp_password=True),
            'subscription': subscription.to_dict()
        })
    
    # Deduct entry
    if coins_to_deduct > 0:
        QRService.deduct_entry(subscription, coins_to_deduct)
    
    # Create entry log
    entry = EntryLog.create_entry(
        customer_id=customer.id,
        branch_id=branch_id,
        entry_type=EntryType.BARCODE,
        subscription_id=subscription.id,
        validation_token=barcode,
        coins_deducted=coins_to_deduct,
        processed_by_user_id=staff_user.id
    )
    
    db.session.commit()
    
    return success_response({
        'entry': entry.to_dict(),
        'customer': customer.to_dict(include_temp_password=True),
        'subscription': {
            'id': subscription.id,
            'service_name': subscription.service.name if subscription.service else None,
            'remaining_visits': subscription.remaining_visits,
            'remaining_classes': subscription.remaining_classes,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None
        }
    }, 'Entry approved')


@validation_bp.route('/manual', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def manual_entry():
    """
    Manually process entry (for when QR/barcode doesn't work)
    
    Request body:
        - customer_id: Customer ID
        - branch_id: Branch where entry occurred (optional, uses staff branch)
        - notes: Optional notes about why manual entry was needed
    
    Returns:
        - entry: Entry log data
        - customer: Customer data
        - subscription: Active subscription data
    """
    data = request.get_json()
    
    if not data or 'customer_id' not in data:
        return error_response('Customer ID is required', 400)
    
    customer_id = data['customer_id']
    
    # Get current staff user
    staff_user = get_current_user()
    branch_id = data.get('branch_id', staff_user.branch_id)
    notes = data.get('notes', 'Manual entry')
    
    # Get customer
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return error_response('Customer not found', 404)
    
    if not customer.is_active:
        return error_response('Customer account is inactive', 403)
    
    # The subscription that grants entry — not just any the member holds.
    subscription = _entry_subscription(customer)

    if not subscription:
        return error_response('No active subscription found', 403)
    
    # Validate entry
    is_valid, reason, subscription, coins_to_deduct = QRService.validate_entry(
        customer_id=customer_id,
        subscription_id=subscription.id,
        branch_id=branch_id
    )
    
    if not is_valid:
        # Create denied entry
        entry = EntryLog.create_denied_entry(
            customer_id=customer_id,
            branch_id=branch_id,
            entry_type=EntryType.MANUAL,
            denial_reason=reason,
            subscription_id=subscription.id,
            processed_by_user_id=staff_user.id
        )
        db.session.commit()
        
        return error_response(reason, 403, {
            'entry_id': entry.id
        })
    
    # Deduct entry
    if coins_to_deduct > 0:
        QRService.deduct_entry(subscription, coins_to_deduct)
    
    # Create entry log
    entry = EntryLog.create_entry(
        customer_id=customer_id,
        branch_id=branch_id,
        entry_type=EntryType.MANUAL,
        subscription_id=subscription.id,
        coins_deducted=coins_to_deduct,
        processed_by_user_id=staff_user.id,
        notes=notes
    )
    
    db.session.commit()
    
    return success_response({
        'entry': entry.to_dict(),
        'customer': customer.to_dict(include_temp_password=True),
        'subscription': {
            'id': subscription.id,
            'service_name': subscription.service.name if subscription.service else None,
            'remaining_visits': subscription.remaining_visits,
            'remaining_classes': subscription.remaining_classes,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None
        }
    }, 'Entry approved')


@validation_bp.route('/entry-logs', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK,
               UserRole.BRANCH_ACCOUNTANT, UserRole.CENTRAL_ACCOUNTANT, UserRole.TRAINER)
def get_entry_logs():
    """
    Get entry logs (for staff to review)
    
    Query params:
        - page: Page number (default 1)
        - per_page: Items per page (default 20)
        - branch_id: Filter by branch
        - customer_id: Filter by customer
        - status: Filter by status (approved/denied)
        - from_date: Start date filter
        - to_date: End date filter
    
    Returns:
        Paginated list of entry logs
    """
    from app.utils import paginate, format_pagination_response
    
    staff_user = get_current_user()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    branch_id = request.args.get('branch_id', type=int)
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = EntryLog.query

    # Branch filtering based on role. Uses the shared helper rather than a
    # local rule: the previous hand-rolled version only filtered when the
    # caller had a branch_id of their own, so a regional manager (whose scope
    # lives in managed_branches, leaving branch_id NULL) and an owner who
    # passed no branch_id both fell through with no WHERE clause at all and
    # read every gym's entry logs.
    query = scope_query_to_branches(query, EntryLog.branch_id, staff_user, branch_id)

    # Customer filter
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    # Status filter. Resolved through the enum by value ('approved') and by
    # name ('APPROVED'); passing the raw string straight to the query makes
    # Postgres reject it outright as an invalid enum literal (a 500).
    if status:
        try:
            query = query.filter_by(entry_status=EntryStatus(status.lower()))
        except ValueError:
            return error_response(
                f"Invalid status. Use one of: {', '.join(s.value for s in EntryStatus)}",
                400,
            )

    # Date filters
    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date)
            query = query.filter(EntryLog.entry_time >= from_dt)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date)
            query = query.filter(EntryLog.entry_time <= to_dt)
        except ValueError:
            pass
    
    query = query.order_by(EntryLog.entry_time.desc())
    
    items, total, pages, current_page = paginate(query, page, per_page)
    
    entries = [entry.to_dict() for entry in items]
    
    return success_response({
        'entries': entries,
        'pagination': {
            'total': total,
            'pages': pages,
            'current_page': current_page,
            'per_page': per_page
        }
    })
