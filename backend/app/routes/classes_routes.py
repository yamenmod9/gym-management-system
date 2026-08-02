"""
Class routes — managers schedule classes and assign trainers; trainers run the
sessions, record who turned up, and close them to collect feedback.
"""
from datetime import date, datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import (
    Customer, GymClass, ClassSession, ClassAttendance, ClassFeedback,
    ClassSessionStatus, Subscription,
)
from app.models.branch import Branch
from app.models.user import User, UserRole
from app.services.gym_rules import gym_rule
from app.utils import (
    success_response, error_response, role_required, get_current_user,
    get_accessible_branch_ids, scope_query_to_branches, get_current_gym_id,
)
from app.extensions import db

classes_bp = Blueprint('classes', __name__, url_prefix='/api/classes')

#: Who may create and edit classes and read every trainer's feedback.
MANAGER_ROLES = (
    UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER,
)


def _parse_days(raw):
    """Normalise a weekday list into the stored '0,2,4' form."""
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = [p for p in raw.split(',') if p.strip()]
    if not isinstance(raw, (list, tuple)):
        raise ValueError('days_of_week must be a list of weekday numbers (0=Mon)')
    days = sorted({int(d) for d in raw})
    if any(d < 0 or d > 6 for d in days):
        raise ValueError('weekday numbers must be between 0 (Monday) and 6 (Sunday)')
    return ','.join(str(d) for d in days)


def _load_scoped_class(class_id):
    """A class inside the caller's branch scope, or (None, error)."""
    gym_class = db.session.get(GymClass, class_id)
    if not gym_class:
        return None, error_response('Class not found', 404)

    accessible = get_accessible_branch_ids()
    if accessible is not None and gym_class.branch_id not in accessible:
        # 404 rather than 403: whether a class exists in another gym is itself
        # information the caller has no business confirming.
        return None, error_response('Class not found', 404)
    return gym_class, None


def _validate_trainer(trainer_id, branch_id):
    """A trainer id that may actually be assigned to this branch's class."""
    if trainer_id is None:
        return None, None
    trainer = db.session.get(User, trainer_id)
    if not trainer or trainer.role != UserRole.TRAINER or not trainer.is_active:
        return None, error_response('Trainer not found', 404)

    branch = db.session.get(Branch, branch_id)
    if branch is None or trainer.gym_id != branch.gym_id:
        return None, error_response('That trainer belongs to a different gym', 400)
    return trainer, None


# ─────────────────────────────── manager ────────────────────────────────

@classes_bp.route('', methods=['GET'])
@jwt_required()
def list_classes():
    """Classes in the caller's scope. Trainers see only their own."""
    user = get_current_user()
    branch_id = request.args.get('branch_id', type=int)

    query = GymClass.query
    query = scope_query_to_branches(query, GymClass.branch_id, user, branch_id)
    if user.role == UserRole.TRAINER:
        query = query.filter(GymClass.trainer_id == user.id)

    classes = query.order_by(GymClass.name).all()
    return success_response([c.to_dict() for c in classes])


@classes_bp.route('', methods=['POST'])
@jwt_required()
@role_required(*MANAGER_ROLES)
def create_class():
    """Schedule a class and (optionally) assign the trainer who runs it."""
    user = get_current_user()
    data = request.json or {}

    name = (data.get('name') or '').strip()
    if not name:
        return error_response('name is required', 400)

    branch_id = data.get('branch_id') or user.branch_id
    if not branch_id:
        return error_response('branch_id is required', 400)

    accessible = get_accessible_branch_ids(user)
    if accessible is not None and branch_id not in accessible:
        return error_response('Access denied to this branch', 403)

    try:
        days = _parse_days(data.get('days_of_week', [])) or ''
    except (ValueError, TypeError) as e:
        return error_response(str(e), 400)

    trainer, err = _validate_trainer(data.get('trainer_id'), branch_id)
    if err:
        return err

    branch = db.session.get(Branch, branch_id)
    gym_class = GymClass(
        name=name,
        description=data.get('description'),
        branch_id=branch_id,
        gym_id=branch.gym_id if branch else None,
        trainer_id=trainer.id if trainer else None,
        capacity=data.get('capacity'),
        days_of_week=days,
        start_time=data.get('start_time'),
        duration_minutes=data.get('duration_minutes'),
    )
    db.session.add(gym_class)
    db.session.commit()

    return success_response(gym_class.to_dict(), 'Class created', 201)


@classes_bp.route('/<int:class_id>', methods=['PUT'])
@jwt_required()
@role_required(*MANAGER_ROLES)
def update_class(class_id):
    """Edit a class, including reassigning the trainer."""
    gym_class, err = _load_scoped_class(class_id)
    if err:
        return err

    data = request.json or {}

    if 'trainer_id' in data:
        trainer, terr = _validate_trainer(data['trainer_id'], gym_class.branch_id)
        if terr:
            return terr
        gym_class.trainer_id = trainer.id if trainer else None

    if 'days_of_week' in data:
        try:
            gym_class.days_of_week = _parse_days(data['days_of_week']) or ''
        except (ValueError, TypeError) as e:
            return error_response(str(e), 400)

    for field in ('name', 'description', 'capacity', 'start_time', 'duration_minutes'):
        if field in data:
            setattr(gym_class, field, data[field])
    if 'is_active' in data:
        gym_class.is_active = bool(data['is_active'])

    db.session.commit()
    return success_response(gym_class.to_dict(), 'Class updated')


