"""
QR Code scanning routes - Alias for validation routes
Maps /api/qr/* to validation functionality for Flutter app compatibility
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Customer, Subscription, SubscriptionStatus, EntryLog, Branch
from app.models.entry_log import EntryType
from app.models.user import UserRole
from app.utils import (
    success_response, error_response, get_current_user, role_required,
    get_accessible_branch_ids
)
from app.extensions import db
from datetime import datetime

qr_bp = Blueprint('qr', __name__, url_prefix='/api/qr')

#: Staff who may work the door.
SCAN_ROLES = (
    UserRole.SUPER_ADMIN, UserRole.OWNER,
    UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK,
)


def _parse_coin_count(raw):
    """Validate a coin quantity from the request body.

    Returns (count, None) or (None, error_response). Deductions were taken
    straight from the body with no validation, and the "enough coins?" check
    (`requested > remaining`) passes trivially for a negative number — so
    posting -50 subtracted a negative and *credited* the member 50 coins.
    """
    try:
        count = int(raw)
    except (TypeError, ValueError):
        return None, error_response('coins_to_deduct must be a whole number', 400)
    if count < 1:
        return None, error_response('coins_to_deduct must be at least 1', 400)
    return count, None


def _usable_subscription(customer):
    """The customer's active, unexpired subscription, or (None, error)."""
    subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status=SubscriptionStatus.ACTIVE
    ).first()

    if not subscription:
        return None, error_response('No active subscription found for this customer', 403)

    # Status alone is not enough: nothing flips a subscription to EXPIRED when
    # its end date passes, so a date check has to happen at the door.
    if subscription.end_date and subscription.end_date < datetime.utcnow().date():
        return None, error_response('Subscription has expired', 403)

    return subscription, None


@qr_bp.route('/scan', methods=['POST'])
@jwt_required()
@role_required(*SCAN_ROLES)
def scan_qr_code():
    """
    Scan QR code and process entry (check-in or coin deduction)
    
    Request body:
        - qr_code: QR code string (e.g., "GYM-151")
        - branch_id: Branch ID for entry
        - action: "check_in" or "deduct_coins"
        - coins_to_deduct: Number of coins to deduct (if action is deduct_coins)
        - service_name: Service name for coin deduction
        - notes: Optional notes
    
    Returns:
        - customer_id, customer_name
        - subscription_status
        - remaining_days, remaining_coins
        - entry_id, entry_time
    """
    data = request.get_json()
    
    if not data or 'qr_code' not in data:
        return error_response('QR code is required', 400)
    
    qr_code = data['qr_code'].strip()
    branch_id = data.get('branch_id')
    action = data.get('action', 'check_in')
    
    # Find customer by QR code
    customer = Customer.query.filter_by(qr_code=qr_code, is_active=True).first()
    
    if not customer:
        return error_response('Invalid QR code or customer not found', 404)
    
    # Verify branch
    if not branch_id:
        return error_response('Branch ID is required', 400)
    
    branch = db.session.get(Branch, branch_id)
    if not branch:
        return error_response('Branch not found', 404)

    # The door being scanned has to be one the operator actually works at.
    # branch_id came straight from the body, so any authenticated staffer
    # could log entries and spend coins against another gym's branch.
    accessible = get_accessible_branch_ids(get_current_user())
    if accessible is not None and branch_id not in accessible:
        return error_response('Access denied to this branch', 403)

    active_subscription, denied = _usable_subscription(customer)
    if denied:
        return denied

    # Only coin-based plans meter entries. remaining_coins is NULL on
    # time-based plans, and comparing None with an int raises a TypeError —
    # scanning a time-based member used to 500 right here.
    meters_coins = active_subscription.remaining_coins is not None

    # Process action
    if action == 'check_in':
        coins_deducted = 1 if meters_coins else 0
        service_name = 'Check-in'
    elif action == 'deduct_coins':
        if not meters_coins:
            return error_response('This subscription does not use coins', 400)
        coins_deducted, invalid = _parse_coin_count(data.get('coins_to_deduct', 1))
        if invalid:
            return invalid
        service_name = data.get('service_name', 'Service')
    else:
        return error_response('Invalid action. Use "check_in" or "deduct_coins"', 400)

    if meters_coins and coins_deducted > active_subscription.remaining_coins:
        return error_response(
            f'Insufficient coins. Available: {active_subscription.remaining_coins}, '
            f'Required: {coins_deducted}',
            403
        )

    # Deduct coins from subscription
    coins_before = active_subscription.remaining_coins
    if meters_coins:
        active_subscription.remaining_coins -= coins_deducted
    
    # Create entry log
    entry_log = EntryLog(
        customer_id=customer.id,
        subscription_id=active_subscription.id,
        branch_id=branch_id,
        entry_type=EntryType.QR_CODE,
        entry_time=datetime.utcnow(),
        notes=data.get('notes', f'{service_name} - {coins_deducted} coin(s) deducted')
    )
    
    db.session.add(entry_log)
    db.session.commit()
    
    return success_response({
        'customer_id': customer.id,
        'customer_name': customer.full_name,
        'subscription_status': active_subscription.status.value,
        'remaining_days': active_subscription.remaining_days,
        'remaining_coins': active_subscription.remaining_coins,
        'coins_before': coins_before,
        'coins_deducted': coins_deducted,
        'entry_id': entry_log.id,
        'entry_time': entry_log.entry_time.isoformat() + 'Z'
    }, f'{service_name} successful')


