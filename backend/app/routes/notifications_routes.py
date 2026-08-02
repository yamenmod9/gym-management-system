"""
Push notification routes — register/unregister device tokens and send notifications
"""
from flask import Blueprint, request
from flask_jwt_extended import decode_token, jwt_required
from app.extensions import db
from app.models.device_token import DeviceToken
from app.models.user import User, UserRole
from app.utils import success_response, error_response, role_required

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


def _identity_from_request():
    """Resolve (user_id, customer_id) from the Authorization header.

    Returns (None, None) when the header is absent or the token is not valid;
    ``decode_token`` verifies both the signature and the expiry.
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, None

    try:
        decoded = decode_token(auth_header.split(' ', 1)[1])
    except Exception:
        return None, None

    if decoded.get('scope') == 'client':
        cid = decoded.get('customer_id')
        return None, (int(cid) if cid else None)

    identity = decoded.get('sub')
    if not identity:
        return None, None
    user = db.session.get(User, int(identity))
    return (user.id if user else None), None


@notifications_bp.route('/register-device', methods=['POST'])
def register_device():
    """
    Register an FCM device token.
    Works for both staff (JWT) and client (client JWT) tokens.

    Body:
      {
        "fcm_token": "...",
        "app_type": "staff" | "client" | "super_admin",
        "platform": "android" | "ios"   (optional, default android)
      }
    """
    data = request.get_json()
    if not data or not data.get('fcm_token') or not data.get('app_type'):
        return error_response('fcm_token and app_type are required', 400)

    fcm_token = data['fcm_token']
    app_type = data['app_type']
    platform = data.get('platform', 'android')

    user_id, customer_id = _identity_from_request()

    if user_id is None and customer_id is None:
        return error_response('Unable to identify user from token', 401)

    # Deactivate any existing token with the same fcm_token (token reuse across accounts)
    DeviceToken.query.filter_by(fcm_token=fcm_token).update({'is_active': False})

    # Check for an existing active entry for this user/customer + app_type
    existing = DeviceToken.query.filter_by(
        user_id=user_id,
        customer_id=customer_id,
        app_type=app_type,
        is_active=True,
    ).first()

    if existing:
        existing.fcm_token = fcm_token
        existing.platform = platform
    else:
        new_token = DeviceToken(
            user_id=user_id,
            customer_id=customer_id,
            fcm_token=fcm_token,
            app_type=app_type,
            platform=platform,
            is_active=True,
        )
        db.session.add(new_token)

    db.session.commit()

    return success_response({'registered': True}, 'Device registered for notifications')


@notifications_bp.route('/unregister-device', methods=['POST'])
def unregister_device():
    """
    Unregister an FCM device token (on logout).
    Body: { "fcm_token": "..." }
    """
    data = request.get_json()
    if not data or not data.get('fcm_token'):
        return error_response('fcm_token is required', 400)

    # Scoped to the caller's own registrations. Unauthenticated, this let
    # anyone who learned a device token silence that device's notifications.
    # The client unregisters during logout, while its token is still valid.
    user_id, customer_id = _identity_from_request()
    if user_id is None and customer_id is None:
        return error_response('Unable to identify user from token', 401)

    count = DeviceToken.query.filter_by(
        fcm_token=data['fcm_token'],
        user_id=user_id,
        customer_id=customer_id,
    ).update({'is_active': False})
    db.session.commit()

    return success_response({'unregistered': count}, 'Device unregistered')


@notifications_bp.route('/debug-tokens', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN)
def debug_tokens():
    """
    Debug endpoint: list all registered device tokens.

    Super admin only. This dumps raw FCM tokens across every gym, so any
    authenticated staffer having it — which was the case — handed one tenant
    the push identifiers of every other tenant's staff and members.
    """
    tokens = DeviceToken.query.order_by(DeviceToken.id.desc()).limit(50).all()
    return success_response({
        'total': DeviceToken.query.count(),
        'active': DeviceToken.query.filter_by(is_active=True).count(),
        'client_active': DeviceToken.query.filter_by(app_type='client', is_active=True).count(),
        'staff_active': DeviceToken.query.filter_by(app_type='staff', is_active=True).count(),
        'tokens': [t.to_dict() for t in tokens],
    })
