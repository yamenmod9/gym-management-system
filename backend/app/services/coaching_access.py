"""Which members does a captain actually coach?

Both the message centre and body-measurement history hang off one question:
does this trainer have a live private-training relationship with this member?
It lives here rather than in either feature so that the two cannot drift into
answering it differently — a trainer blocked from the measurements of someone
they can still message would be a bug in whichever one is wrong, and there
would be no way to tell which.

The relationship is derived from the subscription every time it is asked. It is
never copied onto a message or a measurement: a permission stamped at write
time keeps granting access long after the member has stopped training with that
captain.
"""
from app.models.subscription import Subscription, SubscriptionStatus

#: A relationship counts while the subscription is live. FROZEN is included
#: deliberately: a member who has paused for a month is still that captain's
#: client, and cutting the conversation off mid-pause is precisely when they
#: most need to be able to ask a question.
COACHING_STATUSES = (SubscriptionStatus.ACTIVE, SubscriptionStatus.FROZEN)


def coaching_subscriptions(trainer_id):
    """Live private-training subscriptions naming this captain."""
    if trainer_id is None:
        return []
    return Subscription.query.filter(
        Subscription.trainer_id == trainer_id,
        Subscription.status.in_(COACHING_STATUSES),
    ).order_by(Subscription.end_date.desc()).all()


def trainer_has_client(trainer_id, customer_id):
    """May this trainer see and message this member?"""
    if trainer_id is None or customer_id is None:
        return False
    return db_exists(
        Subscription.query.filter(
            Subscription.trainer_id == trainer_id,
            Subscription.customer_id == customer_id,
            Subscription.status.in_(COACHING_STATUSES),
        )
    )


def coached_customer_ids(trainer_id):
    """Every member this captain currently coaches, as a set of ids.

    For list endpoints, where asking :func:`trainer_has_client` per row would
    be one query per member on the page.
    """
    if trainer_id is None:
        return set()
    from app.extensions import db
    rows = db.session.query(Subscription.customer_id).filter(
        Subscription.trainer_id == trainer_id,
        Subscription.status.in_(COACHING_STATUSES),
    ).distinct().all()
    return {row[0] for row in rows}


def has_ever_coached(trainer_id, customer_id):
    """Was there ever a private-training subscription between these two?

    Used only to decide whether a *past* conversation stays readable. Sending
    requires :func:`trainer_has_client`; reading what the two of them already
    said to each other does not, because the alternative is deleting a member's
    own conversation out from under them the day their package lapses.
    """
    if trainer_id is None or customer_id is None:
        return False
    return db_exists(
        Subscription.query.filter(
            Subscription.trainer_id == trainer_id,
            Subscription.customer_id == customer_id,
        )
    )


def coaches_of(customer_id):
    """The captains this member currently trains with."""
    if customer_id is None:
        return []
    subs = Subscription.query.filter(
        Subscription.customer_id == customer_id,
        Subscription.trainer_id.isnot(None),
        Subscription.status.in_(COACHING_STATUSES),
    ).all()

    # A member may hold two packages with the same captain; the conversation is
    # still one conversation.
    seen = {}
    for sub in subs:
        seen.setdefault(sub.trainer_id, sub)
    return list(seen.values())


def db_exists(query):
    """True if the query matches anything, without loading a row.

    ``query.first() is not None`` would fetch every column of a subscription to
    answer a yes/no asked on most requests in these two features.
    """
    from app.extensions import db
    return db.session.query(query.exists()).scalar()
