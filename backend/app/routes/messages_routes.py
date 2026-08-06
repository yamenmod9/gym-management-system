"""The message centre: a captain and the members who train privately with them.

Symmetric by design — the same thread, read and written from both ends, with
the trainer routes under /api/private-training and the member routes under
/api/client because that is how each app already authenticates.

Sending requires a live coaching relationship. Reading an existing thread does
not: when a member's package lapses, deleting the conversation out from under
both of them would be a worse answer than letting it go quiet.
"""
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func, or_

from app.extensions import db
from app.models.customer import Customer
from app.models.message import Message, MessageSender
from app.models.user import User, UserRole
from app.services.coaching_access import (
    coaches_of, coaching_subscriptions, has_ever_coached, trainer_has_client,
)
from app.utils import success_response, error_response, role_required, get_current_user
from app.utils.client_auth import client_token_required, get_current_client

messages_bp = Blueprint('messages', __name__, url_prefix='/api')


def _clean_body(data):
    """Validate a message body. Returns (body, error_response)."""
    body = (data.get('body') or '').strip()
    if not body:
        return None, error_response('Message body is required', 400)
    if len(body) > Message.MAX_BODY_LENGTH:
        return None, error_response(
            f'Message must be {Message.MAX_BODY_LENGTH} characters or fewer', 400)
    return body, None


def _thread_query(trainer_id, customer_id):
    return Message.query.filter(
        Message.trainer_id == trainer_id,
        Message.customer_id == customer_id,
    )


def _unread_counts(pairs, unread_from):
    """Unread totals for many threads in one query.

    ``pairs`` is a list of (trainer_id, customer_id). Counting per thread in a
    loop is a query per member on a captain's roster, on the screen they open
    most.
    """
    if not pairs:
        return {}

    conditions = [
        db.and_(Message.trainer_id == t, Message.customer_id == c)
        for t, c in pairs
    ]
    rows = db.session.query(
        Message.trainer_id, Message.customer_id, func.count(Message.id)
    ).filter(
        or_(*conditions),
        Message.sender == unread_from,
        Message.read_at.is_(None),
    ).group_by(Message.trainer_id, Message.customer_id).all()

    return {(t, c): n for t, c, n in rows}


def _last_messages(pairs):
    """The most recent message in each thread, as {(trainer, customer): Message}."""
    if not pairs:
        return {}

    conditions = [
        db.and_(Message.trainer_id == t, Message.customer_id == c)
        for t, c in pairs
    ]
    # Ordered oldest-first so the dict ends up holding the newest per thread.
    rows = Message.query.filter(or_(*conditions)).order_by(
        Message.created_at.asc()).all()

    latest = {}
    for message in rows:
        latest[(message.trainer_id, message.customer_id)] = message
    return latest


def _mark_read(trainer_id, customer_id, sender_to_mark):
    """Mark the other party's messages in this thread as read."""
    updated = _thread_query(trainer_id, customer_id).filter(
        Message.sender == sender_to_mark,
        Message.read_at.is_(None),
    ).update({'read_at': datetime.utcnow()}, synchronize_session=False)
    if updated:
        db.session.commit()
    return updated


def _serialise_thread_messages(trainer_id, customer_id, limit):
    rows = _thread_query(trainer_id, customer_id).order_by(
        Message.created_at.desc()).limit(limit).all()
    # Returned oldest-first: a chat reads downwards, and the newest-first order
    # above exists only so the limit takes the *recent* end of a long thread.
    return [m.to_dict() for m in reversed(rows)]


# ────────────────────────────── trainer ─────────────────────────────────

@messages_bp.route('/private-training/messages/threads', methods=['GET'])
@jwt_required()
@role_required(UserRole.TRAINER)
def trainer_threads():
    """One thread per member on this captain's roster.

    Members with no messages yet are included: the captain has to be able to
    start the conversation, and a list that only shows existing threads gives
    them nowhere to start it from.
    """
    trainer = get_current_user()
    subs = coaching_subscriptions(trainer.id)

    # A member holding two packages with the same captain is still one thread.
    by_customer = {}
    for sub in subs:
        by_customer.setdefault(sub.customer_id, sub)

    pairs = [(trainer.id, customer_id) for customer_id in by_customer]
    unread = _unread_counts(pairs, MessageSender.MEMBER)
    latest = _last_messages(pairs)

    threads = []
    for customer_id, sub in by_customer.items():
        last = latest.get((trainer.id, customer_id))
        threads.append({
            'customer_id': customer_id,
            'customer_name': sub.customer.full_name if sub.customer else None,
            'customer_phone': sub.customer.phone if sub.customer else None,
            'subscription_status': sub.status.value,
            'unread_count': unread.get((trainer.id, customer_id), 0),
            'last_message': last.to_dict() if last else None,
            'last_message_at': last.created_at.isoformat() if last else None,
        })

    # Most recently active first; never-messaged members fall to the bottom
    # rather than being scattered through the list by member id.
    threads.sort(key=lambda t: t['last_message_at'] or '', reverse=True)

    return success_response({
        'items': threads,
        'total_unread': sum(t['unread_count'] for t in threads),
    })


