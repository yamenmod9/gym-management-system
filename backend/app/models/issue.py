"""
Issue model — staff-to-staff operational tickets.

Distinct from Complaint on purpose. A Complaint is raised by a *member* about
the gym and every staff member should help resolve it. An Issue is raised by a
*staff member* and routed upward — to whoever outranks them in the same scope,
or to one named colleague — so problems the front line can't fix reach someone
who can. The two never share a table because their audiences are opposite:
complaints face down to the whole team, issues face up the hierarchy.
"""
from datetime import datetime
from app.extensions import db
import enum


class IssueStatus(enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'


class IssuePriority(enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class Issue(db.Model):
    """A ticket a staff member raises for higher-ranking / named staff."""
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.Enum(IssueStatus), default=IssueStatus.OPEN, nullable=False, index=True)
    priority = db.Column(db.Enum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False, index=True)

    # Scope — the reporter's gym and branch, so visibility can be limited the
    # same way every other record is.
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=True, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True, index=True)

    # Who raised it.
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reported_by = db.relationship('User', foreign_keys=[reported_by_id])

    # Optional single recipient. When null, the issue is addressed to "whoever
    # outranks me in my scope" rather than one person.
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])

    # Resolution.
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id])
    resolved_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Issue {self.id} - {self.title}>'

    @property
    def branch_name(self):
        return self.branch.name if self.branch_id and self.branch else None

    branch = db.relationship('Branch')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'gym_id': self.gym_id,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name if self.branch else None,
            'reported_by_id': self.reported_by_id,
            'reported_by_name': self.reported_by.full_name if self.reported_by else None,
            'reported_by_role': self.reported_by.role.value if self.reported_by else None,
            'assigned_to_id': self.assigned_to_id,
            'assigned_to_name': self.assigned_to.full_name if self.assigned_to else None,
            'resolution_notes': self.resolution_notes,
            'resolved_by_id': self.resolved_by_id,
            'resolved_by_name': self.resolved_by.full_name if self.resolved_by else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
