"""
Service model - Gym services (Gym, Swimming, Karate, Bundles)
"""
from datetime import datetime
from app.extensions import db
import enum


class ServiceType(enum.Enum):
    """Service types"""
    GYM = 'gym'
    SWIMMING_EDUCATION = 'swimming_education'
    SWIMMING_RECREATION = 'swimming_recreation'
    KARATE = 'karate'
    BUNDLE = 'bundle'


class Service(db.Model):
    """Service/Package model"""
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    service_type = db.Column(db.Enum(ServiceType), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Duration
    duration_days = db.Column(db.Integer, nullable=False)  # Subscription duration in days
    
    # Allowed days per week (e.g., 3 days, 5 days, unlimited=7)
    allowed_days_per_week = db.Column(db.Integer, nullable=False, default=7)
    
    # Class limits (for education programs)
    class_limit = db.Column(db.Integer, nullable=True)  # Max classes per subscription
    
    # Freeze rules
    freeze_count_limit = db.Column(db.Integer, default=2)  # Max freeze times
    freeze_max_days = db.Column(db.Integer, default=15)  # Max freeze duration
    freeze_is_paid = db.Column(db.Boolean, default=False)  # Is freeze paid
    freeze_cost = db.Column(db.Numeric(10, 2), default=0)  # Cost per freeze
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', back_populates='service', lazy='dynamic')

    @property
    def has_classes(self):
        """Check if this service has class limits"""
        return self.class_limit is not None and self.class_limit > 0
    
    @property
    def has_visits(self):
        """Check if this service has visit tracking (currently all services have unlimited visits)"""
        # Can be extended in future to support limited visits per subscription
        return not self.has_classes

    def __repr__(self):
        return f'<Service {self.name} ({self.service_type.value})>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'service_type': self.service_type.value,
            'description': self.description,
            'price': float(self.price),
            'duration_days': self.duration_days,
            'allowed_days_per_week': self.allowed_days_per_week,
            'class_limit': self.class_limit,
            'freeze_count_limit': self.freeze_count_limit,
            'freeze_max_days': self.freeze_max_days,
            'freeze_is_paid': self.freeze_is_paid,
            'freeze_cost': float(self.freeze_cost),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
