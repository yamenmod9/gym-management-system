"""
Subscription service - handles subscription logic
"""
from datetime import datetime, timedelta, date
from app.extensions import db
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.customer import Customer
from app.models.service import Service
from app.models.transaction import Transaction, PaymentMethod, TransactionType
from app.models.freeze_history import FreezeHistory
from app.models.fingerprint import Fingerprint


class SubscriptionService:
    """Subscription management service"""
    
    @staticmethod
    def create_subscription(data, created_by_user_id):
        """Create a new subscription"""
        # Validate customer
        customer = db.session.get(Customer, data['customer_id'])
        if not customer:
            return None, "Customer not found"
        
        # Validate service
        service = db.session.get(Service, data['service_id'])
        if not service or not service.is_active:
            return None, "Service not found or inactive"
        
        # Calculate dates
        start_date = data.get('start_date', date.today())
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        end_date = start_date + timedelta(days=service.duration_days)
        
        # Initialize visit/class tracking based on service type
        remaining_visits = None
        remaining_classes = None
        
        if service.class_limit:
            # Class-based service (education programs)
            remaining_classes = service.class_limit
        else:
            # Visit-based service (gym, swimming recreation, karate)
            # Set default to 30 visits per subscription (can be customized)
            remaining_visits = 30
        
        # Create subscription
        subscription = Subscription(
            customer_id=customer.id,
            service_id=service.id,
            branch_id=data['branch_id'],
            start_date=start_date,
            end_date=end_date,
            status=SubscriptionStatus.ACTIVE,
            remaining_visits=remaining_visits,
            remaining_classes=remaining_classes
        )
        
        db.session.add(subscription)
        db.session.flush()  # Get subscription ID
        
        # Create transaction
        transaction = Transaction(
            amount=service.price,
            payment_method=PaymentMethod(data.get('payment_method', 'cash')),
            transaction_type=TransactionType.SUBSCRIPTION,
            branch_id=data['branch_id'],
            customer_id=customer.id,
            subscription_id=subscription.id,
            created_by=created_by_user_id,
            description=f"New subscription: {service.name}",
            reference_number=data.get('reference_number')
        )
        
        db.session.add(transaction)
        
        # Activate fingerprint if exists
        fingerprints = Fingerprint.query.filter_by(
            customer_id=customer.id
        ).all()
        
        for fp in fingerprints:
            if not fp.is_active:
                fp.is_active = True
                fp.deactivation_reason = None
        
        db.session.commit()
        
        return subscription, None
    
    @staticmethod
    def renew_subscription(subscription_id, data, created_by_user_id):
        """Renew an existing subscription"""
        subscription = db.session.get(Subscription, subscription_id)
        if not subscription:
            return None, "Subscription not found"
        
        service = subscription.service
        
        # Calculate new dates
        # If subscription is still active, extend from current end date
        # Otherwise, start from today
        if subscription.status == SubscriptionStatus.ACTIVE and subscription.end_date >= date.today():
            start_date = subscription.end_date + timedelta(days=1)
        else:
            start_date = date.today()
        
        end_date = start_date + timedelta(days=service.duration_days)
        
        # Reinitialize visit/class tracking based on service type
        if service.class_limit:
            remaining_classes = service.class_limit
            remaining_visits = None
        else:
            remaining_visits = 30  # Default visits for renewed subscription
            remaining_classes = None
        
        # Update subscription
        subscription.start_date = start_date
        subscription.end_date = end_date
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.freeze_count = 0
        subscription.total_frozen_days = 0
        subscription.classes_attended = 0
        subscription.remaining_visits = remaining_visits
        subscription.remaining_classes = remaining_classes
        subscription.stop_reason = None
        subscription.stopped_at = None
        
        # Create renewal transaction
        transaction = Transaction(
            amount=service.price,
            payment_method=PaymentMethod(data.get('payment_method', 'cash')),
            transaction_type=TransactionType.RENEWAL,
            branch_id=subscription.branch_id,
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            created_by=created_by_user_id,
            description=f"Renewal: {service.name}",
            reference_number=data.get('reference_number')
        )
        
        db.session.add(transaction)
        
        # Reactivate fingerprints
        fingerprints = Fingerprint.query.filter_by(
            customer_id=subscription.customer_id
        ).all()
        
        for fp in fingerprints:
            fp.is_active = True
            fp.deactivation_reason = None
        
        db.session.commit()
        
        return subscription, None
    
    @staticmethod
    def freeze_subscription(subscription_id, days, reason, created_by_user_id):
        """Freeze a subscription"""
        subscription = db.session.get(Subscription, subscription_id)
        if not subscription:
            return None, "Subscription not found"
        
        success, message = subscription.freeze(days, reason)
        if not success:
            return None, message
        
        # Create freeze history
        freeze_start = date.today()
        freeze_end = freeze_start + timedelta(days=days)
        
        freeze_history = FreezeHistory(
            subscription_id=subscription.id,
            freeze_start=freeze_start,
            freeze_end=freeze_end,
            freeze_days=days,
            reason=reason,
            cost=subscription.service.freeze_cost,
            is_active=True
        )
        
        db.session.add(freeze_history)
        
        # Create transaction if freeze is paid
        if subscription.service.freeze_is_paid and subscription.service.freeze_cost > 0:
            transaction = Transaction(
                amount=subscription.service.freeze_cost,
                payment_method=PaymentMethod.CASH,
                transaction_type=TransactionType.FREEZE,
                branch_id=subscription.branch_id,
                customer_id=subscription.customer_id,
                subscription_id=subscription.id,
                created_by=created_by_user_id,
                description=f"Freeze fee: {days} days"
            )
            db.session.add(transaction)
        
        # Deactivate fingerprints
        fingerprints = Fingerprint.query.filter_by(
            customer_id=subscription.customer_id,
            is_active=True
        ).all()
        
        for fp in fingerprints:
            fp.deactivate("Subscription frozen")
        
        db.session.commit()
        
        return subscription, None
    
    @staticmethod
    def unfreeze_subscription(subscription_id):
        """Unfreeze a subscription"""
        subscription = db.session.get(Subscription, subscription_id)
        if not subscription:
            return None, "Subscription not found"
        
        success, message = subscription.unfreeze()
        if not success:
            return None, message
        
        # Mark current freeze as inactive
        active_freeze = FreezeHistory.query.filter_by(
            subscription_id=subscription.id,
            is_active=True
        ).first()
        
        if active_freeze:
            active_freeze.is_active = False
            active_freeze.unfrozen_at = datetime.utcnow()
        
        # Reactivate fingerprints
        fingerprints = Fingerprint.query.filter_by(
            customer_id=subscription.customer_id
        ).all()
        
        for fp in fingerprints:
            fp.is_active = True
            fp.deactivation_reason = None
        
        db.session.commit()
        
        return subscription, None
    
    @staticmethod
    def stop_subscription(subscription_id, reason):
        """Stop a subscription"""
        subscription = db.session.get(Subscription, subscription_id)
        if not subscription:
            return None, "Subscription not found"
        
        success, message = subscription.stop(reason)
        if not success:
            return None, message
        
        # Deactivate fingerprints
        fingerprints = Fingerprint.query.filter_by(
            customer_id=subscription.customer_id,
            is_active=True
        ).all()
        
        for fp in fingerprints:
            # Check if customer has other active subscriptions
            other_active = Subscription.query.filter(
                Subscription.customer_id == subscription.customer_id,
                Subscription.id != subscription.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).first()
            
            if not other_active:
                fp.deactivate("Subscription stopped")
        
        db.session.commit()
        
        return subscription, None
