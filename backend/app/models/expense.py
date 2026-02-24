"""
Expense model - Business expenses tracking
"""
from datetime import datetime
from app.extensions import db
import enum


class ExpenseStatus(enum.Enum):
    """Expense approval status"""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Expense(db.Model):
    """Expense model - Track business expenses"""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    
    # Expense details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100), nullable=True)  # e.g., 'maintenance', 'supplies', 'utilities'
    
    # Branch
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    branch = db.relationship('Branch', back_populates='expenses')
    
    # Approval workflow
    status = db.Column(db.Enum(ExpenseStatus), default=ExpenseStatus.PENDING, nullable=False, index=True)
    
    # Created by (who requested)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_by = db.relationship('User', foreign_keys=[created_by_id], back_populates='expenses')
    
    # Approved/Rejected by
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])
    
    review_notes = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    expense_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Expense {self.title} - {self.amount}>'

    @property
    def branch_name(self):
        """Branch name for schema serialization"""
        return self.branch.name if self.branch else 'N/A'

    @property
    def created_by_name(self):
        """Creator name for schema serialization"""
        return self.created_by.full_name if self.created_by else 'N/A'

    @property
    def reviewed_by_name(self):
        """Reviewer name for schema serialization"""
        return self.reviewed_by.full_name if self.reviewed_by else None

    def approve(self, reviewer_id, notes=None):
        """Approve expense"""
        self.status = ExpenseStatus.APPROVED
        self.reviewed_by_id = reviewer_id
        self.review_notes = notes
        self.reviewed_at = datetime.utcnow()

    def reject(self, reviewer_id, notes):
        """Reject expense"""
        self.status = ExpenseStatus.REJECTED
        self.reviewed_by_id = reviewer_id
        self.review_notes = notes
        self.reviewed_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'amount': float(self.amount),
            'category': self.category,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name,
            'status': self.status.value,
            'created_by_id': self.created_by_id,
            'created_by_name': self.created_by.full_name,
            'reviewed_by_id': self.reviewed_by_id,
            'reviewed_by_name': self.reviewed_by.full_name if self.reviewed_by else None,
            'review_notes': self.review_notes,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'expense_date': self.expense_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