@messages_bp.route('/private-training/messages/<int:customer_id>', methods=['GET'])
@jwt_required()
@role_required(UserRole.TRAINER)
def trainer_read_thread(customer_id):
    trainer = get_current_user()
    if not has_ever_coached(trainer.id, customer_id):
        return error_response('Conversation not found', 404)

    limit = min(request.args.get('limit', 100, type=int), 200)
    messages = _serialise_thread_messages(trainer.id, customer_id, limit)
    _mark_read(trainer.id, customer_id, MessageSender.MEMBER)

    customer = db.session.get(Customer, customer_id)
    return success_response({
        'customer_id': customer_id,
        'customer_name': customer.full_name if customer else None,
        'items': messages,
        # False once the package lapses: the thread stays readable, but the
        # composer is closed rather than failing on send.
        'can_send': trainer_has_client(trainer.id, customer_id),
    })


@messages_bp.route('/private-training/messages/<int:customer_id>', methods=['POST'])
@jwt_required()
@role_required(UserRole.TRAINER)
def trainer_send(customer_id):
    trainer = get_current_user()
    if not trainer_has_client(trainer.id, customer_id):
        return error_response(
            'You can only message members who train privately with you', 403)

    body, failure = _clean_body(request.get_json() or {})
    if failure:
        return failure

    customer = db.session.get(Customer, customer_id)
    message = Message(
        trainer_id=trainer.id,
        customer_id=customer_id,
        sender=MessageSender.TRAINER,
        body=body,
        branch_id=customer.branch_id if customer else None,
    )
    db.session.add(message)
    db.session.commit()

    _notify(
        to_customer=customer_id,
        title=trainer.full_name,
        body=body,
        data={'type': 'message', 'trainer_id': str(trainer.id)},
    )

    return success_response(message.to_dict(), 'Message sent', 201)


# ────────────────────────────── member ──────────────────────────────────

@messages_bp.route('/client/messages/threads', methods=['GET'])
@client_token_required
def client_threads():
    """The captains this member currently trains with."""
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    subs = coaches_of(customer.id)
    pairs = [(sub.trainer_id, customer.id) for sub in subs]
    unread = _unread_counts(pairs, MessageSender.TRAINER)
    latest = _last_messages(pairs)

    threads = []
    for sub in subs:
        trainer = db.session.get(User, sub.trainer_id)
        last = latest.get((sub.trainer_id, customer.id))
        threads.append({
            'trainer_id': sub.trainer_id,
            'trainer_name': trainer.full_name if trainer else None,
            'service_name': sub.service.name if sub.service else None,
            'unread_count': unread.get((sub.trainer_id, customer.id), 0),
            'last_message': last.to_dict() if last else None,
            'last_message_at': last.created_at.isoformat() if last else None,
        })

    threads.sort(key=lambda t: t['last_message_at'] or '', reverse=True)

    return success_response({
        'items': threads,
        'total_unread': sum(t['unread_count'] for t in threads),
    })


@messages_bp.route('/client/messages/<int:trainer_id>', methods=['GET'])
@client_token_required
def client_read_thread(trainer_id):
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)
    if not has_ever_coached(trainer_id, customer.id):
        return error_response('Conversation not found', 404)

    limit = min(request.args.get('limit', 100, type=int), 200)
    messages = _serialise_thread_messages(trainer_id, customer.id, limit)
    _mark_read(trainer_id, customer.id, MessageSender.TRAINER)

    trainer = db.session.get(User, trainer_id)
    return success_response({
        'trainer_id': trainer_id,
        'trainer_name': trainer.full_name if trainer else None,
        'items': messages,
        'can_send': trainer_has_client(trainer_id, customer.id),
    })


@messages_bp.route('/client/messages/<int:trainer_id>', methods=['POST'])
@client_token_required
def client_send(trainer_id):
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)
    if not trainer_has_client(trainer_id, customer.id):
        return error_response(
            'You can only message a captain you train with', 403)

    body, failure = _clean_body(request.get_json() or {})
    if failure:
        return failure

    message = Message(
        trainer_id=trainer_id,
        customer_id=customer.id,
        sender=MessageSender.MEMBER,
        body=body,
        branch_id=customer.branch_id,
    )
    db.session.add(message)
    db.session.commit()

    _notify(
        to_user=trainer_id,
        title=customer.full_name,
        body=body,
        data={'type': 'message', 'customer_id': str(customer.id)},
    )

    return success_response(message.to_dict(), 'Message sent', 201)


def _notify(title, body, data, to_customer=None, to_user=None):
    """Push the message to the other party's device, if they have one.

    Never allowed to fail the send: the message is already committed, and a
    delivery problem must not turn a saved message into an error the sender
    will retry.
    """
    try:
        from app.services import fcm_service

        preview = body if len(body) <= 120 else body[:117] + '...'
        if to_customer is not None:
            fcm_service.notify_customer(to_customer, title, preview, data)
        elif to_user is not None:
            fcm_service.notify_user(to_user, title, preview, data)
    except Exception:
        from flask import current_app
        current_app.logger.warning('Message push notification failed', exc_info=True)
