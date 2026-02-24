"""
Client routes - Mobile app endpoints for clients
"""
from flask import Blueprint, request
from datetime import datetime, timedelta
from app.models import Customer, Subscription, SubscriptionStatus, EntryLog, EntryType
from app.services.qr_service import QRService
from app.utils import success_response, error_response, paginate, format_pagination_response
from app.utils.client_auth import client_token_required, get_current_client
from app.extensions import db

client_bp = Blueprint('client', __name__, url_prefix='/api/client')


@client_bp.route('/me', methods=['GET'])
@client_token_required
def get_client_profile():
    """
    Get current client profile
    
    Returns:
        Customer profile with active subscription and QR status
    """
    customer = get_current_client()
    
    if not customer:
        return error_response('Customer not found', 404)
    
    # Get active subscription with proper validation
    from datetime import date
    active_subscription = Subscription.query.filter(
        Subscription.customer_id == customer.id,
        Subscription.status == SubscriptionStatus.ACTIVE,
        db.or_(
            Subscription.subscription_type == 'coins',  # Coins never expire
            Subscription.end_date >= date.today()  # Time-based must not be expired
        )
    ).first()
    
    response_data = customer.to_dict(include_temp_password=False)

    # ── Auto-repair NULL subscription_type on legacy records ─────────────
    if active_subscription and not active_subscription.subscription_type:
        from app.services.subscription_service import SubscriptionService
        sub_type = SubscriptionService._derive_subscription_type(active_subscription.service)
        active_subscription.subscription_type = sub_type

        # Restore coin / session counters if still empty
        if sub_type == 'coins' and active_subscription.remaining_coins is None:
            coin_amount = active_subscription.service.class_limit or 50
            active_subscription.remaining_coins = coin_amount
            active_subscription.total_coins = coin_amount
        elif sub_type in ('sessions', 'training') and active_subscription.remaining_sessions is None:
            session_count = active_subscription.service.class_limit or 10
            active_subscription.remaining_sessions = session_count
            active_subscription.total_sessions = session_count

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    # ─────────────────────────────────────────────────────────────────────

    response_data['active_subscription'] = active_subscription.to_dict() if active_subscription else None
    response_data['password_changed'] = customer.password_changed
    response_data['qr_code_active'] = active_subscription is not None  # Add QR active status
    response_data['qr_image_url'] = f'/api/client/qr-image'
    
    return success_response(response_data)


@client_bp.route('/change-password', methods=['POST'])
@client_token_required
def change_password():
    """
    Change client password
    
    Request body:
        - current_password: Current password
        - new_password: New password (min 6 characters)
    
    Returns:
        Success message
    """
    customer = get_current_client()
    
    if not customer:
        return error_response('Customer not found', 404)
    
    data = request.get_json()
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return error_response('Current password and new password are required', 400)
    
    current_password = data['current_password'].strip()
    new_password = data['new_password'].strip()
    
    # Validate new password
    if len(new_password) < 6:
        return error_response('New password must be at least 6 characters', 400)
    
    # Verify current password
    if not customer.check_password(current_password):
        return error_response('Current password is incorrect', 401)
    
    # Set new password
    customer.set_password(new_password)
    db.session.commit()
    
    return success_response(
        {'password_changed': True},
        'Password changed successfully'
    )


@client_bp.route('/subscription', methods=['GET'])
@client_token_required
def get_client_subscription():
    """
    Get current client's active subscription details
    
    Returns:
        Active subscription with service details
    """
    customer = get_current_client()
    
    if not customer:
        return error_response('Customer not found', 404)
    
    # Get active subscription
    subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        return error_response('No active subscription found', 404)
    
    subscription_data = subscription.to_dict()
    
    # Add service details
    if subscription.service:
        subscription_data['service'] = {
            'id': subscription.service.id,
            'name': subscription.service.name,
            'service_type': subscription.service.service_type.value,
            'has_visits': subscription.service.has_visits,
            'has_classes': subscription.service.has_classes,
            'duration_days': subscription.service.duration_days
        }
    
    return success_response(subscription_data)


@client_bp.route('/subscriptions/history', methods=['GET'])
@client_token_required
def get_subscription_history():
    """
    Get client's subscription history (paginated)
    
    Query params:
        - page: Page number (default 1)
        - per_page: Items per page (default 10)
    
    Returns:
        List of all subscriptions
    """
    customer = get_current_client()
    
    if not customer:
        return error_response('Customer not found', 404)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Subscription.query.filter_by(customer_id=customer.id).order_by(Subscription.created_at.desc())
    
    items, total, pages, current_page = paginate(query, page, per_page)
    
    subscriptions = [sub.to_dict() for sub in items]
    
    return success_response({
        'subscriptions': subscriptions,
        'pagination': {
            'total': total,
            'pages': pages,
            'current_page': current_page,
            'per_page': per_page
        }
    })


