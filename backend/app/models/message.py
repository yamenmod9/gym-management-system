"""Messages between a captain and the members who train privately with them.

There is no thread table. A thread *is* the (trainer, member) pair — the same
pair the private-training subscription already names — so a separate row would
be a second place for the same fact to live and a second place for it to go
stale. Listing threads reads the captain's roster and joins the last message.

Who may talk to whom is deliberately not stored here either. It is derived from
the subscription every time, by ``trainer_has_client``: a permission copied
onto a message row at send time would keep granting access long after the
member stopped training with that captain.
"""
import enum
from datetime import datetime

from app.extensions import db


class MessageSender(enum.Enum):
    """Which side of the conversation wrote this.

    A boolean would have done, but `sender == TRAINER` reads correctly at every
    call site and `is_trainer == False` does not.
    """
    TRAINER = 'trainer'
    MEMBER = 'member'


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)

    trainer_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)

    trainer = db.relationship('User', foreign_keys=[trainer_id])
    customer = db.relationship('Customer', foreign_keys=[customer_id])

    sender = db.Column(db.Enum(MessageSender), nullable=False)
    body = db.Column(db.Text, nullable=False)

    #: Denormalised from the customer so a gym's messages can be scoped and
    #: purged without joining, and so the row still says where it happened
    #: after the member transfers branch.
    branch_id = db.Column(
        db.Integer, db.ForeignKey('branches.id'), nullable=True, index=True)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    #: Null until the *other* party opens the thread.
    read_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        # Every query here is "this conversation, newest first".
        db.Index('ix_messages_thread', 'trainer_id', 'customer_id', 'created_at'),
    )

    #: Longest message accepted. Generous for a chat line, short enough that
    #: the column cannot be used as free file storage.
    MAX_BODY_LENGTH = 2000

    def __repr__(self):
        return (f'<Message {self.sender.value} trainer={self.trainer_id} '
                f'customer={self.customer_id}>')

    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'customer_id': self.customer_id,
            'sender': self.sender.value,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
        }
