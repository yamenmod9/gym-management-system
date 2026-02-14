"""
Alerts routes - System alerts and notifications
Maps /api/alerts/* for Flutter app compatibility
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models import Subscription, Customer, Complaint
from app.models.subscription import SubscriptionStatus
from app.utils import success_response, error_response, get_current_user, role_required
from app.models.user import UserRole
from datetime import datetime, timedelta
from app.extensions import db

alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


@alerts_bp.route('', methods=['GET'])
@jwt_required()
def get_alerts():
    """
    Get all alerts for the current user
    
    Query params:
        - branch_id: Filter by branch
        - alert_type: expiring, low_coins, complaints
        - is_read: Filter by read status (not implemented yet)
    """
    branch_id = request.args.get('branch_id', type=int)
    alert_type = request.args.get('alert_type')
    
    current_user = get_current_user()
    
    # Determine branch access
    if current_user.role not in [UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
        branch_id = current_user.branch_id
    
    alerts = []
    
    # Expiring subscriptions alert
    if not alert_type or alert_type == 'expiring':
        # Get subscriptions expiring in the next 7 days
        today = datetime.utcnow().date()
        week_from_now = today + timedelta(days=7)
        
        expiring_query = Subscription.query.filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.end_date <= week_from_now,
            Subscription.end_date >= today
        )
        
        if branch_id:
            expiring_query = expiring_query.filter_by(branch_id=branch_id)
        
        expiring_subs = expiring_query.all()
        
        for sub in expiring_subs:
            days_remaining = (sub.end_date - today).days
            priority = 'high' if days_remaining <= 1 else 'medium' if days_remaining <= 3 else 'low'
            
            alerts.append({
                'id': f'exp_{sub.id}',
                'alert_type': 'expiring_subscription',
                'priority': priority,
                'customer_id': sub.customer_id,
                'customer_name': sub.customer.full_name if sub.customer else 'N/A',
                'branch_id': sub.branch_id,
                'message': f'Subscription expires in {days_remaining} day(s)',
                'is_read': False,
                'created_at': today.isoformat()
            })
    
    # Low coins alert
    if not alert_type or alert_type == 'low_coins':
        low_coins_query = Subscription.query.filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.remaining_coins <= 3,
            Subscription.remaining_coins > 0
        )
        
        if branch_id:
            low_coins_query = low_coins_query.filter_by(branch_id=branch_id)
        
        low_coins_subs = low_coins_query.all()
        
        for sub in low_coins_subs:
            priority = 'high' if sub.remaining_coins == 1 else 'medium'
            
            alerts.append({
                'id': f'coin_{sub.id}',
                'alert_type': 'low_coins',
                'priority': priority,
                'customer_id': sub.customer_id,
                'customer_name': sub.customer.full_name if sub.customer else 'N/A',
                'branch_id': sub.branch_id,
                'message': f'Only {sub.remaining_coins} coin(s) remaining',
                'is_read': False,
                'created_at': datetime.utcnow().date().isoformat()
            })
    
    # Open complaints alert
    if not alert_type or alert_type == 'complaints':
        complaints_query = Complaint.query.filter_by(status='open')
        
        if branch_id:
            complaints_query = complaints_query.filter_by(branch_id=branch_id)
        
        open_complaints = complaints_query.all()
        
        for complaint in open_complaints:
            alerts.append({
                'id': f'comp_{complaint.id}',
                'alert_type': 'open_complaint',
                'priority': complaint.priority,
                'customer_id': complaint.customer_id,
                'customer_name': complaint.customer.full_name if complaint.customer else 'N/A',
                'branch_id': complaint.branch_id,
                'message': f'{complaint.category}: {complaint.description[:50]}...',
                'is_read': False,
                'created_at': complaint.created_at.isoformat()
            })
    
    # Count unread (all are unread in this simple implementation)
    unread_count = len(alerts)
    
    return success_response({
        'data': alerts,
        'unread_count': unread_count
    })


@alerts_bp.route('/smart', methods=['GET'])
@jwt_required()
@role_required([UserRole.OWNER])
def get_smart_alerts():
    """
    Get smart alerts for owner dashboard
    Returns counts of various alert types
    """
    # Expiring subscriptions
    today = datetime.utcnow().date()
    
    expiring_today = Subscription.query.filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.end_date == today
    ).count()
    
    week_from_now = today + timedelta(days=7)
    expiring_week = Subscription.query.filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.end_date <= week_from_now,
        Subscription.end_date > today
    ).count()
    
    # Low coins
    low_coins = Subscription.query.filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.remaining_coins <= 3,
        Subscription.remaining_coins > 0
    ).count()
    
    # Open complaints
    open_complaints = Complaint.query.filter_by(status='open').count()
    
    # Pending expenses
    from app.models import Expense
    pending_expenses = Expense.query.filter_by(approval_status='pending').count()
    urgent_expenses = Expense.query.filter_by(
        approval_status='pending',
        priority='urgent'
    ).count()
    
    return success_response({
        'expiring_today': expiring_today,
        'expiring_week': expiring_week,
        'low_coins': low_coins,
        'open_complaints': open_complaints,
        'pending_expenses': pending_expenses,
        'urgent_expenses': urgent_expenses
    })
