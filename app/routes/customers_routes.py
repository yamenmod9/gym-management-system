"""
Customer management routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.schemas import CustomerSchema
from app.models.customer import Customer
from app.utils import (
    success_response, error_response, role_required,
    paginate, format_pagination_response, get_current_user
)
from app.models.user import UserRole
from app.extensions import db

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    """Get all customers (paginated)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    branch_id = request.args.get('branch_id', type=int)
    search = request.args.get('search', type=str)
    
    user = get_current_user()
    
    query = Customer.query
    
    # Branch filtering based on role
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id:
            query = query.filter_by(branch_id=user.branch_id)
    elif branch_id:
        query = query.filter_by(branch_id=branch_id)
    
    # Search
    if search:
        query = query.filter(
            db.or_(
                Customer.full_name.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(Customer.created_at.desc())
    
    items, total, pages, current_page = paginate(query, page, per_page)
    
    schema = CustomerSchema()
    return success_response(
        format_pagination_response(items, total, pages, current_page, schema)
    )


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Get customer by ID"""
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return error_response("Customer not found", 404)
    
    # Check branch access
    user = get_current_user()
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id and customer.branch_id != user.branch_id:
            return error_response("Access denied", 403)
    
    return success_response(customer.to_dict())


@customers_bp.route('/phone/<string:phone>', methods=['GET'])
@jwt_required()
def get_customer_by_phone(phone):
    """Get customer by phone number"""
    customer = Customer.query.filter_by(phone=phone).first()
    
    if not customer:
        return error_response("Customer not found", 404)
    
    # Check branch access
    user = get_current_user()
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id and customer.branch_id != user.branch_id:
            return error_response("Access denied", 403)
    
    return success_response(customer.to_dict())


@customers_bp.route('', methods=['POST'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def create_customer():
    """Create new customer"""
    try:
        schema = CustomerSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    # Check if phone already exists
    if Customer.query.filter_by(phone=data['phone']).first():
        return error_response("Phone number already registered", 400)
    
    # Validate branch access
    user = get_current_user()
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id and data['branch_id'] != user.branch_id:
            return error_response("Cannot create customer for another branch", 403)
    
    customer = Customer(**data)
    
    # Calculate health metrics
    if customer.height and customer.weight:
        customer.calculate_health_metrics()
    
    db.session.add(customer)
    db.session.commit()
    
    return success_response(customer.to_dict(), "Customer created successfully", 201)


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK)
def update_customer(customer_id):
    """Update customer"""
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return error_response("Customer not found", 404)
    
    # Check branch access
    user = get_current_user()
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id and customer.branch_id != user.branch_id:
            return error_response("Access denied", 403)
    
    try:
        schema = CustomerSchema(partial=True)
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    # Update fields
    for field in ['full_name', 'email', 'national_id', 'date_of_birth', 'gender',
                  'address', 'height', 'weight', 'health_notes', 'is_active']:
        if field in data:
            setattr(customer, field, data[field])
    
    # Recalculate health metrics if height or weight changed
    if 'height' in data or 'weight' in data:
        customer.calculate_health_metrics()
    
    db.session.commit()
    
    return success_response(customer.to_dict(), "Customer updated successfully")


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER)
def delete_customer(customer_id):
    """Deactivate customer (soft delete)"""
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return error_response("Customer not found", 404)
    
    # Check branch access
    user = get_current_user()
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id and customer.branch_id != user.branch_id:
            return error_response("Access denied", 403)
    
    customer.is_active = False
    db.session.commit()
    
    return success_response(message="Customer deactivated successfully")
