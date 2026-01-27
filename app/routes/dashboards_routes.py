"""
Dashboard and reporting routes
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime, date, timedelta
from app.services import DashboardService
from app.utils import (
    success_response, error_response, role_required, get_current_user,
    calculate_branch_revenue, get_expiring_subscriptions
)
from app.models.user import UserRole

dashboards_bp = Blueprint('dashboards', __name__, url_prefix='/api/dashboards')


@dashboards_bp.route('/owner', methods=['GET'])
@jwt_required()
@role_required(UserRole.OWNER)
def get_owner_dashboard():
    """Get owner dashboard with smart alerts and analytics"""
    data = DashboardService.get_owner_dashboard()
    return success_response(data)


@dashboards_bp.route('/accountant', methods=['GET'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT, UserRole.ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT)
def get_accountant_dashboard():
    """Get accountant dashboard"""
    user = get_current_user()
    
    # Branch accountants can only see their branch
    branch_id = None
    if user.role in [UserRole.ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT]:
        branch_id = user.branch_id
    else:
        branch_id = request.args.get('branch_id', type=int)
    
    data = DashboardService.get_accountant_dashboard(branch_id)
    return success_response(data)


@dashboards_bp.route('/branch-manager', methods=['GET'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER)
def get_branch_manager_dashboard():
    """Get branch manager dashboard"""
    user = get_current_user()
    
    # Branch managers can only see their branch
    if user.role == UserRole.BRANCH_MANAGER:
        branch_id = user.branch_id
        if not branch_id:
            return error_response("User not assigned to a branch", 403)
    else:
        branch_id = request.args.get('branch_id', type=int)
        if not branch_id:
            return error_response("branch_id is required", 400)
    
    data = DashboardService.get_branch_manager_dashboard(branch_id)
    return success_response(data)


@dashboards_bp.route('/reports/revenue', methods=['GET'])
@jwt_required()
@role_required(UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT, UserRole.ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT)
def get_revenue_report():
    """Get revenue report"""
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    branch_id = request.args.get('branch_id', type=int)
    group_by = request.args.get('group_by', 'day', type=str)
    
    if not start_date or not end_date:
        return error_response("start_date and end_date are required", 400)
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return error_response("Invalid date format. Use YYYY-MM-DD", 400)
    
    user = get_current_user()
    
    # Branch-specific roles can only see their branch
    if user.role in [UserRole.ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT]:
        branch_id = user.branch_id
    
    data = DashboardService.get_revenue_report(start_date, end_date, branch_id, group_by)
    return success_response(data)


@dashboards_bp.route('/alerts/expiring-subscriptions', methods=['GET'])
@jwt_required()
def get_expiring_subscriptions_alert():
    """Get expiring subscriptions alert"""
    days = request.args.get('days', 7, type=int)
    branch_id = request.args.get('branch_id', type=int)
    
    user = get_current_user()
    
    # Branch-specific roles can only see their branch
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        branch_id = user.branch_id
    
    subscriptions = get_expiring_subscriptions(days, branch_id)
    
    from app.schemas import SubscriptionSchema
    schema = SubscriptionSchema()
    
    return success_response({
        'count': len(subscriptions),
        'subscriptions': schema.dump(subscriptions, many=True)
    })
