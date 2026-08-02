"""
Fingerprint model - Simulated fingerprint access control
"""
from datetime import datetime
from app.extensions import db
import hashlib


class Fingerprint(db.Model):
    """Fingerprint model - simulated biometric access"""
    __tablename__ = 'fingerprints'

    id = db.Column(db.Integer, primary_key=True)
    
    # Customer reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer', back_populates='fingerprints')
    
    # Fingerprint hash (simulated unique identifier)
    fingerprint_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # Deterministic template hash for duplicate detection across customers
    # This is a hash of just the biometric data (without timestamp/customer_id)
    template_hash = db.Column(db.String(255), nullable=True, index=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_used = db.Column(db.DateTime, nullable=True)
    
    # Deactivation info
    deactivated_at = db.Column(db.DateTime, nullable=True)
    deactivation_reason = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Fingerprint {self.id} - Customer {self.customer_id}>'

    @staticmethod
    def generate_fingerprint_hash(customer_id, unique_data):
        """Generate a simulated fingerprint hash"""
        # In real system, this would be actual biometric data
        # For simulation, we use customer_id + unique_data
        data = f"{customer_id}:{unique_data}:{datetime.utcnow().timestamp()}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def generate_template_hash(unique_data):
        """Generate a deterministic hash of the biometric template data only.

        Used to detect whether the same fingerprint is already registered
        to a different customer.
        """
        return hashlib.sha256(unique_data.encode()).hexdigest()

    def validate_access(self):
        """Check if fingerprint can grant access"""
        if not self.is_active:
            return False, "Fingerprint is deactivated"

        # Only subscriptions that grant gym entry count here. A member whose
        # only active package is private training has bought a captain's time,
        # not floor access, so their finger must not open the door.
        from app.models.subscription import Subscription, SubscriptionStatus
        from app.models.service import Service
        from app.services.gym_rules import gym_rule

        customer = self.customer
        allow_non_entry = gym_rule(
            customer.branch.gym_id if customer and customer.branch else None,
            'pt_only_members_may_enter',
        )

        query = Subscription.query.join(
            Service, Subscription.service_id == Service.id
        ).filter(
            Subscription.customer_id == self.customer_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
        if not allow_non_entry:
            query = query.filter(Service.grants_gym_entry.is_(True))

        active_subscriptions = query.all()

        if not active_subscriptions:
            return False, "No active subscriptions"

        # Check if any subscription allows access
        for sub in active_subscriptions:
            if sub.can_access():
                self.last_used = datetime.utcnow()
                db.session.commit()
                return True, "Access granted"

        return False, "No valid active subscriptions"

    def deactivate(self, reason):
        """Deactivate fingerprint"""
        self.is_active = False
        self.deactivated_at = datetime.utcnow()
        self.deactivation_reason = reason

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name,
            'fingerprint_hash': self.fingerprint_hash[:20] + '...',  # Truncated for security
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'deactivated_at': self.deactivated_at.isoformat() if self.deactivated_at else None,
            'deactivation_reason': self.deactivation_reason
        }
