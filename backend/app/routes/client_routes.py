"""
Client routes - Mobile app endpoints for clients
"""
from flask import Blueprint, request
from datetime import datetime, timedelta
from app.models import (
    Customer, Subscription, SubscriptionStatus, EntryLog, EntryType, EntryStatus, Transaction,
)
from app.services.qr_service import QRService
from app.services.gym_rules import gym_rule
from app.utils import success_response, error_response, paginate, format_pagination_response
from app.utils.client_auth import client_token_required, get_current_client
from app.extensions import db

client_bp = Blueprint('client', __name__, url_prefix='/api/client')

_DELETE_REQUEST_PREFIX = '[DELETE_REQUEST]'
_DELETE_GRACE_DAYS = 90


def _extract_delete_request_date(customer: Customer):
    notes = customer.health_notes or ''
    for line in notes.splitlines():
        if line.startswith(_DELETE_REQUEST_PREFIX):
            try:
                raw_date = line.split(':', 1)[1].strip()
                return datetime.fromisoformat(raw_date)
            except (IndexError, ValueError):
                return None
    return None


def _append_delete_request_note(customer: Customer, requested_at: datetime):
    notes = customer.health_notes or ''
    cleaned_lines = [
        line for line in notes.splitlines() if not line.startswith(_DELETE_REQUEST_PREFIX)
    ]
    cleaned_lines.append(f'{_DELETE_REQUEST_PREFIX}: {requested_at.isoformat()}')
    customer.health_notes = '\n'.join([line for line in cleaned_lines if line]).strip() or None


def _clear_delete_request_note(customer: Customer):
    notes = customer.health_notes or ''
    cleaned_lines = [
        line for line in notes.splitlines() if not line.startswith(_DELETE_REQUEST_PREFIX)
    ]
    customer.health_notes = '\n'.join([line for line in cleaned_lines if line]).strip() or None


