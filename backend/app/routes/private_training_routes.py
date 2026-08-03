"""
Private training — a captain's roster, the sessions they log, and the dispute
path when a member says a session never happened.
"""
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import (
    Customer, PrivateSession, PrivateSessionStatus, Subscription,
    SubscriptionStatus, Service,
)
from app.models.private_session import AUTO_CONFIRM_AFTER
from app.models.user import UserRole
from app.utils import (
    success_response, error_response, role_required, get_current_user,
    get_accessible_branch_ids,
)
from app.utils.client_auth import client_token_required, get_current_client
from app.extensions import db

private_bp = Blueprint('private_training', __name__, url_prefix='/api/private-training')

#: Who settles a disputed session.
ADJUDICATOR_ROLES = (
    UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.BRANCH_MANAGER,
)


def _trainer_subscriptions(trainer_id):
    """Active private-training subscriptions naming this captain."""
    return Subscription.query.filter(
        Subscription.trainer_id == trainer_id,
        Subscription.status.in_(
            [SubscriptionStatus.ACTIVE, SubscriptionStatus.FROZEN]
        ),
    ).order_by(Subscription.end_date.desc()).all()


# ─────────────────────────────── trainer ────────────────────────────────

@private_bp.route('/clients', methods=['GET'])
@jwt_required()
@role_required(UserRole.TRAINER)
def my_private_clients():
    """The members who train privately with this captain."""
    user = get_current_user()
    subs = _trainer_subscriptions(user.id)

    # Only sessions still inside the confirmation window count as awaiting an
    # answer. Past it they are treated as agreed everywhere else (see
    # PrivateSession.effective_status), and counting them here would leave the
    # captain staring at a badge that only ever climbs.
    still_open_after = datetime.utcnow() - AUTO_CONFIRM_AFTER

    pending_by_sub = {}
    for s in PrivateSession.query.filter(
        PrivateSession.trainer_id == user.id,
        PrivateSession.status == PrivateSessionStatus.PENDING,
        PrivateSession.logged_at > still_open_after,
    ).all():
        pending_by_sub.setdefault(s.subscription_id, 0)
        pending_by_sub[s.subscription_id] += 1

    payload = []
    for sub in subs:
        payload.append({
            'subscription_id': sub.id,
            'customer_id': sub.customer_id,
            'customer_name': sub.customer.full_name if sub.customer else None,
            'customer_phone': sub.customer.phone if sub.customer else None,
            'service_name': sub.service.name if sub.service else None,
            'status': sub.status.value,
            'start_date': sub.start_date.isoformat(),
            'end_date': sub.end_date.isoformat(),
            'remaining_sessions': sub.remaining_sessions,
            'total_sessions': sub.total_sessions,
            'awaiting_confirmation': pending_by_sub.get(sub.id, 0),
        })
    return success_response(payload)


@private_bp.route('/sessions', methods=['POST'])
@jwt_required()
@role_required(UserRole.TRAINER)
def log_session():
    """Record a session just delivered, and ask the member to confirm it.

    The session is deducted now rather than on confirmation: the member's
    remaining balance should reflect training they have actually had. If they
    dispute it and a manager agrees, the deduction is reversed.
    """
    user = get_current_user()
    data = request.json or {}

    subscription_id = data.get('subscription_id')
    if not subscription_id:
        return error_response('subscription_id is required', 400)

    sub = db.session.get(Subscription, subscription_id)
    if not sub or sub.trainer_id != user.id:
        return error_response('Subscription not found', 404)
    if sub.status != SubscriptionStatus.ACTIVE:
        return error_response(f'Subscription is {sub.status.value}', 400)

    if sub.remaining_sessions is not None and sub.remaining_sessions <= 0:
        return error_response('No sessions remaining on this package', 400)

    session = PrivateSession(
        subscription_id=sub.id,
        customer_id=sub.customer_id,
        trainer_id=user.id,
        branch_id=sub.branch_id,
        notes=(data.get('notes') or None),
    )
    if sub.remaining_sessions is not None:
        sub.remaining_sessions -= 1

    db.session.add(session)
    db.session.commit()

    try:
        from app.services.fcm_service import notify_customer
        notify_customer(
            sub.customer_id,
            'Confirm your training session',
            f'{user.full_name} logged a session with you. Confirm it, or let us know if it did not happen.',
            {'type': 'private_session_confirm', 'session_id': str(session.id)},
        )
    except Exception:
        pass  # never fail the log because a push could not be delivered

    return success_response(session.to_dict(), 'Session logged', 201)


@private_bp.route('/sessions', methods=['GET'])
@jwt_required()
@role_required(UserRole.TRAINER)
def my_logged_sessions():
    """Sessions this captain has logged, newest first."""
    user = get_current_user()
    rows = PrivateSession.query.filter_by(trainer_id=user.id).order_by(
        PrivateSession.logged_at.desc()
    ).limit(100).all()
    return success_response([r.to_dict() for r in rows])


# ──────────────────────────────── client ────────────────────────────────

