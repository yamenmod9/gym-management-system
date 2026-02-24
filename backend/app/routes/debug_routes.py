"""
Additional test route - Debug data visibility
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Customer, Subscription, Transaction, Branch
from app.utils import get_current_user
from app.extensions import db

debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')


@debug_bp.route('/my-data-summary', methods=['GET'])
@jwt_required()
def my_data_summary():
    """
    Shows what data the current user should see
    This helps debug why Flutter app shows no data
    """
    user = get_current_user()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Build base query for each entity
    customer_query = Customer.query
    subscription_query = Subscription.query
    transaction_query = Transaction.query
    
    # Apply branch filtering if needed
    from app.models.user import UserRole
    if user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        if user.branch_id:
            customer_query = customer_query.filter_by(branch_id=user.branch_id)
            subscription_query = subscription_query.filter_by(branch_id=user.branch_id)
            transaction_query = transaction_query.filter_by(branch_id=user.branch_id)
    
    # Get counts
    customer_count = customer_query.count()
    subscription_count = subscription_query.count()
    transaction_count = transaction_query.count()
    
    # Get branch info
    branches = Branch.query.all()
    branch_info = []
    for branch in branches:
        branch_customers = Customer.query.filter_by(branch_id=branch.id).count()
        branch_info.append({
            'id': branch.id,
            'name': branch.name,
            'customers': branch_customers,
            'is_my_branch': branch.id == user.branch_id
        })
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role.value,
            'branch_id': user.branch_id,
            'branch_name': user.branch.name if user.branch else None
        },
        'data_access': {
            'can_see_all_branches': user.role.value in ['owner', 'central_accountant'],
            'restricted_to_branch': user.branch_id if user.role.value not in ['owner', 'central_accountant'] else None
        },
        'data_counts': {
            'customers': customer_count,
            'subscriptions': subscription_count,
            'transactions': transaction_count
        },
        'all_branches': branch_info,
        'total_system_data': {
            'total_customers': Customer.query.count(),
            'total_subscriptions': Subscription.query.count(),
            'total_transactions': Transaction.query.count(),
            'total_branches': len(branches)
        },
        'message': f"You should see {customer_count} customers, {subscription_count} subscriptions, and {transaction_count} transactions in the Flutter app."
    })
