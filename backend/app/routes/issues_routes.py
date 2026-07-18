"""
Issue routes — staff-to-staff operational tickets.

Visibility is the whole point and is deliberately the inverse of complaints:
an issue is seen by its reporter, the one colleague it was assigned to, and
anyone who OUTRANKS the reporter within the same gym/branch scope. So a front
desk's issue surfaces to their branch manager, regional manager and owner, but
not to a peer at the next desk.
"""
from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.user import User, UserRole
from app.utils import (
    success_response, error_response, get_current_user,
    get_current_gym_id, get_accessible_branch_ids,
)

issues_bp = Blueprint('issues', __name__, url_prefix='/api/issues')

# Every staff role may use issues; clients cannot (they carry a separate token
# whose identity get_current_user rejects).
_STAFF_ROLES = {
    UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.REGIONAL_MANAGER,
    UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK, UserRole.CENTRAL_ACCOUNTANT,
    UserRole.REGIONAL_ACCOUNTANT, UserRole.BRANCH_ACCOUNTANT, UserRole.ACCOUNTANT,
}


def _require_staff():
    user = get_current_user()
    if not user or user.role not in _STAFF_ROLES:
        return None, error_response('Staff access required', 403)
    return user, None


def _can_view(user, issue, accessible):
    """Reporter and assignee always; superiors within scope; owner/admin in gym."""
    if user.role in (UserRole.SUPER_ADMIN, UserRole.OWNER):
        return True
    if issue.reported_by_id == user.id or issue.assigned_to_id == user.id:
        return True
    reporter = issue.reported_by
    if reporter and user.rank > reporter.rank:
        if accessible is None or issue.branch_id is None or issue.branch_id in accessible:
            return True
    return False


@issues_bp.route('', methods=['GET'])
@jwt_required()
def list_issues():
    """Issues visible to the current staff member."""
    user, err = _require_staff()
    if err:
        return err

    status = request.args.get('status')
    box = request.args.get('box')  # 'inbox' (to me) | 'reported' (by me) | None (all)

    query = Issue.query
    gym_id = get_current_gym_id(user)
    if gym_id is not None:
        query = query.filter(Issue.gym_id == gym_id)

    if status:
        try:
            query = query.filter(Issue.status == IssueStatus(status))
        except ValueError:
            return error_response('Invalid status', 400)

    accessible = get_accessible_branch_ids(user)
    issues = query.order_by(Issue.created_at.desc()).all()

    visible = [i for i in issues if _can_view(user, i, accessible)]
    if box == 'reported':
        visible = [i for i in visible if i.reported_by_id == user.id]
    elif box == 'inbox':
        # Things routed to me: assigned to me, or raised by someone I outrank.
        visible = [
            i for i in visible
            if i.reported_by_id != user.id
        ]

    return success_response([i.to_dict() for i in visible])


@issues_bp.route('/<int:issue_id>', methods=['GET'])
@jwt_required()
def get_issue(issue_id):
    user, err = _require_staff()
    if err:
        return err
    issue = db.session.get(Issue, issue_id)
    if not issue:
        return error_response('Issue not found', 404)
    if not _can_view(user, issue, get_accessible_branch_ids(user)):
        return error_response('Access denied', 403)
    return success_response(issue.to_dict())


@issues_bp.route('', methods=['POST'])
@jwt_required()
def create_issue():
    """Raise an issue. Reporter's gym/branch scope it automatically."""
    user, err = _require_staff()
    if err:
        return err

    data = request.json or {}
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    if not title or not description:
        return error_response('title and description are required', 400)

    priority = IssuePriority.MEDIUM
    if data.get('priority'):
        try:
            priority = IssuePriority(str(data['priority']).lower())
        except ValueError:
            return error_response('Invalid priority', 400)

    assigned_to_id = data.get('assigned_to_id')
    if assigned_to_id:
        target = db.session.get(User, assigned_to_id)
        if not target or target.role not in _STAFF_ROLES:
            return error_response('Assigned staff member not found', 400)
        # Can only assign within your own gym.
        gym_id = get_current_gym_id(user)
        if gym_id is not None and target.gym_id != gym_id:
            return error_response('Cannot assign to staff of another gym', 403)

    issue = Issue(
        title=title,
        description=description,
        priority=priority,
        gym_id=get_current_gym_id(user),
        branch_id=user.branch_id,
        reported_by_id=user.id,
        assigned_to_id=assigned_to_id or None,
        status=IssueStatus.OPEN,
    )
    db.session.add(issue)
    db.session.commit()
    return success_response(issue.to_dict(), 'Issue raised successfully', 201)


@issues_bp.route('/<int:issue_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_issue(issue_id):
    """Update status / resolution. Any staff member who can see it may act."""
    user, err = _require_staff()
    if err:
        return err

    issue = db.session.get(Issue, issue_id)
    if not issue:
        return error_response('Issue not found', 404)
    if not _can_view(user, issue, get_accessible_branch_ids(user)):
        return error_response('Access denied', 403)

    data = request.json or {}

    if 'status' in data:
        try:
            new_status = IssueStatus(str(data['status']).lower())
        except ValueError:
            return error_response('Invalid status', 400)
        issue.status = new_status
        if new_status == IssueStatus.RESOLVED:
            issue.resolved_at = datetime.utcnow()
            issue.resolved_by_id = user.id
        else:
            issue.resolved_at = None
            issue.resolved_by_id = None

    if 'resolution_notes' in data:
        issue.resolution_notes = data['resolution_notes']

    if 'assigned_to_id' in data:
        assigned_to_id = data['assigned_to_id']
        if assigned_to_id:
            target = db.session.get(User, assigned_to_id)
            if not target or target.role not in _STAFF_ROLES:
                return error_response('Assigned staff member not found', 400)
        issue.assigned_to_id = assigned_to_id or None

    db.session.commit()
    return success_response(issue.to_dict(), 'Issue updated successfully')


@issues_bp.route('/assignable-staff', methods=['GET'])
@jwt_required()
def assignable_staff():
    """Staff this user can address an issue to: those who outrank them in-gym.

    Powers the "assign to" picker so a front desk can send an issue straight to
    their manager or the owner rather than into the general upward pool.
    """
    user, err = _require_staff()
    if err:
        return err

    query = User.query.filter(User.is_active.is_(True))
    gym_id = get_current_gym_id(user)
    if gym_id is not None:
        query = query.filter(User.gym_id == gym_id)

    candidates = [
        u for u in query.all()
        if u.id != user.id and u.rank > user.rank
    ]
    candidates.sort(key=lambda u: -u.rank)
    return success_response([
        {
            'id': u.id,
            'full_name': u.full_name,
            'role': u.role.value,
            'branch_name': u.branch.name if u.branch else None,
        }
        for u in candidates
    ])
