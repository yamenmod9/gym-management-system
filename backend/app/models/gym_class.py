"""
Classes: a recurring session a manager assigns a trainer to run, the individual
sittings of it, who attended, and what they thought of it.
"""
from datetime import datetime
from app.extensions import db
import enum


class ClassSessionStatus(enum.Enum):
    """Lifecycle of one sitting of a class."""
    OPEN = 'open'          # started; the trainer is still adding attendees
    CLOSED = 'closed'      # finished; feedback has been requested
    CANCELLED = 'cancelled'


class GymClass(db.Model):
    """A recurring class: 'Spinning, Mon/Wed/Fri 18:00, run by Omar'."""
    __tablename__ = 'gym_classes'

    id = db.Column(db.Integer, primary_key=True)

    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=True, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    branch = db.relationship('Branch')

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Assigned by a manager. Nullable so a class can be created before anyone
    # is free to take it; a class with no trainer simply cannot be started.
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    trainer = db.relationship('User', foreign_keys=[trainer_id])

    capacity = db.Column(db.Integer, nullable=True)

    # Which weekdays it runs, as a comma-separated list of Python weekday
    # numbers (Monday=0 … Sunday=6), e.g. "0,2,4". Stored as text rather than
    # seven booleans so the shape survives adding fortnightly patterns later.
    days_of_week = db.Column(db.String(20), nullable=False, default='')

    start_time = db.Column(db.String(5), nullable=True)   # 'HH:MM', display only
    duration_minutes = db.Column(db.Integer, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = db.relationship('ClassSession', back_populates='gym_class', lazy='dynamic')

    def __repr__(self):
        return f'<GymClass {self.name} branch={self.branch_id}>'

    @property
    def weekdays(self):
        """The scheduled weekdays as a list of ints."""
        return [int(d) for d in self.days_of_week.split(',') if d.strip().isdigit()]

    def runs_on(self, day):
        """Is this class scheduled on the given date?"""
        return day.weekday() in self.weekdays

    def to_dict(self, include_trainer=True):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name if self.branch else None,
            'trainer_id': self.trainer_id,
            'capacity': self.capacity,
            'days_of_week': self.weekdays,
            'start_time': self.start_time,
            'duration_minutes': self.duration_minutes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }
        if include_trainer:
            data['trainer_name'] = self.trainer.full_name if self.trainer else None
        return data


class ClassSession(db.Model):
    """One sitting of a class on one day."""
    __tablename__ = 'class_sessions'

    id = db.Column(db.Integer, primary_key=True)

    class_id = db.Column(db.Integer, db.ForeignKey('gym_classes.id'), nullable=False, index=True)
    gym_class = db.relationship('GymClass', back_populates='sessions')

    # Denormalised from the class so scoping and reporting never have to join
    # through it — and so a session stays attributable if the class is edited.
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    trainer = db.relationship('User', foreign_keys=[trainer_id])

    session_date = db.Column(db.Date, nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)

    status = db.Column(
        db.Enum(ClassSessionStatus),
        default=ClassSessionStatus.OPEN,
        nullable=False,
        index=True,
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    attendance = db.relationship(
        'ClassAttendance', back_populates='session',
        lazy='dynamic', cascade='all, delete-orphan',
    )
    feedback = db.relationship(
        'ClassFeedback', back_populates='session',
        lazy='dynamic', cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f'<ClassSession {self.id} class={self.class_id} {self.session_date}>'

    def to_dict(self, attendance_count=None, feedback_summary=None):
        data = {
            'id': self.id,
            'class_id': self.class_id,
            'class_name': self.gym_class.name if self.gym_class else None,
            'branch_id': self.branch_id,
            'trainer_id': self.trainer_id,
            'trainer_name': self.trainer.full_name if self.trainer else None,
            'session_date': self.session_date.isoformat(),
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'status': self.status.value,
            'attendance_count': (
                attendance_count if attendance_count is not None
                else self.attendance.count()
            ),
        }
        if feedback_summary is not None:
            data['feedback'] = feedback_summary
        return data


class ClassAttendance(db.Model):
    """A member the trainer marked as present at a session."""
    __tablename__ = 'class_attendance'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'customer_id', name='uq_class_attendance_session_customer'),
    )

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(db.Integer, db.ForeignKey('class_sessions.id'), nullable=False, index=True)
    session = db.relationship('ClassSession', back_populates='attendance')

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer')

    # Whether a coin was actually taken. Recorded per row rather than inferred
    # from the gym rule, because the rule can be switched off later and the
    # history still has to say what happened at the time.
    coin_deducted = db.Column(db.Boolean, default=False, nullable=False)

    marked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'coin_deducted': self.coin_deducted,
            'marked_at': self.marked_at.isoformat(),
        }


class ClassFeedback(db.Model):
    """A member's rating of a session they attended."""
    __tablename__ = 'class_feedback'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'customer_id', name='uq_class_feedback_session_customer'),
    )

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(db.Integer, db.ForeignKey('class_sessions.id'), nullable=False, index=True)
    session = db.relationship('ClassSession', back_populates='feedback')

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer')

    rating = db.Column(db.Integer, nullable=False)   # 1..5, enforced at the route
    comment = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self, include_member=True):
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
        }
        if include_member:
            data['customer_id'] = self.customer_id
            data['customer_name'] = self.customer.full_name if self.customer else None
        return data
