"""
Subscription management routes
"""
import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.schemas import (
    SubscriptionSchema, FreezeSubscriptionSchema, StopSubscriptionSchema
)
from app.models.subscription import Subscription, SubscriptionStatus
from app.services import SubscriptionService
from sqlalchemy.orm import joinedload
from app.utils import (
    success_response, error_response, role_required,
    paginate, format_pagination_response, get_current_user,
    get_accessible_branch_ids, scope_query_to_branches
)
from app.models.user import UserRole
from app.extensions import db

logger = logging.getLogger(__name__)

subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/api/subscriptions')


def _load_scoped_subscription(subscription_id):
    """Fetch a subscription the caller is actually allowed to act on.

    Returns (subscription, None) or (None, error_response). Every mutating
    endpoint below routed straight into SubscriptionService with nothing but
    an id, so a front-desk staffer could renew, freeze, unfreeze or stop any
    subscription in any gym by guessing one.
    """
    subscription = db.session.get(Subscription, subscription_id)
    if not subscription:
        return None, error_response("Subscription not found", 404)

    accessible = get_accessible_branch_ids(get_current_user())
    if accessible is not None and subscription.branch_id not in accessible:
        # 404 rather than 403 so the response does not confirm the id exists.
        return None, error_response("Subscription not found", 404)

    return subscription, None


@subscriptions_bp.route('', methods=['GET'])
@jwt_required()
def get_subscriptions():
    """Get all subscriptions (paginated)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    branch_id = request.args.get('branch_id', type=int)
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status', type=str)
    
    user = get_current_user()
    
    # Eager-load what the schema names, so serialising a page of 20 does not
    # fire three extra queries per row.
    query = Subscription.query.options(
        joinedload(Subscription.customer),
        joinedload(Subscription.service),
        joinedload(Subscription.branch),
    )

    # Branch scope. The hand-rolled filter this replaces applied nothing at all
    # to an owner unless they passed ?branch_id, so listing subscriptions
    # returned every gym's members; any role with a NULL branch_id fell through
    # the same gap.
    query = scope_query_to_branches(query, Subscription.branch_id, user, branch_id)

    # Customer filter
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    # Status filter
    if status:
        try:
            query = query.filter_by(status=SubscriptionStatus(status))
        except ValueError:
            return error_response("Invalid status", 400)
    
    query = query.order_by(Subscription.created_at.desc())
    
    items, total, pages, current_page = paginate(query, page, per_page)
    
    schema = SubscriptionSchema()
    return success_response(
        format_pagination_response(items, total, pages, current_page, schema)
    )


@subscriptions_bp.route('/<int:subscription_id>', methods=['GET'])
@jwt_required()
def get_subscription(subscription_id):
    """Get subscription by ID"""
    # Same scope as every mutating endpoint here. The check this replaces
    # exempted owners entirely, so one could read any subscription in the
    # database — including another gym's — by guessing an id.
    subscription, error = _load_scoped_subscription(subscription_id)
    if error:
        return error

    return success_response(subscription.to_dict())


@subscriptions_bp.route('', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def create_subscription():
    """Create new subscription"""
    try:
        schema = SubscriptionSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    # Validate branch access
    user = get_current_user()
    # Same scope as /activate. The check this replaces exempted owners, so one
    # could sell a subscription into another gym's branch, and skipped any role
    # whose branch_id is NULL.
    accessible = get_accessible_branch_ids(user)
    if accessible is not None and data['branch_id'] not in accessible:
        return error_response("Cannot create subscription for another branch", 403)

    subscription, error = SubscriptionService.create_subscription(data, user.id)
    
    if error:
        return error_response(error, 400)
    
    # Notify the customer about the new subscription
    try:
        from app.services.fcm_service import notify_customer
        notify_customer(
            subscription.customer_id,
            '✅ تم تفعيل الاشتراك',
            f'مرحباً! تم تفعيل اشتراكك بنجاح.',
            {'type': 'subscription_created', 'subscription_id': str(subscription.id)},
        )
    except Exception as e:
        logger.exception('Push notification failed: %s', e)

    return success_response(subscription.to_dict(), "Subscription created successfully", 201)


@subscriptions_bp.route('/activate', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def activate_subscription():
    """Activate new subscription (alias for create)"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['customer_id', 'service_id', 'branch_id']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Validate branch access.
        #
        # This used to compare against user.branch_id directly, which let two
        # cases through: an owner (exempted outright) could target another
        # gym's branch, and a regional manager — who has no branch_id of their
        # own — skipped the check entirely.
        user = get_current_user()
        accessible = get_accessible_branch_ids(user)
        if accessible is not None and data['branch_id'] not in accessible:
            return error_response("Cannot create subscription for another branch", 403)
        
        # Prepare data for service — forward ALL subscription-type fields
        subscription_data = {
            'customer_id': data['customer_id'],
            'service_id': data['service_id'],
            'branch_id': data['branch_id'],
            # The amount reception actually collected. Without this the
            # transaction was booked at the service's list price, so the
            # ledger disagreed with the cash drawer on every subscription
            # sold at a negotiated or multi-month price.
            'amount': data.get('amount'),
            'payment_method': data.get('payment_method', 'cash'),
            'reference_number': data.get('reference_number'),
            'start_date': data.get('start_date'),
            # The captain a private-training package is sold against. This dict
            # is built field by field, and trainer_id was simply not on the
            # list — so reception could pick a captain, the request carried the
            # id, and it was dropped here. Every private package sold through
            # the desk ended up with no trainer, which is what the captain's
            # client roster is built from, so the member never appeared on it.
            # SubscriptionService validates the id (active trainer, same gym).
            'trainer_id': data.get('trainer_id'),
            # ── type overrides from client ────────────────────────────
            'subscription_type': data.get('subscription_type'),       # 'coins', 'time_based', 'sessions', 'training'
            # coins fields
            'coins':             data.get('coins'),
            'coin_amount':       data.get('coin_amount'),
            'remaining_coins':   data.get('remaining_coins'),
            # session / training fields
            'session_count':     data.get('session_count') or data.get('sessions'),
            # time_based: duration in months from the form
            'duration_months':   data.get('duration_months'),
        }

        # If duration_months provided, override the service's default end_date
        if subscription_data.get('duration_months'):
            try:
                months = int(subscription_data['duration_months'])
                subscription_data['duration_days_override'] = months * 30
            except (ValueError, TypeError):
                pass

        subscription, error = SubscriptionService.create_subscription(subscription_data, user.id)
        
        if error:
            return error_response(error, 400)
        
        # Format response to match Flutter app expectations
        response_data = subscription.to_dict()
        response_data['subscription_id'] = subscription.id

        # Notify the customer
        try:
            from app.services.fcm_service import notify_customer
            notify_customer(
                subscription.customer_id,
                '✅ تم تفعيل الاشتراك',
                f'مرحباً! تم تفعيل اشتراكك بنجاح.',
                {'type': 'subscription_activated', 'subscription_id': str(subscription.id)},
            )
        except Exception as e:
            logger.exception('Push notification failed: %s', e)

        return success_response(
            response_data,
            "Subscription activated successfully",
            201
        )
    
    except Exception as e:
        # Reason stays server-side; the caller gets a stable message.
        logger.exception('Failed to activate subscription: %s', e)
        return error_response("Failed to activate subscription", 500)


