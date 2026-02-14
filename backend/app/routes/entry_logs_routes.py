"""
Entry logs routes - Customer check-in/scanning
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.models import Customer, Subscription, EntryLog, Branch
from app.models.subscription import SubscriptionStatus
from app.models.entry_log import EntryType
from app.utils import success_response, error_response, role_required
from app.models.user import UserRole
from app.extensions import db

entry_logs_bp = Blueprint('entry_logs', __name__, url_prefix='/api/entry-logs')


@entry_logs_bp.route('/scan', methods=['POST'])
@jwt_required()
@role_required(UserRole.FRONT_DESK, UserRole.BRANCH_MANAGER, UserRole.OWNER)
def scan_qr_code():
    """
    Record customer check-in via QR scan
    
    Request Body:
    {
        "qr_code": "GYM-000001",
        "branch_id": 1
    }
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    qr_code = data.get('qr_code')
    branch_id = data.get('branch_id')
    
    if not qr_code:
        return error_response("qr_code is required", 400)
    
    if not branch_id:
        return error_response("branch_id is required", 400)
    
    # Verify branch exists
    branch = db.session.get(Branch, branch_id)
    if not branch:
        return error_response("Branch not found", 404)
    
    # Find customer by QR code
    customer = Customer.query.filter_by(qr_code=qr_code).first()
    
    if not customer:
        return error_response("Customer not found", 404)
    
    # Find active subscription
    subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    # Check if no active subscription
    if not subscription:
        # Check for expired subscription
        expired_sub = Subscription.query.filter_by(
            customer_id=customer.id,
            status=SubscriptionStatus.EXPIRED
        ).order_by(Subscription.end_date.desc()).first()
        
        return error_response(
            "No active subscription found",
            403,
            {
                "code": "NO_SUBSCRIPTION",
                "customer_name": customer.full_name,
                "customer_id": customer.id,
                "has_expired_subscription": expired_sub is not None,
                "last_subscription_end_date": expired_sub.end_date.isoformat() if expired_sub else None
            }
        )
    
    # Check if subscription is frozen
    if subscription.status == SubscriptionStatus.FROZEN:
        # Get freeze history to find reason
        freeze_reason = "Subscription is currently frozen"
        frozen_date = subscription.updated_at
        
        from app.models.freeze_history import FreezeHistory
        latest_freeze = FreezeHistory.query.filter_by(
            subscription_id=subscription.id
        ).order_by(FreezeHistory.freeze_start.desc()).first()
        
        if latest_freeze:
            freeze_reason = latest_freeze.reason or "Subscription is frozen"
            frozen_date = latest_freeze.freeze_start
        
        return error_response(
            "Subscription is frozen",
            403,
            {
                "code": "FROZEN",
                "customer_name": customer.full_name,
                "customer_id": customer.id,
                "frozen_date": frozen_date.isoformat() if frozen_date else None,
                "freeze_reason": freeze_reason
            }
        )
    
    # Check remaining coins/visits
    if subscription.remaining_visits is not None and subscription.remaining_visits <= 0:
        return error_response(
            "No coins remaining",
            403,
            {
                "code": "NO_COINS",
                "customer_name": customer.full_name,
                "customer_id": customer.id,
                "remaining_coins": 0,
                "subscription_type": subscription.service.name
            }
        )
    
    # All checks passed - record entry and deduct coin
    entry_log = EntryLog(
        customer_id=customer.id,
        subscription_id=subscription.id,
        branch_id=branch_id,
        entry_time=datetime.utcnow(),
        entry_type=EntryType.QR_CODE,
        coins_deducted=1
    )
    
    # Deduct coin/visit
    if subscription.remaining_visits is not None:
        subscription.remaining_visits -= 1
    
    db.session.add(entry_log)
    db.session.commit()
    
    return success_response({
        "message": "Check-in successful",
        "entry_log_id": entry_log.id,
        "customer_name": customer.full_name,
        "customer_id": customer.id,
        "entry_time": entry_log.entry_time.isoformat(),
        "coins_used": 1,
        "remaining_coins": subscription.remaining_visits if subscription.remaining_visits is not None else None,
        "subscription_end_date": subscription.end_date.isoformat()
    })
