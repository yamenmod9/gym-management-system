"""
Branch management routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.schemas import BranchSchema
from app.models.branch import Branch
from app.utils import (
    success_response, error_response, role_required,
    paginate, format_pagination_response
)
from app.models.user import UserRole
from app.extensions import db

branches_bp = Blueprint('branches', __name__, url_prefix='/api/branches')


@branches_bp.route('', methods=['GET'])
@jwt_required()
def get_branches():
    """Get all branches"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_active = request.args.get('is_active', type=bool)
    
    query = Branch.query
    
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    query = query.order_by(Branch.name)
    
    items, total, pages, current_page = paginate(query, page, per_page)
    
    schema = BranchSchema()
    return success_response(
        format_pagination_response(items, total, pages, current_page, schema)
    )


@branches_bp.route('/<int:branch_id>', methods=['GET'])
@jwt_required()
def get_branch(branch_id):
    """Get branch by ID"""
    branch = db.session.get(Branch, branch_id)
    
    if not branch:
        return error_response("Branch not found", 404)
    
    return success_response(branch.to_dict())


@branches_bp.route('', methods=['POST'])
@jwt_required()
@role_required(UserRole.OWNER)
def create_branch():
    """Create new branch"""
    try:
        schema = BranchSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    # Check if code already exists
    if Branch.query.filter_by(code=data['code']).first():
        return error_response("Branch code already exists", 400)
    
    # Check if name already exists
    if Branch.query.filter_by(name=data['name']).first():
        return error_response("Branch name already exists", 400)
    
    branch = Branch(**data)
    db.session.add(branch)
    db.session.commit()
    
    return success_response(branch.to_dict(), "Branch created successfully", 201)


@branches_bp.route('/<int:branch_id>', methods=['PUT'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER)
def update_branch(branch_id):
    """Update branch"""
    branch = db.session.get(Branch, branch_id)
    
    if not branch:
        return error_response("Branch not found", 404)
    
    try:
        schema = BranchSchema(partial=True)
        data = schema.load(request.json)
    except ValidationError as e:
        return error_response("Validation error", 400, e.messages)
    
    # Update fields
    for field in ['name', 'address', 'phone', 'city', 'is_active']:
        if field in data:
            setattr(branch, field, data[field])
    
    db.session.commit()
    
    return success_response(branch.to_dict(), "Branch updated successfully")


@branches_bp.route('/<int:branch_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRole.OWNER)
def delete_branch(branch_id):
    """Deactivate branch (soft delete)"""
    branch = db.session.get(Branch, branch_id)
    
    if not branch:
        return error_response("Branch not found", 404)
    
    branch.is_active = False
    db.session.commit()
    
    return success_response(message="Branch deactivated successfully")
