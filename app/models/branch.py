"""
Branch model - Multi-branch support
"""
from datetime import datetime
from app.extensions import db


class Branch(db.Model):
    """Branch/Location model"""
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('User', back_populates='branch', lazy='dynamic')
    customers = db.relationship('Customer', back_populates='branch', lazy='dynamic')
    subscriptions = db.relationship('Subscription', back_populates='branch', lazy='dynamic')
    transactions = db.relationship('Transaction', back_populates='branch', lazy='dynamic')
    expenses = db.relationship('Expense', back_populates='branch', lazy='dynamic')
    complaints = db.relationship('Complaint', back_populates='branch', lazy='dynamic')
    daily_closings = db.relationship('DailyClosing', back_populates='branch', lazy='dynamic')

    def __repr__(self):
        return f'<Branch {self.name} ({self.code})>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'address': self.address,
            'phone': self.phone,
            'city': self.city,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'staff_count': self.staff.count(),
            'customers_count': self.customers.count()
        }
