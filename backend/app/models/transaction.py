"""
Transaction model - Financial transactions
"""
from datetime import datetime
from app.extensions import db
import enum


class PaymentMethod(enum.Enum):
    """Payment methods"""
    CASH = 'cash'
    NETWORK = 'network'
    TRANSFER = 'transfer'


class TransactionType(enum.Enum):
    """Transaction types"""
    SUBSCRIPTION = 'subscription'
    RENEWAL = 'renewal'
    FREEZE = 'freeze'
    OTHER = 'other'


class Transaction(db.Model):
    """Transaction model - All financial transactions"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    
    # Amount
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Payment
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    
    # References
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    branch = db.relationship('Branch', back_populates='transactions')
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True, index=True)
    
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True, index=True)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_by_user = db.relationship('User', back_populates='transactions')
    
    # Description
    description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Reference number (for network/transfer)
    reference_number = db.Column(db.String(100), nullable=True)
    
    # Timestamp
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Transaction {self.id} - {self.amount} - {self.transaction_type.value}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'amount': float(self.amount),
            'payment_method': self.payment_method.value,
            'transaction_type': self.transaction_type.value,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name,
            'customer_id': self.customer_id,
            'subscription_id': self.subscription_id,
            'created_by': self.created_by,
            'created_by_name': self.created_by_user.full_name,
            'description': self.description,
            'notes': self.notes,
            'reference_number': self.reference_number,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
