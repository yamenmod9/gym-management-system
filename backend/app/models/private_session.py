"""
Private training sessions: a captain logs a session they delivered, the member
confirms or disputes it, and a manager settles the disagreement.
"""
from datetime import datetime, timedelta
from app.extensions import db
import enum


#: How long a member has to answer before a logged session is taken as agreed.
#: Without this a member who simply never opens the app leaves the captain's
#: work permanently unconfirmed and the package impossible to reconcile.
AUTO_CONFIRM_AFTER = timedelta(hours=48)


class PrivateSessionStatus(enum.Enum):
    PENDING = 'pending'      # logged; waiting on the member
    CONFIRMED = 'confirmed'  # member agreed, or the window lapsed
    DISPUTED = 'disputed'    # member says it did not happen; manager to rule
    REVERSED = 'reversed'    # manager ruled for the member; session credited back


class PrivateSession(db.Model):
    """One private-training session logged against a subscription.

    The session is deducted from the member's balance the moment the captain
    logs it, not when the member confirms: a balance that only moves on
    confirmation would show sessions the member has already used as still
    available. A manager ruling for the member reverses the deduction, which is
    the correction path.
    """
    __tablename__ = 'private_sessions'

    id = db.Column(db.Integer, primary_key=True)

    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False, index=True)
    subscription = db.relationship('Subscription')

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer')

    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    trainer = db.relationship('User', foreign_keys=[trainer_id])

    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)

    status = db.Column(
        db.Enum(PrivateSessionStatus),
        default=PrivateSessionStatus.PENDING,
        nullable=False,
        index=True,
    )

    notes = db.Column(db.Text, nullable=True)              # what the captain worked on
    dispute_reason = db.Column(db.Text, nullable=True)     # why the member objected

    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    answered_at = db.Column(db.DateTime, nullable=True)    # confirmed or disputed

    resolved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_user_id])
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<PrivateSession {self.id} customer={self.customer_id} {self.status.value}>'

    @property
    def auto_confirms_at(self):
        return self.logged_at + AUTO_CONFIRM_AFTER

    @property
    def is_auto_confirmed(self):
        """Pending, but past the window — treated as agreed."""
        return (
            self.status == PrivateSessionStatus.PENDING
            and datetime.utcnow() >= self.auto_confirms_at
        )

    @property
    def effective_status(self):
        """Status as the world should see it, applying the auto-confirm window.

        Derived rather than written by a scheduled job: there is no worker
        process in this deployment, so a status that depended on one would sit
        stale forever.
        """
        if self.is_auto_confirmed:
            return PrivateSessionStatus.CONFIRMED
        return self.status

    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'trainer_id': self.trainer_id,
            'trainer_name': self.trainer.full_name if self.trainer else None,
            'branch_id': self.branch_id,
            'status': self.effective_status.value,
            'raw_status': self.status.value,
            'auto_confirmed': self.is_auto_confirmed,
            'notes': self.notes,
            'dispute_reason': self.dispute_reason,
            'logged_at': self.logged_at.isoformat(),
            'auto_confirms_at': self.auto_confirms_at.isoformat(),
            'answered_at': self.answered_at.isoformat() if self.answered_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by.full_name if self.resolved_by else None,
            'resolution_note': self.resolution_note,
        }
