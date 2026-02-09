"""
Subscription model - Customer subscriptions to services
"""
from datetime import datetime, timedelta
from app.extensions import db
import enum


class SubscriptionStatus(enum.Enum):
    """Subscription status"""
    ACTIVE = 'active'
    FROZEN = 'frozen'
    STOPPED = 'stopped'
    EXPIRED = 'expired'


class Subscription(db.Model):
    """Subscription model - links customers to services"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    
    # References
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer', back_populates='subscriptions')
    
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False, index=True)
    service = db.relationship('Service', back_populates='subscriptions')
    
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    branch = db.relationship('Branch', back_populates='subscriptions')
    
    # Dates
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    
    # Status
    status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False, index=True)
    
    # Freeze tracking
    freeze_count = db.Column(db.Integer, default=0)
    total_frozen_days = db.Column(db.Integer, default=0)
    
    # Stop information
    stop_reason = db.Column(db.Text, nullable=True)
    stopped_at = db.Column(db.DateTime, nullable=True)
    
    # Classes tracking (for education programs)
    classes_attended = db.Column(db.Integer, default=0)
    
    # Visit/Class tracking (for entry system)
    remaining_visits = db.Column(db.Integer, nullable=True)  # For unlimited or visit-based subscriptions
    remaining_classes = db.Column(db.Integer, nullable=True)  # For class-based subscriptions
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    freeze_history = db.relationship('FreezeHistory', back_populates='subscription', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Subscription {self.id} - {self.customer.full_name} - {self.service.name}>'

    def is_expired(self):
        """Check if subscription is expired"""
        if self.status == SubscriptionStatus.EXPIRED:
            return True
        if self.end_date < datetime.utcnow().date():
            self.status = SubscriptionStatus.EXPIRED
            db.session.commit()
            return True
        return False

    def can_access(self):
        """Check if customer can access facility"""
        return self.status == SubscriptionStatus.ACTIVE and not self.is_expired()

    def freeze(self, days, reason=None):
        """Freeze subscription"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False, "Subscription is not active"
        
        if self.freeze_count >= self.service.freeze_count_limit:
            return False, "Freeze limit reached"
        
        if self.total_frozen_days + days > self.service.freeze_max_days:
            return False, "Total freeze days exceeded"
        
        self.status = SubscriptionStatus.FROZEN
        self.freeze_count += 1
        self.total_frozen_days += days
        
        # Extend end date
        self.end_date += timedelta(days=days)
        
        return True, "Subscription frozen successfully"

    def unfreeze(self):
        """Unfreeze subscription"""
        if self.status == SubscriptionStatus.FROZEN:
            self.status = SubscriptionStatus.ACTIVE
            return True, "Subscription unfrozen successfully"
        return False, "Subscription is not frozen"

    def stop(self, reason):
        """Stop subscription"""
        if self.status == SubscriptionStatus.STOPPED:
            return False, "Subscription is already stopped"
        
        self.status = SubscriptionStatus.STOPPED
        self.stop_reason = reason
        self.stopped_at = datetime.utcnow()
        return True, "Subscription stopped successfully"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name,
            'customer_phone': self.customer.phone,
            'service_id': self.service_id,
            'service_name': self.service.name,
            'service_type': self.service.service_type.value,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status.value,
            'freeze_count': self.freeze_count,
            'total_frozen_days': self.total_frozen_days,
            'stop_reason': self.stop_reason,
            'stopped_at': self.stopped_at.isoformat() if self.stopped_at else None,
            'classes_attended': self.classes_attended,
            'created_at': self.created_at.isoformat(),
            'is_expired': self.is_expired(),
            'can_access': self.can_access()
        }