@classes_bp.route('/<int:class_id>', methods=['DELETE'])
@jwt_required()
@role_required(*MANAGER_ROLES)
def deactivate_class(class_id):
    """Retire a class. Kept rather than deleted so past sessions and their
    feedback stay readable."""
    gym_class, err = _load_scoped_class(class_id)
    if err:
        return err

    gym_class.is_active = False
    db.session.commit()
    return success_response(gym_class.to_dict(), 'Class deactivated')


# ─────────────────────────────── trainer ────────────────────────────────

@classes_bp.route('/mine', methods=['GET'])
@jwt_required()
@role_required(UserRole.TRAINER)
def my_classes():
    """The classes this trainer runs, flagged with whether one runs today."""
    user = get_current_user()
    today = date.today()

    classes = GymClass.query.filter(
        GymClass.trainer_id == user.id,
        GymClass.is_active.is_(True),
    ).order_by(GymClass.name).all()

    open_by_class = {
        s.class_id: s for s in ClassSession.query.filter(
            ClassSession.trainer_id == user.id,
            ClassSession.session_date == today,
            ClassSession.status == ClassSessionStatus.OPEN,
        ).all()
    }

    payload = []
    for c in classes:
        data = c.to_dict(include_trainer=False)
        data['runs_today'] = c.runs_on(today)
        open_session = open_by_class.get(c.id)
        data['open_session'] = open_session.to_dict() if open_session else None
        payload.append(data)

    return success_response(payload)


@classes_bp.route('/<int:class_id>/sessions', methods=['POST'])
@jwt_required()
@role_required(UserRole.TRAINER)
def start_session(class_id):
    """Start today's sitting of a class."""
    user = get_current_user()
    gym_class, err = _load_scoped_class(class_id)
    if err:
        return err

    if gym_class.trainer_id != user.id:
        return error_response('You are not assigned to this class', 403)
    if not gym_class.is_active:
        return error_response('This class is no longer active', 400)

    today = date.today()
    if not gym_class.runs_on(today):
        return error_response('This class is not scheduled to run today', 400)

    # One sitting per class per day — starting twice would split the register
    # and ask attendees for feedback on a session they were never at.
    existing = ClassSession.query.filter_by(
        class_id=gym_class.id, session_date=today,
    ).filter(ClassSession.status != ClassSessionStatus.CANCELLED).first()
    if existing:
        return success_response(existing.to_dict(), 'Session already started')

    session = ClassSession(
        class_id=gym_class.id,
        branch_id=gym_class.branch_id,
        trainer_id=user.id,
        session_date=today,
    )
    db.session.add(session)
    db.session.commit()

    return success_response(session.to_dict(), 'Session started', 201)


@classes_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """A session with its register."""
    session, err = _load_scoped_session(session_id)
    if err:
        return err

    data = session.to_dict()
    data['attendance'] = [a.to_dict() for a in session.attendance.all()]
    return success_response(data)


def _load_scoped_session(session_id):
    session = db.session.get(ClassSession, session_id)
    if not session:
        return None, error_response('Session not found', 404)

    user = get_current_user()
    accessible = get_accessible_branch_ids(user)
    if accessible is not None and session.branch_id not in accessible:
        return None, error_response('Session not found', 404)
    if user.role == UserRole.TRAINER and session.trainer_id != user.id:
        return None, error_response('Session not found', 404)
    return session, None


