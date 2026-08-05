"""
Complaint model - Customer complaints tracking
"""
from datetime import datetime
from app.extensions import db
import enum


class ComplaintType(enum.Enum):
    """Complaint types"""
    DEVICE = 'device'
    POOL = 'pool'
    CLEANLINESS = 'cleanliness'
    SERVICE = 'service'
    OTHER = 'other'


class ComplaintStatus(enum.Enum):
    """Complaint status"""
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    CLOSED = 'closed'


class Complaint(db.Model):
    """Complaint model"""
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    
    # Complaint details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complaint_type = db.Column(db.Enum(ComplaintType), nullable=False, index=True)
    
    # Status
    status = db.Column(db.Enum(ComplaintStatus), default=ComplaintStatus.OPEN, nullable=False, index=True)
    
    # Branch
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    branch = db.relationship('Branch', back_populates='complaints')
    
    # Customer (optional - can be anonymous)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True, index=True)
    # The alerts feed falls back to this relationship when customer_name is
    # blank, which is the normal case for a complaint filed by a registered
    # member. It was never declared, so that fallback raised AttributeError and
    # took the whole alerts endpoint down with a 500 whenever any complaint was
    # open — which is precisely when the feed has something to say.
    customer = db.relationship('Customer')
    customer_name = db.Column(db.String(150), nullable=True)  # If not registered
    customer_phone = db.Column(db.String(20), nullable=True)
    
    # Resolution
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Complaint {self.id} - {self.title}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'complaint_type': self.complaint_type.value,
            'status': self.status.value,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'resolution_notes': self.resolution_notes,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
