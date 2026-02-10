"""
Client authentication routes - Code-based authentication for mobile app
"""
from flask import Blueprint, request
from app.models import Customer, ActivationCode, ActivationCodeType
from app.services.notification_service import get_notification_service
from app.utils import success_response, error_response
from app.utils.client_auth import create_client_token
from app.extensions import db

client_auth_bp = Blueprint('client_auth', __name__, url_prefix='/api/client/auth')


@client_auth_bp.route('/login', methods=['POST'])
def client_login():
    """
    Client login with phone and password
    
    Request body:
        - phone: Customer phone number
        - password: Password (temporary or changed)
    
    Returns:
        - access_token: JWT token for client
        - customer: Customer profile data
        - password_changed: Whether client has changed password
    """
    data = request.get_json()
    
    if not data or 'phone' not in data or 'password' not in data:
        return error_response('Phone and password are required', 400)
    
    phone = data['phone'].strip()
    password = data['password'].strip()
    
    # Find customer by phone
    customer = Customer.query.filter_by(phone=phone, is_active=True).first()
    
    if not customer:
        return error_response('Invalid phone or password', 401)
    
    # Verify password
    if not customer.check_password(password):
        return error_response('Invalid phone or password', 401)
    
    # Generate client JWT
    access_token = create_client_token(customer.id)
    
    # Get active subscription
    from app.models.subscription import Subscription, SubscriptionStatus
    active_subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    return success_response({
        'access_token': access_token,
        'token_type': 'Bearer',
        'password_changed': customer.password_changed,
        'customer': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,
            'branch_id': customer.branch_id,
            'branch_name': customer.branch.name if customer.branch else None,
            'has_active_subscription': active_subscription is not None
        }
    }, 'Login successful')


@client_auth_bp.route('/request-code', methods=['POST'])
def request_activation_code():
    """
    Request activation code for client login
    
    Request body:
        - identifier: phone or email
        - delivery_method: 'sms' or 'email' (optional, auto-detected)
    
    Returns:
        - message: Success message
        - delivery_target: Masked phone/email
        - expires_in: Code expiry time in seconds
    """
    data = request.get_json()
    
    if not data or 'identifier' not in data:
        return error_response('Identifier (phone or email) is required', 400)
    
    identifier = data['identifier'].strip()
    
    # Determine if identifier is phone or email
    if '@' in identifier:
        delivery_method = 'email'
        customer = Customer.query.filter_by(email=identifier, is_active=True).first()
        delivery_target = identifier
    else:
        delivery_method = 'sms'
        customer = Customer.query.filter_by(phone=identifier, is_active=True).first()
        delivery_target = identifier
    
    if not customer:
        # Security: Don't reveal if customer exists
        return success_response({
            'message': 'If this account exists, you will receive an activation code',
            'delivery_target': _mask_identifier(identifier, delivery_method),
            'expires_in': 900
        })
    
    # Allow override of delivery method
    if 'delivery_method' in data:
        requested_method = data['delivery_method']
        if requested_method == 'email' and customer.email:
            delivery_method = 'email'
            delivery_target = customer.email
        elif requested_method == 'sms' and customer.phone:
            delivery_method = 'sms'
            delivery_target = customer.phone
    
    # Invalidate old codes for this customer
    old_codes = ActivationCode.query.filter_by(
        customer_id=customer.id,
        is_used=False
    ).all()
    for old_code in old_codes:
        old_code.is_used = True
    
    # Create new activation code
    activation_code, plain_code = ActivationCode.create_code(
        customer_id=customer.id,
        delivery_method=delivery_method,
        delivery_target=delivery_target,
        code_type=ActivationCodeType.LOGIN,
        expiry_minutes=15
    )
    
    db.session.commit()
    
    # Send code via notification service
    notification_service = get_notification_service()
    try:
        print(f"\n{'='*70}", flush=True)
        print(f"🔐 ACTIVATION CODE REQUESTED", flush=True)
        print(f"{'='*70}", flush=True)
        print(f"📱 Phone: {delivery_target}", flush=True)
        print(f"🔢 CODE: {plain_code}", flush=True)
        print(f"👤 Customer: {customer.full_name}", flush=True)
        print(f"{'='*70}\n", flush=True)
        
        notification_service.send_activation_code(
            delivery_method=delivery_method,
            target=delivery_target,
            code=plain_code,
            customer_name=customer.full_name
        )
    except Exception as e:
        print(f"[ERROR] Failed to send code: {str(e)}", flush=True)
        db.session.rollback()
        return error_response(f'Failed to send activation code: {str(e)}', 500)
    
    # For development/testing, include the code in response
    # TODO: Remove this in production!
    response_data = {
        'message': f'Activation code sent via {delivery_method}',
        'delivery_target': _mask_identifier(delivery_target, delivery_method),
        'expires_in': 900  # 15 minutes in seconds
    }
    
    # Add code to response in development mode only
    from flask import current_app
    if current_app.debug:
        response_data['code'] = plain_code  # DEV ONLY - Remove in production!
        response_data['note'] = 'Code included in response for testing only'
    
    return success_response(response_data)


@client_auth_bp.route('/verify-code', methods=['POST'])
def verify_activation_code():
    """
    Verify activation code and issue client JWT
    
    Request body:
        - identifier: phone or email
        - code: 6-digit activation code
    
    Returns:
        - access_token: JWT token for client
        - customer: Customer profile data
    """
    data = request.get_json()
    
    if not data or 'identifier' not in data or 'code' not in data:
        return error_response('Identifier and code are required', 400)
    
    identifier = data['identifier'].strip()
    code = data['code'].strip()
    
    # Find customer
    if '@' in identifier:
        customer = Customer.query.filter_by(email=identifier, is_active=True).first()
    else:
        customer = Customer.query.filter_by(phone=identifier, is_active=True).first()
    
    if not customer:
        return error_response('Invalid credentials', 401)
    
    # Find valid activation code
    activation_code = ActivationCode.query.filter_by(
        customer_id=customer.id,
        is_used=False
    ).order_by(ActivationCode.created_at.desc()).first()
    
    if not activation_code:
        return error_response('No valid activation code found', 401)
    
    # Verify code
    if not activation_code.verify_code(code):
        db.session.commit()  # Save attempt count
        
        if activation_code.attempts >= activation_code.max_attempts:
            return error_response('Maximum attempts exceeded. Request a new code.', 401)
        
        return error_response('Invalid activation code', 401)
    
    db.session.commit()
    
    # Generate client JWT
    access_token = create_client_token(customer.id)
    
    # Update customer last_login equivalent (could add field)
    # For now, just return success
    
    return success_response({
        'access_token': access_token,
        'token_type': 'Bearer',
        'customer': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,
            'branch_id': customer.branch_id,
            'branch_name': customer.branch.name if customer.branch else None
        }
    }, 'Login successful')


def _mask_identifier(identifier: str, method: str) -> str:
    """
    Mask phone or email for security
    
    Args:
        identifier: Phone or email
        method: 'sms' or 'email'
    
    Returns:
        str: Masked identifier
    """
    if method == 'email':
        parts = identifier.split('@')
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            if len(username) > 2:
                masked = username[0] + '*' * (len(username) - 2) + username[-1]
            else:
                masked = username[0] + '*'
            return f"{masked}@{domain}"
        return identifier
    else:
        # Phone number
        if len(identifier) > 4:
            return identifier[:2] + '*' * (len(identifier) - 4) + identifier[-2:]
        return identifier
