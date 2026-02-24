"""
Freeze History model - Track subscription freezes
"""
from datetime import datetime
from app.extensions import db


class FreezeHistory(db.Model):
    """Track subscription freeze history"""
    __tablename__ = 'freeze_history'

    id = db.Column(db.Integer, primary_key=True)
    
    # Subscription reference
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False, index=True)
    subscription = db.relationship('Subscription', back_populates='freeze_history')
    
    # Freeze details
    freeze_start = db.Column(db.Date, nullable=False)
    freeze_end = db.Column(db.Date, nullable=False)
    freeze_days = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    
    # Cost (if paid freeze)
    cost = db.Column(db.Numeric(10, 2), default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)  # Active freeze or completed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    unfrozen_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<FreezeHistory {self.id} - Subscription {self.subscription_id}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'freeze_start': self.freeze_start.isoformat(),
            'freeze_end': self.freeze_end.isoformat(),
            'freeze_days': self.freeze_days,
            'reason': self.reason,
            'cost': float(self.cost),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'unfrozen_at': self.unfrozen_at.isoformat() if self.unfrozen_at else None
        }