@qr_bp.route('/deduct-coins', methods=['POST'])
@jwt_required()
@role_required(*SCAN_ROLES)
def deduct_coins():
    """
    Deduct coins from customer subscription
    
    Request body:
        - qr_code: QR code string
        - coins_to_deduct: Number of coins to deduct
        - service_name: Name of service
        - notes: Optional notes
    
    Returns:
        - customer_name
        - coins_before, coins_after
        - subscription_status
    """
    data = request.get_json()
    
    if not data or 'qr_code' not in data:
        return error_response('QR code is required', 400)
    
    qr_code = data['qr_code'].strip()
    coins_to_deduct, invalid = _parse_coin_count(data.get('coins_to_deduct', 1))
    if invalid:
        return invalid
    service_name = data.get('service_name', 'Service')

    # Find customer
    customer = Customer.query.filter_by(qr_code=qr_code, is_active=True).first()

    if not customer:
        return error_response('Invalid QR code', 404)

    current_user = get_current_user()
    accessible = get_accessible_branch_ids(current_user)
    if accessible is not None and customer.branch_id not in accessible:
        return error_response('Invalid QR code', 404)

    active_subscription, denied = _usable_subscription(customer)
    if denied:
        return denied

    if active_subscription.remaining_coins is None:
        return error_response('This subscription does not use coins', 400)

    # Check coins
    if active_subscription.remaining_coins < coins_to_deduct:
        return error_response(
            f'Insufficient coins. Available: {active_subscription.remaining_coins}',
            403
        )

    # Deduct coins
    coins_before = active_subscription.remaining_coins
    active_subscription.remaining_coins -= coins_to_deduct

    branch_id = current_user.branch_id if current_user.branch_id else customer.branch_id
    
    # Create entry log
    entry_log = EntryLog(
        customer_id=customer.id,
        subscription_id=active_subscription.id,
        branch_id=branch_id,
        entry_type=EntryType.QR_CODE,
        entry_time=datetime.utcnow(),
        notes=data.get('notes', f'{service_name} - {coins_to_deduct} coin(s) deducted')
    )
    
    db.session.add(entry_log)
    db.session.commit()
    
    return success_response({
        'customer_name': customer.full_name,
        'coins_before': coins_before,
        'coins_after': active_subscription.remaining_coins,
        'subscription_status': active_subscription.status.value
    }, f'{coins_to_deduct} coins deducted successfully')