@client_bp.route('/qr', methods=['GET'])
@client_token_required
def get_client_qr():
    """
    Generate time-limited QR code for gym entry
    
    Query params:
        - expiry_minutes: Token validity (default 5, max 10)
    
    Returns:
        - qr_token: JWT token for QR code
        - expires_at: Token expiry timestamp
        - static_barcode: Customer's permanent barcode
    """
    customer = get_current_client()
    
    if not customer:
        return error_response('Customer not found', 404)
    
    # Get active subscription
    subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        return error_response('No active subscription. Please purchase a subscription.', 403)
    
    # Validate subscription
    is_valid, reason, _, _ = QRService.validate_entry(customer.id, subscription.id)
    
    if not is_valid:
        return error_response(f'Cannot generate QR code: {reason}', 403)
    
    # Get expiry time
    expiry_minutes = min(int(request.args.get('expiry_minutes', 5)), 10)
    
    # Generate QR token
    qr_token = QRService.generate_qr_token(
        customer_id=customer.id,
        subscription_id=subscription.id,
        expiry_minutes=expiry_minutes
    )
    
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    
    return success_response({
        'qr_token': qr_token,
        'expires_at': expires_at.isoformat(),
        'expires_in': expiry_minutes * 60,  # seconds
        'static_barcode': customer.qr_code,
        'subscription': {
            'id': subscription.id,
            'service_name': subscription.service.name if subscription.service else None,
            'remaining_visits': subscription.remaining_visits,
            'remaining_classes': subscription.remaining_classes,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None
        }
    })


@client_bp.route('/refresh-qr', methods=['POST'])
@client_token_required
def refresh_client_qr():
    """
    Refresh QR code (alias for GET /qr)
    Returns the same as GET /qr since QR codes don't expire in this implementation
    """
    # Get current client
    customer_id = request.customer_id
    customer = db.session.get(Customer, customer_id)
    
    if not customer or not customer.is_active:
        return error_response('Customer not found or inactive', 404)
    
    # QR code is permanent (GYM-{id}), but we return it in the expected format
    return success_response({
        'qr_code': customer.qr_code,
        'qr_token': customer.qr_code,  # Static QR
        'expires_at': None,  # Never expires
        'message': 'QR code is permanent and does not need refreshing'
    })


@client_bp.route('/entry-history', methods=['GET'])
@client_token_required
def get_client_entry_history():
    """
    Get client entry history (alias for /history)
    """
    # Redirect to the actual history implementation
    return get_client_history()


@client_bp.route('/history', methods=['GET'])
@client_token_required
def get_client_history():
    """
    Get client's entry history (paginated)
    
    Query params:
        - page: Page number (default 1)
        - per_page: Items per page (default 20)
        - from_date: Start date filter (ISO format)
        - to_date: End date filter (ISO format)
    
    Returns:
        List of entry logs
    """
    customer = get_current_client()
    
    if not customer:
        return error_response('Customer not found', 404)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    query = EntryLog.query.filter_by(customer_id=customer.id)
    
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
    
    # Format entries with proper structure for Flutter client
    entries = []
    for entry in items:
        entry_dict = entry.to_dict()
        
        # Ensure all required fields are present
        entry_data = {
            'id': entry_dict.get('id'),
            'date': entry.entry_time.strftime('%Y-%m-%d') if entry.entry_time else '',
            'time': entry.entry_time.strftime('%H:%M:%S') if entry.entry_time else '',
            'datetime': entry.entry_time.isoformat() if entry.entry_time else '',
            'branch': entry.branch.name if entry.branch else 'Unknown',
            'branch_id': entry_dict.get('branch_id'),
            'service': entry.service.name if entry.service else 'Gym Access',
            'service_id': entry_dict.get('service_id'),
            'coins_used': entry_dict.get('coins_used', 1),
            'entry_type': entry_dict.get('entry_type', 'scan')
        }
        entries.append(entry_data)
    
    # Return array directly (Flutter expects data: [array])
    return success_response(entries)


@client_bp.route('/stats', methods=['GET'])
@client_token_required
def get_client_stats():
    """
    Get client statistics
    
    Returns:
        - total_visits: Total gym visits
        - visits_this_month: Visits in current month
        - current_streak: Current consecutive days
        - active_subscription: Active subscription details
    """
    customer = get_current_client()
    
    if not customer:
        return error_response('Customer not found', 404)
    
    # Total visits
    total_visits = EntryLog.query.filter_by(
        customer_id=customer.id,
        entry_status='approved'
    ).count()
    
    # Visits this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    visits_this_month = EntryLog.query.filter_by(
        customer_id=customer.id,
        entry_status='approved'
    ).filter(EntryLog.entry_time >= first_day_of_month).count()
    
    # Current streak (simplified - consecutive days)
    current_streak = _calculate_streak(customer.id)
    
    # Active subscription
    active_subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    return success_response({
        'total_visits': total_visits,
        'visits_this_month': visits_this_month,
        'current_streak': current_streak,
        'active_subscription': active_subscription.to_dict() if active_subscription else None
    })


def _calculate_streak(customer_id: int) -> int:
    """Calculate consecutive days streak"""
    # Get unique entry dates in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    entries = db.session.query(
        db.func.date(EntryLog.entry_time).label('entry_date')
    ).filter(
        EntryLog.customer_id == customer_id,
        EntryLog.entry_status == 'approved',
        EntryLog.entry_time >= thirty_days_ago
    ).distinct().order_by(db.desc('entry_date')).all()
    
    if not entries:
        return 0
    
    # Calculate streak
    streak = 0
    current_date = datetime.utcnow().date()
    
    for entry in entries:
        entry_date = entry[0]
        
        # Check if this is consecutive day
        if entry_date == current_date or entry_date == current_date - timedelta(days=streak):
            streak += 1
            current_date = entry_date - timedelta(days=1)
        else:
            break
    
    return streak
