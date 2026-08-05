"""
Service management routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.schemas import ServiceSchema
from app.models.service import Service, ServiceType
from app.utils import (
    success_response, error_response, role_required,
    paginate, format_pagination_response, get_current_user, get_current_gym_id
)
from app.models.user import UserRole
from app.extensions import db

services_bp = Blueprint('services', __name__, url_prefix='/api/services')


def _scope_to_gym(query, user=None):
    """Narrow a Service query to what this caller may see.

    A service carries the price, the freeze allowance and — since the
    multi-subscription work — ``grants_gym_entry``, which decides whether
    holding it opens a door. It had no owner at all, so every gym on the
    platform saw, sold and could edit every other gym's packages.

    NULL gym_id means shared: the pre-existing catalogue, which several gyms'
    subscriptions already point at. Those stay visible to everyone rather than
    being reassigned to one gym and disappearing from the others.
    """
    if user is None:
        user = get_current_user()

    gym_id = get_current_gym_id(user)
    if gym_id is None:          # super admin
        return query
    return query.filter(
        db.or_(Service.gym_id == gym_id, Service.gym_id.is_(None))
    )


def _load_scoped_service(service_id, for_write=False):
    """A service the caller may read, or (for_write) also modify."""
    service = db.session.get(Service, service_id)
    if not service:
        return None, error_response("Service not found", 404)

    user = get_current_user()
    gym_id = get_current_gym_id(user)

    if gym_id is not None and service.gym_id is not None and service.gym_id != gym_id:
        return None, error_response("Service not found", 404)

    # Editing a shared package would change its price and entry rights for
    # every other gym using it, so only the super admin may.
    if (for_write and service.gym_id is None
            and user.role != UserRole.SUPER_ADMIN):
        return None, error_response(
            "This is a shared package and cannot be edited from a single gym. "
            "Create your own copy instead.", 403)

    return service, None


@services_bp.route('', methods=['GET'])
@jwt_required()
def get_services():
    """Get all services"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    service_type = request.args.get('type', type=str)
    is_active = request.args.get('is_active', True, type=bool)

    query = _scope_to_gym(Service.query.filter_by(is_active=is_active))

    if service_type:
        try:
            query = query.filter_by(service_type=ServiceType(service_type))
        except ValueError:
            return error_response("Invalid service type", 400)

    query = query.order_by(Service.name)

    items, total, pages, current_page = paginate(query, page, per_page)

    schema = ServiceSchema()
    return success_response(
        format_pagination_response(items, total, pages, current_page, schema)
    )


@services_bp.route('/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service(service_id):
    """Get service by ID"""
    service, denied = _load_scoped_service(service_id)
    if denied:
        return denied

    return success_response(service.to_dict())


@services_bp.route('', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER)
def create_service():
    """Create new service"""
    try:
        schema = ServiceSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)

    # Stamped from the caller, never taken from the request: a gym must not be
    # able to file a package into someone else's catalogue.
    data.pop('gym_id', None)
    service = Service(**data)
    service.gym_id = get_current_gym_id(get_current_user())

    db.session.add(service)
    db.session.commit()

    return success_response(service.to_dict(), "Service created successfully", 201)


@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER)
def update_service(service_id):
    """Update service"""
    service, denied = _load_scoped_service(service_id, for_write=True)
    if denied:
        return denied

    try:
        schema = ServiceSchema(partial=True)
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)

    # Update fields
    for field in ['name', 'description', 'price', 'duration_days', 'allowed_days_per_week',
                  'class_limit', 'freeze_count_limit', 'freeze_max_days', 'freeze_is_paid',
                  'freeze_cost', 'is_active']:
        if field in data:
            setattr(service, field, data[field])

    db.session.commit()

    return success_response(service.to_dict(), "Service updated successfully")


@services_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER)
def delete_service(service_id):
    """Deactivate service (soft delete)"""
    service, denied = _load_scoped_service(service_id, for_write=True)
    if denied:
        return denied

    service.is_active = False
    db.session.commit()

    return success_response(message="Service deactivated successfully")