def _build_delete_status(customer: Customer):
    requested_at = _extract_delete_request_date(customer)
    if not requested_at:
        return {
            'requested': False,
            'requested_at': None,
            'scheduled_delete_at': None,
            'days_remaining': None,
            'is_due': False,
        }

    scheduled_delete_at = requested_at + timedelta(days=_DELETE_GRACE_DAYS)
    now = datetime.utcnow()
    delta_days = (scheduled_delete_at - now).days
    days_remaining = max(delta_days, 0)

    return {
        'requested': True,
        'requested_at': requested_at.isoformat(),
        'scheduled_delete_at': scheduled_delete_at.isoformat(),
        'days_remaining': days_remaining,
        'is_due': now >= scheduled_delete_at,
    }


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

    deletion_status = _build_delete_status(customer)
    if deletion_status['is_due']:
        customer.is_active = False
        db.session.commit()
        return error_response('This account has been deleted after the 90-day grace period.', 403)
    
    # Get active subscription with proper validation
    from datetime import date
    active_subscription = Subscription.query.filter(
        Subscription.customer_id == customer.id,
        Subscription.status == SubscriptionStatus.ACTIVE,
        db.or_(
            Subscription.subscription_type.in_(['coins', 'sessions', 'training']),  # These don't expire by date
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

    # Include gym branding so client app can refresh colors on startup
    from app.models.gym import Gym
    gym = None
    if customer.branch and hasattr(customer.branch, 'gym_id') and customer.branch.gym_id:
        gym = Gym.query.get(customer.branch.gym_id)
    # No `Gym.query.first()` fallback — that served an arbitrary other
    # tenant's name, logo and colours to a customer whose branch has no gym.
    response_data['gym'] = gym.to_dict() if gym else None
    response_data['account_deletion'] = deletion_status

    return success_response(response_data)


@client_bp.route('/account/delete-request', methods=['POST'])
@client_token_required
def request_account_deletion():
    """
    Create or refresh an account deletion request.

    The account remains active during the 90-day grace period,
    then is soft-deleted automatically on next authenticated interaction.
    """
    customer = get_current_client()

    if not customer:
        return error_response('Customer not found', 404)

    requested_at = datetime.utcnow()
    _append_delete_request_note(customer, requested_at)
    db.session.commit()

    scheduled_delete_at = requested_at + timedelta(days=_DELETE_GRACE_DAYS)

    return success_response(
        {
            'requested': True,
            'requested_at': requested_at.isoformat(),
            'scheduled_delete_at': scheduled_delete_at.isoformat(),
            'grace_period_days': _DELETE_GRACE_DAYS,
        },
        'Account deletion requested. Your account is scheduled for deletion in 90 days.'
    )


@client_bp.route('/account/delete-request', methods=['DELETE'])
@client_token_required
def cancel_account_deletion():
    """Cancel a previously requested account deletion."""
    customer = get_current_client()

    if not customer:
        return error_response('Customer not found', 404)

    existing_request = _extract_delete_request_date(customer)
    if not existing_request:
        return error_response('No pending deletion request found.', 404)

    _clear_delete_request_note(customer)
    db.session.commit()

    return success_response(
        {
            'requested': False,
            'requested_at': None,
            'scheduled_delete_at': None,
        },
        'Account deletion request cancelled.'
    )


_SUPPORTED_LANGUAGES = {'ar', 'en'}


@client_bp.route('/language', methods=['PATCH'])
@client_token_required
def update_preferred_language():
    """Set the current client's preferred UI language ('ar' or 'en').

    Called from the first-login onboarding step and from in-app settings.
    """
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    language = (request.json or {}).get('preferred_language', '').strip().lower()
    if language not in _SUPPORTED_LANGUAGES:
        return error_response(f"preferred_language must be one of {sorted(_SUPPORTED_LANGUAGES)}", 400)

    customer.preferred_language = language
    db.session.commit()

    return success_response(customer.to_dict(), 'Language preference saved')


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
    
    # A member can hold several at once (gym entry, private training with a
    # captain, a combined package). The top-level fields stay the single
    # "headline" subscription so existing clients keep parsing this response
    # unchanged; `subscriptions` carries the full picture for the ones that
    # render a list.
    active = Subscription.active_for(customer.id)

    if not active:
        return error_response('No active subscription found', 404)

    # Headline = whatever opens the door, falling back to the newest.
    entry = Subscription.entry_subscription_for(customer.id)
    subscription = next(
        (s for s in active if entry is not None and s.id == entry.id),
        active[0],
    )

    def _with_service(sub):
        data = sub.to_dict()
        if sub.service:
            data['service'] = {
                'id': sub.service.id,
                'name': sub.service.name,
                'service_type': sub.service.service_type.value,
                'has_visits': sub.service.has_visits,
                'has_classes': sub.service.has_classes,
                'duration_days': sub.service.duration_days,
            }
        return data

    subscription_data = _with_service(subscription)
    subscription_data['subscriptions'] = [_with_service(s) for s in active]

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


@client_bp.route('/payments', methods=['GET'])
@client_token_required
def get_client_payments():
    """
    Get every subscription the client has taken, with what they paid for it.

    Amounts live on transactions, not subscriptions, so each subscription is
    returned with its own transactions and their sum. Transactions that are not
    tied to a subscription (ad-hoc payments) are grouped under 'other_payments'
    so the grand total still reconciles with what the member actually paid.

    Returns:
        subscriptions: list of subscriptions, each with payments[] + total_paid
        other_payments: payments not linked to any subscription
        total_paid: grand total across everything
        currency_amounts are net of discount
    """
    customer = get_current_client()

    if not customer:
        return error_response('Customer not found', 404)

    subscriptions = Subscription.query.filter_by(
        customer_id=customer.id
    ).order_by(Subscription.created_at.desc()).all()

    transactions = Transaction.query.filter_by(
        customer_id=customer.id
    ).order_by(Transaction.transaction_date.desc()).all()

    def _payment_dict(txn):
        return {
            'id': txn.id,
            'amount': float(txn.amount) - float(txn.discount or 0),
            'gross_amount': float(txn.amount),
            'discount': float(txn.discount or 0),
            'payment_method': txn.payment_method.value if txn.payment_method else None,
            'transaction_type': txn.transaction_type.value if txn.transaction_type else None,
            'branch_name': txn.branch.name if txn.branch else None,
            'description': txn.description,
            'reference_number': txn.reference_number,
            'date': txn.transaction_date.isoformat() if txn.transaction_date else None,
        }

    payments_by_subscription = {}
    other_payments = []
    for txn in transactions:
        payment = _payment_dict(txn)
        if txn.subscription_id:
            payments_by_subscription.setdefault(txn.subscription_id, []).append(payment)
        else:
            other_payments.append(payment)

    subscription_items = []
    for sub in subscriptions:
        payments = payments_by_subscription.get(sub.id, [])
        subscription_items.append({
            'id': sub.id,
            'service_name': sub.service.name if sub.service else None,
            'service_type': sub.service.service_type.value if sub.service else None,
            'subscription_type': sub.subscription_type,
            'branch_name': sub.branch.name if sub.branch else None,
            'status': sub.status.value,
            'start_date': sub.start_date.isoformat() if sub.start_date else None,
            'end_date': sub.end_date.isoformat() if sub.end_date else None,
            'created_at': sub.created_at.isoformat() if sub.created_at else None,
            'display_label': sub.display_label,
            'display_value': sub.display_value,
            'payments': payments,
            'payment_count': len(payments),
            'total_paid': sum(p['amount'] for p in payments),
        })

    subscriptions_total = sum(item['total_paid'] for item in subscription_items)
    other_total = sum(p['amount'] for p in other_payments)

    return success_response({
        'subscriptions': subscription_items,
        'other_payments': other_payments,
        'subscriptions_total': subscriptions_total,
        'other_total': other_total,
        'total_paid': subscriptions_total + other_total,
        'subscription_count': len(subscription_items),
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
    
    # This QR opens the door, so it has to be backed by the subscription that
    # grants entry — issuing one against a private-training package would let
    # the scan meter the wrong thing.
    subscription = Subscription.entry_subscription_for(
        customer.id,
        allow_non_entry=gym_rule(
            customer.branch.gym_id if customer.branch else None,
            'pt_only_members_may_enter',
        ),
    )

    if not subscription or subscription.status != SubscriptionStatus.ACTIVE:
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
    # `request.customer_id` was never a thing — nothing in the request
    # pipeline sets it, so reading it raised an AttributeError and this
    # endpoint answered 500 to every call. The member app's "refresh QR"
    # button has therefore never worked.
    customer = get_current_client()

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
        # Derive service name from subscription -> service relationship if available
        service_name = 'Gym Access'
        if entry.subscription and entry.subscription.service:
            service_name = entry.subscription.service.name

        entry_data = {
            'id': entry.id,
            'date': entry.entry_time.strftime('%Y-%m-%d') if entry.entry_time else '',
            'time': entry.entry_time.strftime('%H:%M:%S') if entry.entry_time else '',
            'datetime': entry.entry_time.isoformat() if entry.entry_time else '',
            'branch': entry.branch.name if entry.branch else 'Unknown',
            'branch_id': entry.branch_id,
            'service': service_name,
            'coins_used': entry.coins_deducted or 0,
            'entry_type': entry.entry_type.value if entry.entry_type else 'QR_SCAN',
            'entry_status': entry.entry_status.value if entry.entry_status else 'APPROVED'
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
        entry_status=EntryStatus.APPROVED
    ).count()
    
    # Visits this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    visits_this_month = EntryLog.query.filter_by(
        customer_id=customer.id,
        entry_status=EntryStatus.APPROVED
    ).filter(EntryLog.entry_time >= first_day_of_month).count()
    
    # Current streak (simplified - consecutive days)
    current_streak = _calculate_streak(customer.id)
    
    # Headline subscription stays a single object for existing clients;
    # `active_subscriptions` carries the rest for members holding several.
    active = Subscription.active_for(customer.id)
    entry = Subscription.entry_subscription_for(customer.id)
    headline = next(
        (s for s in active if entry is not None and s.id == entry.id),
        active[0] if active else None,
    )

    return success_response({
        'total_visits': total_visits,
        'visits_this_month': visits_this_month,
        'current_streak': current_streak,
        'active_subscription': headline.to_dict() if headline else None,
        'active_subscriptions': [s.to_dict() for s in active],
    })


# How many check-ins in the trailing hour separate one crowding level from the
# next. Tuned for a branch where ~20 entries/hour is a peak; raise these for
# higher-traffic sites.
_BUSY_MODERATE_FROM = 5
_BUSY_BUSY_FROM = 15


def _busy_level(count):
    if count >= _BUSY_BUSY_FROM:
        return 'busy'
    if count >= _BUSY_MODERATE_FROM:
        return 'moderate'
    return 'quiet'


@client_bp.route('/class-feedback/pending', methods=['GET'])
@client_token_required
def pending_class_feedback():
    """Classes this member attended that they haven't rated yet."""
    from app.models import ClassAttendance, ClassSession, ClassFeedback, ClassSessionStatus

    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    rated = {
        row.session_id for row in
        ClassFeedback.query.filter_by(customer_id=customer.id).all()
    }

    rows = (
        db.session.query(ClassSession, ClassAttendance)
        .join(ClassAttendance, ClassAttendance.session_id == ClassSession.id)
        .filter(
            ClassAttendance.customer_id == customer.id,
            ClassSession.status == ClassSessionStatus.CLOSED,
        )
        .order_by(ClassSession.ended_at.desc())
        .limit(20)
        .all()
    )

    return success_response([
        {
            'session_id': session.id,
            'class_id': session.class_id,
            'class_name': session.gym_class.name if session.gym_class else None,
            'trainer_name': session.trainer.full_name if session.trainer else None,
            'session_date': session.session_date.isoformat(),
            'ended_at': session.ended_at.isoformat() if session.ended_at else None,
        }
        for session, _ in rows if session.id not in rated
    ])


@client_bp.route('/class-feedback', methods=['POST'])
@client_token_required
def submit_class_feedback():
    """Rate a class this member actually attended."""
    from app.models import ClassAttendance, ClassSession, ClassFeedback, ClassSessionStatus

    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    data = request.json or {}
    session_id = data.get('session_id')
    try:
        rating = int(data.get('rating'))
    except (TypeError, ValueError):
        return error_response('rating must be a whole number from 1 to 5', 400)
    if not 1 <= rating <= 5:
        return error_response('rating must be between 1 and 5', 400)

    session = db.session.get(ClassSession, session_id) if session_id else None
    if not session:
        return error_response('Session not found', 404)

    # Only people who were actually marked present may rate it.
    attended = ClassAttendance.query.filter_by(
        session_id=session.id, customer_id=customer.id
    ).first()
    if not attended:
        return error_response('You did not attend that class', 403)

    if session.status != ClassSessionStatus.CLOSED:
        return error_response('That class has not finished yet', 400)

    existing = ClassFeedback.query.filter_by(
        session_id=session.id, customer_id=customer.id
    ).first()
    if existing:
        return error_response('You have already rated that class', 409)

    comment = (data.get('comment') or '').strip() or None
    feedback = ClassFeedback(
        session_id=session.id,
        customer_id=customer.id,
        rating=rating,
        comment=comment,
    )
    db.session.add(feedback)
    db.session.commit()

    return success_response(feedback.to_dict(include_member=False), 'Thanks for the feedback', 201)


@client_bp.route('/branch-activity', methods=['GET'])
@client_token_required
def get_branch_activity():
    """How busy the member's own branch is right now.

    Counts approved check-ins in the trailing hour at the branch this customer
    belongs to — never a branch they aren't a member of, and never a
    gym-wide total, so this can't be used to infer another site's traffic.
    Denied scans are excluded: someone turned away at the door never entered.
    """
    customer = get_current_client()

    if not customer:
        return error_response('Customer not found', 404)

    since = datetime.utcnow() - timedelta(hours=1)
    count = EntryLog.query.filter(
        EntryLog.branch_id == customer.branch_id,
        EntryLog.entry_status == EntryStatus.APPROVED,
        EntryLog.entry_time >= since,
    ).count()

    return success_response({
        'branch_id': customer.branch_id,
        'branch_name': customer.branch.name if customer.branch else None,
        'entries_last_hour': count,
        'level': _busy_level(count),
        'as_of': datetime.utcnow().isoformat(),
    })


def _calculate_streak(customer_id: int) -> int:
    """Calculate consecutive days streak"""
    # Get unique entry dates in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    entries = db.session.query(
        db.func.date(EntryLog.entry_time).label('entry_date')
    ).filter(
        EntryLog.customer_id == customer_id,
        EntryLog.entry_status == EntryStatus.APPROVED,
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