@classes_bp.route('/sessions/<int:session_id>/attendance', methods=['POST'])
@jwt_required()
@role_required(UserRole.TRAINER)
def add_attendance(session_id):
    """Mark members present. Accepts customer_id or customer_ids."""
    user = get_current_user()
    session, err = _load_scoped_session(session_id)
    if err:
        return err

    if session.status != ClassSessionStatus.OPEN:
        return error_response('This session is closed', 400)

    data = request.json or {}
    ids = data.get('customer_ids')
    if ids is None:
        single = data.get('customer_id')
        ids = [single] if single is not None else []
    if not isinstance(ids, list) or not ids:
        return error_response('Provide customer_id or a non-empty customer_ids list', 400)

    deducts = gym_rule(
        get_current_gym_id(user), 'class_attendance_deducts_coin'
    )

    already = {a.customer_id for a in session.attendance.all()}
    added, skipped = [], []

    for raw_id in ids:
        try:
            customer_id = int(raw_id)
        except (TypeError, ValueError):
            skipped.append({'customer_id': raw_id, 'reason': 'invalid id'})
            continue

        if customer_id in already:
            skipped.append({'customer_id': customer_id, 'reason': 'already marked'})
            continue

        customer = db.session.get(Customer, customer_id)
        # Same branch as the session: a trainer must not be able to mark a
        # member of another branch (or gym) into their register.
        if not customer or customer.branch_id != session.branch_id:
            skipped.append({'customer_id': customer_id, 'reason': 'not a member of this branch'})
            continue

        if session.gym_class and session.gym_class.capacity is not None:
            if len(already) + len(added) >= session.gym_class.capacity:
                skipped.append({'customer_id': customer_id, 'reason': 'class is full'})
                continue

        coin_taken = False
        if deducts:
            entry = Subscription.entry_subscription_for(customer_id)
            if entry is not None and entry.remaining_coins is not None:
                if entry.remaining_coins <= 0:
                    skipped.append({'customer_id': customer_id, 'reason': 'no coins remaining'})
                    continue
                entry.remaining_coins -= 1
                coin_taken = True

        db.session.add(ClassAttendance(
            session_id=session.id,
            customer_id=customer_id,
            coin_deducted=coin_taken,
        ))
        added.append(customer_id)

    db.session.commit()

    return success_response({
        'session_id': session.id,
        'added': added,
        'skipped': skipped,
        'attendance_count': session.attendance.count(),
        'coin_rule_active': deducts,
    }, f'{len(added)} member(s) marked present')


@classes_bp.route('/sessions/<int:session_id>/attendance/<int:customer_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRole.TRAINER)
def remove_attendance(session_id, customer_id):
    """Undo a mistaken mark, refunding the coin if one was taken."""
    session, err = _load_scoped_session(session_id)
    if err:
        return err
    if session.status != ClassSessionStatus.OPEN:
        return error_response('This session is closed', 400)

    row = ClassAttendance.query.filter_by(
        session_id=session.id, customer_id=customer_id
    ).first()
    if not row:
        return error_response('That member is not on this register', 404)

    if row.coin_deducted:
        entry = Subscription.entry_subscription_for(customer_id)
        if entry is not None and entry.remaining_coins is not None:
            entry.remaining_coins += 1

    db.session.delete(row)
    db.session.commit()
    return success_response({'session_id': session.id}, 'Attendance removed')


@classes_bp.route('/sessions/<int:session_id>/close', methods=['POST'])
@jwt_required()
@role_required(UserRole.TRAINER)
def close_session(session_id):
    """End a session and ask everyone who attended to rate it."""
    user = get_current_user()
    session, err = _load_scoped_session(session_id)
    if err:
        return err

    if session.status != ClassSessionStatus.OPEN:
        return error_response('This session is already closed', 400)

    session.status = ClassSessionStatus.CLOSED
    session.ended_at = datetime.utcnow()
    db.session.commit()

    attendees = session.attendance.all()
    notified = 0
    if gym_rule(get_current_gym_id(user), 'ask_feedback_after_class'):
        from app.services.fcm_service import notify_customer
        class_name = session.gym_class.name if session.gym_class else 'your class'
        for row in attendees:
            try:
                notified += notify_customer(
                    row.customer_id,
                    'How was your class?',
                    f'Tell us what you thought of {class_name}.',
                    {'type': 'class_feedback', 'session_id': str(session.id)},
                )
            except Exception:
                # A push failure must not roll back a finished class.
                pass

    return success_response({
        **session.to_dict(),
        'attendees': len(attendees),
        'feedback_requested': notified,
    }, 'Session closed')


# ─────────────────────────────── feedback ───────────────────────────────

@classes_bp.route('/sessions/<int:session_id>/feedback', methods=['GET'])
@jwt_required()
def session_feedback(session_id):
    """Feedback for one session.

    A trainer reaches only their own sessions (enforced in the loader), so this
    answers "my ratings" for them and "any trainer's ratings" for a manager.
    """
    session, err = _load_scoped_session(session_id)
    if err:
        return err

    rows = session.feedback.all()
    ratings = [r.rating for r in rows]
    return success_response({
        'session_id': session.id,
        'count': len(rows),
        'average_rating': round(sum(ratings) / len(ratings), 2) if ratings else None,
        'items': [r.to_dict() for r in rows],
    })


@classes_bp.route('/<int:class_id>/feedback', methods=['GET'])
@jwt_required()
def class_feedback(class_id):
    """Every rating a class has collected, newest session first."""
    user = get_current_user()
    gym_class, err = _load_scoped_class(class_id)
    if err:
        return err
    if user.role == UserRole.TRAINER and gym_class.trainer_id != user.id:
        return error_response('Class not found', 404)

    rows = (
        ClassFeedback.query
        .join(ClassSession, ClassFeedback.session_id == ClassSession.id)
        .filter(ClassSession.class_id == gym_class.id)
        .order_by(ClassFeedback.created_at.desc())
        .all()
    )
    ratings = [r.rating for r in rows]

    return success_response({
        'class_id': gym_class.id,
        'class_name': gym_class.name,
        'count': len(rows),
        'average_rating': round(sum(ratings) / len(ratings), 2) if ratings else None,
        'items': [r.to_dict() for r in rows],
    })
