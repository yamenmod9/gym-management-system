"""
QR Code Service - Generate and validate time-limited QR codes
"""
from datetime import datetime, timedelta
import jwt
import hashlib
from flask import current_app
from app.models import Subscription, SubscriptionStatus, Customer


class QRService:
    """Service for QR code generation and validation"""
    
    @staticmethod
    def generate_qr_token(customer_id: int, subscription_id: int = None, 
                         expiry_minutes: int = 5) -> str:
        """
        Generate time-limited QR token
        
        Args:
            customer_id: Customer ID
            subscription_id: Active subscription ID
            expiry_minutes: Token validity in minutes (default 5)
        
        Returns:
            str: JWT token for QR code
        """
        payload = {
            'customer_id': customer_id,
            'subscription_id': subscription_id,
            'token_type': 'qr_access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=expiry_minutes)
        }
        
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def validate_qr_token(token: str) -> dict:
        """
        Validate QR token
        
        Args:
            token: JWT token from QR code
        
        Returns:
            dict: Decoded payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Verify token type
            if payload.get('token_type') != 'qr_access':
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def validate_entry(customer_id: int, subscription_id: int = None, 
                      branch_id: int = None) -> tuple:
        """
        Validate if customer can enter gym
        
        Args:
            customer_id: Customer ID
            subscription_id: Subscription ID
            branch_id: Branch ID where entry is attempted
        
        Returns:
            tuple: (is_valid: bool, reason: str, subscription: Subscription, coins_to_deduct: int)
        """
        from app.models import Customer, Subscription
        from app.extensions import db
        
        # Get customer
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return False, "Customer not found", None, 0
        
        if not customer.is_active:
            return False, "Customer account is inactive", None, 0
        
        # If no subscription_id provided, find active subscription
        if subscription_id:
            subscription = db.session.get(Subscription, subscription_id)
        else:
            subscription = Subscription.query.filter_by(
                customer_id=customer_id,
                status=SubscriptionStatus.ACTIVE
            ).first()
        
        if not subscription:
            return False, "No active subscription found", None, 0
        
        # Check subscription status (includes frozen, stopped, expired)
        if subscription.status != SubscriptionStatus.ACTIVE:
            return False, f"Subscription is {subscription.status.value}", subscription, 0
        
        # Check if subscription is expired by date
        if subscription.end_date and subscription.end_date < datetime.utcnow().date():
            return False, "Subscription expired", subscription, 0
        
        # Check branch access (if branch_id provided)
        if branch_id and subscription.branch_id != branch_id:
            return False, "Subscription not valid for this branch", subscription, 0
        
        # Check remaining visits/coins
        coins_to_deduct = 0
        if subscription.service.has_visits:
            if subscription.remaining_visits <= 0:
                return False, "No remaining visits on subscription", subscription, 0
            coins_to_deduct = 1
        
        # Check class-based limits
        if subscription.service.has_classes:
            if subscription.remaining_classes <= 0:
                return False, "No remaining classes on subscription", subscription, 0
            coins_to_deduct = 1
        
        # All checks passed
        return True, "Entry approved", subscription, coins_to_deduct
    
    @staticmethod
    def deduct_entry(subscription: Subscription, coins: int = 1):
        """
        Deduct entry from subscription
        
        Args:
            subscription: Subscription object
            coins: Number of visits/classes to deduct
        """
        if subscription.service.has_visits:
            subscription.remaining_visits = max(0, subscription.remaining_visits - coins)
            
            # Auto-expire if no visits left
            if subscription.remaining_visits == 0:
                subscription.status = SubscriptionStatus.EXPIRED
        
        if subscription.service.has_classes:
            subscription.remaining_classes = max(0, subscription.remaining_classes - coins)
            
            # Auto-expire if no classes left
            if subscription.remaining_classes == 0:
                subscription.status = SubscriptionStatus.EXPIRED
    
    @staticmethod
    def generate_barcode(customer_id: int) -> str:
        """
        Generate static barcode for customer
        
        Args:
            customer_id: Customer ID
        
        Returns:
            str: Barcode string (customer's QR code)
        """
        customer = Customer.query.get(customer_id)
        if customer and customer.qr_code:
            return customer.qr_code
        return f"GYM-{customer_id}"
    
    @staticmethod
    def validate_barcode(barcode: str) -> tuple:
        """
        Validate barcode and get customer
        
        Args:
            barcode: Barcode string (e.g., GYM-123)
        
        Returns:
            tuple: (customer: Customer or None, error: str or None)
        """
        customer = Customer.query.filter_by(qr_code=barcode).first()
        
        if not customer:
            return None, "Invalid barcode"
        
        if not customer.is_active:
            return None, "Customer account is inactive"
        
        return customer, None
