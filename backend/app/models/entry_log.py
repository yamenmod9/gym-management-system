"""
Entry Log model - Track gym access entries
"""
from datetime import datetime
from app.extensions import db
import enum


class EntryType(enum.Enum):
    """Entry types"""
    QR_SCAN = 'qr_scan'
    FINGERPRINT = 'fingerprint'
    MANUAL = 'manual'
    BARCODE = 'barcode'


class EntryStatus(enum.Enum):
    """Entry validation status"""
    APPROVED = 'approved'
    DENIED = 'denied'
    PENDING = 'pending'


class EntryLog(db.Model):
    """Entry log for tracking gym access"""
    __tablename__ = 'entry_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    # Customer and subscription
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer', backref=db.backref('entry_logs', lazy='dynamic'))
    
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True, index=True)
    subscription = db.relationship('Subscription', backref=db.backref('entry_logs', lazy='dynamic'))
    
    # Entry details
    entry_type = db.Column(db.Enum(EntryType), nullable=False, default=EntryType.QR_SCAN)
    entry_status = db.Column(db.Enum(EntryStatus), nullable=False, default=EntryStatus.APPROVED)
    
    # Location
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    branch = db.relationship('Branch', backref=db.backref('entry_logs', lazy='dynamic'))
    
    # Validation details
    validation_token = db.Column(db.String(500), nullable=True)  # QR/Barcode token used
    coins_deducted = db.Column(db.Integer, default=0, nullable=False)  # Coins/visits deducted
    
    # Denial reason
    denial_reason = db.Column(db.String(200), nullable=True)
    
    # Staff who processed entry
    processed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    processed_by = db.relationship('User', backref=db.backref('processed_entries', lazy='dynamic'))
    
    # Notes
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<EntryLog {self.id} - Customer {self.customer_id} at {self.entry_time}>'

    @classmethod
    def create_entry(cls, customer_id, branch_id, entry_type=EntryType.QR_SCAN,
                     subscription_id=None, validation_token=None, coins_deducted=0,
                     processed_by_user_id=None, notes=None):
        """
        Create a new entry log
        
        Args:
            customer_id: Customer ID
            branch_id: Branch ID
            entry_type: Type of entry (QR, fingerprint, etc.)
            subscription_id: Active subscription ID
            validation_token: Token used for validation
            coins_deducted: Number of coins/visits deducted
            processed_by_user_id: Staff user who processed entry
            notes: Additional notes
        
        Returns:
            EntryLog: Created entry log
        """
        entry = cls(
            customer_id=customer_id,
            branch_id=branch_id,
            entry_type=entry_type,
            subscription_id=subscription_id,
            validation_token=validation_token,
            coins_deducted=coins_deducted,
            processed_by_user_id=processed_by_user_id,
            notes=notes,
            entry_status=EntryStatus.APPROVED
        )
        
        db.session.add(entry)
        return entry

    @classmethod
    def create_denied_entry(cls, customer_id, branch_id, entry_type, denial_reason,
                           subscription_id=None, processed_by_user_id=None):
        """
        Create a denied entry log
        
        Args:
            customer_id: Customer ID
            branch_id: Branch ID
            entry_type: Type of entry attempted
            denial_reason: Reason for denial
            subscription_id: Subscription ID if applicable
            processed_by_user_id: Staff user who denied entry
        
        Returns:
            EntryLog: Created entry log with denied status
        """
        entry = cls(
            customer_id=customer_id,
            branch_id=branch_id,
            entry_type=entry_type,
            subscription_id=subscription_id,
            entry_status=EntryStatus.DENIED,
            denial_reason=denial_reason,
            processed_by_user_id=processed_by_user_id
        )
        
        db.session.add(entry)
        return entry

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'subscription_id': self.subscription_id,
            'entry_type': self.entry_type.value,
            'entry_status': self.entry_status.value,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name if self.branch else None,
            'coins_deducted': self.coins_deducted,
            'denial_reason': self.denial_reason,
            'processed_by': self.processed_by.full_name if self.processed_by else None,
            'notes': self.notes,
            'entry_time': self.entry_time.isoformat(),
            'created_at': self.created_at.isoformat()
        }