@private_bp.route('/client/pending', methods=['GET'])
@client_token_required
def client_pending_sessions():
    """Sessions awaiting this member's confirmation."""
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    rows = PrivateSession.query.filter(
        PrivateSession.customer_id == customer.id,
        PrivateSession.status == PrivateSessionStatus.PENDING,
    ).order_by(PrivateSession.logged_at.desc()).all()

    # Past the window it counts as agreed, so stop nagging about it.
    return success_response([r.to_dict() for r in rows if not r.is_auto_confirmed])


def _load_client_session(session_id, customer):
    session = db.session.get(PrivateSession, session_id)
    if not session or session.customer_id != customer.id:
        return None, error_response('Session not found', 404)
    if session.status != PrivateSessionStatus.PENDING:
        return None, error_response(
            f'This session is already {session.status.value}', 400
        )
    if session.is_auto_confirmed:
        return None, error_response(
            'The confirmation window for this session has closed', 400
        )
    return session, None


@private_bp.route('/client/sessions/<int:session_id>/confirm', methods=['POST'])
@client_token_required
def client_confirm_session(session_id):
    """Member agrees the session happened."""
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    session, err = _load_client_session(session_id, customer)
    if err:
        return err

    session.status = PrivateSessionStatus.CONFIRMED
    session.answered_at = datetime.utcnow()
    db.session.commit()
    return success_response(session.to_dict(), 'Session confirmed')


@private_bp.route('/client/sessions/<int:session_id>/dispute', methods=['POST'])
@client_token_required
def client_dispute_session(session_id):
    """Member says the session did not happen; a manager will decide."""
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    session, err = _load_client_session(session_id, customer)
    if err:
        return err

    reason = ((request.json or {}).get('reason') or '').strip()
    if len(reason) < 5:
        return error_response('Please say briefly what went wrong (5 characters minimum)', 400)

    session.status = PrivateSessionStatus.DISPUTED
    session.dispute_reason = reason
    session.answered_at = datetime.utcnow()
    db.session.commit()

    # Tell the managers who can actually settle it.
    try:
        from app.services.fcm_service import notify_role
        branch = session.subscription.branch if session.subscription else None
        gym_id = branch.gym_id if branch else None
        for role in (UserRole.BRANCH_MANAGER, UserRole.OWNER):
            notify_role(
                role.value,
                'Training session disputed',
                f'{customer.full_name} disputed a session logged by '
                f'{session.trainer.full_name if session.trainer else "a trainer"}.',
                {'type': 'private_session_dispute', 'session_id': str(session.id)},
                gym_id=gym_id,
            )
    except Exception:
        pass

    return success_response(session.to_dict(), 'Session disputed — a manager will review it')


# ─────────────────────────────── manager ────────────────────────────────

@private_bp.route('/disputes', methods=['GET'])
@jwt_required()
@role_required(*ADJUDICATOR_ROLES)
def list_disputes():
    """Disputed sessions awaiting a ruling, within the caller's branches."""
    user = get_current_user()
    query = PrivateSession.query.filter(
        PrivateSession.status == PrivateSessionStatus.DISPUTED
    )
    accessible = get_accessible_branch_ids(user)
    if accessible is not None:
        query = query.filter(PrivateSession.branch_id.in_(accessible))

    rows = query.order_by(PrivateSession.answered_at.desc()).all()
    return success_response([r.to_dict() for r in rows])


@private_bp.route('/disputes/<int:session_id>/resolve', methods=['POST'])
@jwt_required()
@role_required(*ADJUDICATOR_ROLES)
def resolve_dispute(session_id):
    """Settle a dispute.

    ``uphold`` — the session stands and stays deducted.
    ``refund`` — the member was right; the session is credited back.
    """
    user = get_current_user()
    session = db.session.get(PrivateSession, session_id)
    if not session:
        return error_response('Session not found', 404)

    accessible = get_accessible_branch_ids(user)
    if accessible is not None and session.branch_id not in accessible:
        return error_response('Session not found', 404)

    if session.status != PrivateSessionStatus.DISPUTED:
        return error_response('That session is not under dispute', 400)

    data = request.json or {}
    decision = (data.get('decision') or '').strip().lower()
    if decision not in ('uphold', 'refund'):
        return error_response("decision must be 'uphold' or 'refund'", 400)

    if decision == 'refund':
        session.status = PrivateSessionStatus.REVERSED
        sub = session.subscription
        if sub is not None and sub.remaining_sessions is not None:
            sub.remaining_sessions += 1
    else:
        session.status = PrivateSessionStatus.CONFIRMED

    session.resolved_by_user_id = user.id
    session.resolved_at = datetime.utcnow()
    session.resolution_note = (data.get('note') or None)
    db.session.commit()

    try:
        from app.services.fcm_service import notify_customer, notify_user
        outcome = (
            'Your session was credited back.' if decision == 'refund'
            else 'The session was confirmed as delivered.'
        )
        notify_customer(
            session.customer_id, 'Your dispute was reviewed', outcome,
            {'type': 'private_session_resolved', 'session_id': str(session.id)},
        )
        notify_user(
            session.trainer_id, 'Disputed session reviewed', outcome,
            {'type': 'private_session_resolved', 'session_id': str(session.id)},
        )
    except Exception:
        pass

    return success_response(session.to_dict(), f'Dispute resolved ({decision})')