@subscriptions_bp.route('/<int:subscription_id>/renew', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def renew_subscription(subscription_id):
    """Renew subscription"""
    data = request.json or {}

    _, denied = _load_scoped_subscription(subscription_id)
    if denied:
        return denied

    user = get_current_user()

    subscription, error = SubscriptionService.renew_subscription(
        subscription_id, data, user.id
    )
    
    if error:
        return error_response(error, 400)
    
    # Notify customer
    try:
        from app.services.fcm_service import notify_customer
        notify_customer(
            subscription.customer_id,
            '🔄 تم تجديد الاشتراك',
            f'تم تجديد اشتراكك حتى {subscription.end_date.strftime("%Y-%m-%d")}.',
            {'type': 'subscription_renewed', 'subscription_id': str(subscription.id)},
        )
    except Exception as e:
        logger.exception('Push notification failed: %s', e)

    return success_response(subscription.to_dict(), "Subscription renewed successfully")


@subscriptions_bp.route('/<int:subscription_id>/freeze', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def freeze_subscription(subscription_id):
    """Freeze subscription"""
    try:
        schema = FreezeSubscriptionSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)

    _, denied = _load_scoped_subscription(subscription_id)
    if denied:
        return denied

    user = get_current_user()

    subscription, error = SubscriptionService.freeze_subscription(
        subscription_id,
        data['days'],
        data.get('reason'),
        user.id
    )
    
    if error:
        return error_response(error, 400)
    
    # Notify customer
    try:
        from app.services.fcm_service import notify_customer
        notify_customer(
            subscription.customer_id,
            '❄️ تم تجميد الاشتراك',
            f'تم تجميد اشتراكك لمدة {data["days"]} يوم.',
            {'type': 'subscription_frozen', 'subscription_id': str(subscription.id)},
        )
    except Exception as e:
        logger.exception('Push notification failed: %s', e)

    return success_response(subscription.to_dict(), "Subscription frozen successfully")


@subscriptions_bp.route('/<int:subscription_id>/unfreeze', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def unfreeze_subscription(subscription_id):
    """Unfreeze subscription"""
    _, denied = _load_scoped_subscription(subscription_id)
    if denied:
        return denied

    subscription, error = SubscriptionService.unfreeze_subscription(subscription_id)
    
    if error:
        return error_response(error, 400)
    
    # Notify customer
    try:
        from app.services.fcm_service import notify_customer
        notify_customer(
            subscription.customer_id,
            '☀️ تم إلغاء تجميد الاشتراك',
            'اشتراكك أصبح فعالاً مجدداً. مرحباً بعودتك!',
            {'type': 'subscription_unfrozen', 'subscription_id': str(subscription.id)},
        )
    except Exception as e:
        logger.exception('Push notification failed: %s', e)

    return success_response(subscription.to_dict(), "Subscription unfrozen successfully")


@subscriptions_bp.route('/<int:subscription_id>/stop', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def stop_subscription(subscription_id):
    """Stop subscription"""
    try:
        schema = StopSubscriptionSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)

    _, denied = _load_scoped_subscription(subscription_id)
    if denied:
        return denied

    subscription, error = SubscriptionService.stop_subscription(
        subscription_id,
        data['reason']
    )
    
    if error:
        return error_response(error, 400)
    
    # Notify customer
    try:
        from app.services.fcm_service import notify_customer
        notify_customer(
            subscription.customer_id,
            '⛔ تم إيقاف الاشتراك',
            'تم إيقاف اشتراكك. تواصل مع الإدارة للمزيد.',
            {'type': 'subscription_stopped', 'subscription_id': str(subscription.id)},
        )
    except Exception as e:
        logger.exception('Push notification failed: %s', e)

    return success_response(subscription.to_dict(), "Subscription stopped successfully")


# Alternative endpoints for Flutter app - accept subscription_id in body instead of URL
@subscriptions_bp.route('/renew', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def renew_subscription_body():
    """Renew subscription (body-based)"""
    data = request.get_json()
    
    if not data or 'subscription_id' not in data:
        return error_response('subscription_id is required', 400)
    
    _, denied = _load_scoped_subscription(data['subscription_id'])
    if denied:
        return denied

    user = get_current_user()
    # renew_subscription takes (subscription_id, data, created_by_user_id).
    # This used to pass only the id, so every renewal raised a TypeError and
    # came back as a 500 — the reception app's Renew button never worked.
    subscription, error = SubscriptionService.renew_subscription(
        data['subscription_id'], data, user.id
    )

    if error:
        return error_response(error, 400)

    return success_response(subscription.to_dict(), "Subscription renewed successfully")


@subscriptions_bp.route('/freeze', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER)
def freeze_subscription_body():
    """Freeze subscription (body-based)"""
    data = request.get_json()
    
    if not data or 'subscription_id' not in data:
        return error_response('subscription_id is required', 400)
    
    subscription_id = data['subscription_id']
    freeze_days = data.get('freeze_days')
    reason = data.get('reason')
    
    if not freeze_days:
        return error_response('freeze_days is required', 400)

    _, denied = _load_scoped_subscription(subscription_id)
    if denied:
        return denied

    user = get_current_user()
    # created_by_user_id is required — omitting it raised a TypeError, so
    # every freeze came back as a 500.
    subscription, error = SubscriptionService.freeze_subscription(
        subscription_id,
        freeze_days,
        reason,
        user.id,
    )

    if error:
        return error_response(error, 400)

    return success_response(subscription.to_dict(), "Subscription frozen successfully")


@subscriptions_bp.route('/stop', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def stop_subscription_body():
    """Stop subscription (body-based)"""
    data = request.get_json()
    
    if not data or 'subscription_id' not in data:
        return error_response('subscription_id is required', 400)
    
    subscription_id = data['subscription_id']
    reason = data.get('reason', 'Customer request')

    _, denied = _load_scoped_subscription(subscription_id)
    if denied:
        return denied

    subscription, error = SubscriptionService.stop_subscription(
        subscription_id,
        reason
    )
    
    if error:
        return error_response(error, 400)
    
    return success_response(subscription.to_dict(), "Subscription stopped successfully")


@subscriptions_bp.route('/repair-types', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER)
def repair_subscription_types():
    """
    One-time repair endpoint: back-fills subscription_type, remaining_coins,
    total_coins, remaining_sessions, total_sessions for all subscriptions
    that have subscription_type = NULL (legacy records created before the fix).
    Safe to call multiple times.
    """
    fixed = 0
    skipped = 0

    subs = Subscription.query.filter(Subscription.subscription_type == None).all()

    for sub in subs:
        if not sub.service:
            skipped += 1
            continue

        sub_type = SubscriptionService._derive_subscription_type(sub.service)
        sub.subscription_type = sub_type

        if sub_type == 'coins' and sub.remaining_coins is None:
            coin_amount = sub.service.class_limit or 50
            sub.remaining_coins = coin_amount
            sub.total_coins = coin_amount

        elif sub_type in ('sessions', 'training') and sub.remaining_sessions is None:
            session_count = sub.service.class_limit or 10
            sub.remaining_sessions = session_count
            sub.total_sessions = session_count

        fixed += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error_response(f"DB error during repair: {str(e)}", 500)

    return success_response(
        {'fixed': fixed, 'skipped': skipped},
        f"Repaired {fixed} subscription(s), skipped {skipped}"
    )
