"""
Subscription management routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.schemas import (
    SubscriptionSchema, FreezeSubscriptionSchema, StopSubscriptionSchema
)
from app.models.subscription import Subscription, SubscriptionStatus
from app.services import SubscriptionService
from app.utils import (
    success_response, error_response, role_required,
    paginate, format_pagination_response, get_current_user
)
from app.models.user import UserRole
from app.extensions import db

subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/api/subscriptions')


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
    
    query = Subscription.query
    
    # Branch filtering based on role
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id:
            query = query.filter_by(branch_id=user.branch_id)
    elif branch_id:
        query = query.filter_by(branch_id=branch_id)
    
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
    subscription = db.session.get(Subscription, subscription_id)
    
    if not subscription:
        return error_response("Subscription not found", 404)
    
    # Check branch access
    user = get_current_user()
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id and subscription.branch_id != user.branch_id:
            return error_response("Access denied", 403)
    
    return success_response(subscription.to_dict())


@subscriptions_bp.route('', methods=['POST'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def create_subscription():
    """Create new subscription"""
    try:
        schema = SubscriptionSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    # Validate branch access
    user = get_current_user()
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id and data['branch_id'] != user.branch_id:
            return error_response("Cannot create subscription for another branch", 403)
    
    subscription, error = SubscriptionService.create_subscription(data, user.id)
    
    if error:
        return error_response(error, 400)
    
    return success_response(subscription.to_dict(), "Subscription created successfully", 201)


@subscriptions_bp.route('/<int:subscription_id>/renew', methods=['POST'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def renew_subscription(subscription_id):
    """Renew subscription"""
    data = request.json or {}
    
    user = get_current_user()
    
    subscription, error = SubscriptionService.renew_subscription(
        subscription_id, data, user.id
    )
    
    if error:
        return error_response(error, 400)
    
    return success_response(subscription.to_dict(), "Subscription renewed successfully")


@subscriptions_bp.route('/<int:subscription_id>/freeze', methods=['POST'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def freeze_subscription(subscription_id):
    """Freeze subscription"""
    try:
        schema = FreezeSubscriptionSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    user = get_current_user()
    
    subscription, error = SubscriptionService.freeze_subscription(
        subscription_id,
        data['days'],
        data.get('reason'),
        user.id
    )
    
    if error:
        return error_response(error, 400)
    
    return success_response(subscription.to_dict(), "Subscription frozen successfully")


@subscriptions_bp.route('/<int:subscription_id>/unfreeze', methods=['POST'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def unfreeze_subscription(subscription_id):
    """Unfreeze subscription"""
    subscription, error = SubscriptionService.unfreeze_subscription(subscription_id)
    
    if error:
        return error_response(error, 400)
    
    return success_response(subscription.to_dict(), "Subscription unfrozen successfully")


@subscriptions_bp.route('/<int:subscription_id>/stop', methods=['POST'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def stop_subscription(subscription_id):
    """Stop subscription"""
    try:
        schema = StopSubscriptionSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    subscription, error = SubscriptionService.stop_subscription(
        subscription_id,
        data['reason']
    )
    
    if error:
        return error_response(error, 400)
    
    return success_response(subscription.to_dict(), "Subscription stopped successfully")
