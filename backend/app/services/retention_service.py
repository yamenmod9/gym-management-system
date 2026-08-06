"""Carrying out account deletion requests.

A member asks to be deleted, a 90-day grace period runs, and then the account
has to actually go. Two things were wrong with how that worked:

* It only happened if the member came back. The purge was triggered from the
  member's own login and profile read, and someone who has asked to be deleted
  is precisely the person who does not log in again — so their data stayed
  indefinitely.
* "Deleted" meant ``is_active = False``. Name, phone, email, national id,
  address and health notes all remained on the row.

This module does the erasure, and :func:`purge_due_accounts` is safe to call
from anywhere — a CLI command, a boot hook, or the opportunistic sweep in the
request guard — because it is idempotent and only ever touches rows whose
grace period has already elapsed.

The customer row itself is kept. Transactions, entry logs and subscriptions
reference it, and deleting it would either cascade away a gym's financial
history or leave dangling references. Emptying it of personal data is the
erasure; the skeleton that remains identifies nobody.
"""
from datetime import datetime, timedelta

from app.extensions import db

#: Marker written into health_notes when a deletion is requested.
DELETE_REQUEST_PREFIX = '[DELETE_REQUEST]'

#: How long a member has to change their mind.
GRACE_DAYS = 90


def _requested_at(customer):
    """When deletion was requested, or None."""
    for line in (customer.health_notes or '').splitlines():
        if line.startswith(DELETE_REQUEST_PREFIX):
            stamp = line[len(DELETE_REQUEST_PREFIX):].strip()
            try:
                return datetime.fromisoformat(stamp)
            except ValueError:
                return None
    return None


def is_due(customer, now=None):
    """Has this member's grace period elapsed?"""
    requested = _requested_at(customer)
    if requested is None:
        return False
    return (now or datetime.utcnow()) >= requested + timedelta(days=GRACE_DAYS)


def anonymise(customer):
    """Strip every piece of personal data from a member record.

    Deliberately overwrites rather than nulls the fields that carry a NOT NULL
    or a uniqueness constraint — a phone number has to stay unique, so it
    becomes a per-id placeholder instead of NULL, which would collide the
    moment a second account was deleted.
    """
    marker = f'deleted-{customer.id}'

    customer.full_name = 'Deleted member'
    customer.phone = marker
    customer.email = None
    customer.national_id = None
    customer.address = None
    customer.date_of_birth = None
    customer.gender = None
    customer.health_notes = None
    customer.qr_code = None

    # Body measurements are health data and identify a person as readily as a
    # name does when paired with a branch and a join date.
    customer.height = None
    customer.weight = None
    customer.bmi = None
    customer.bmi_category = None
    customer.bmr = None
    customer.ideal_weight = None
    customer.daily_calories = None

    # The login must stop working, not merely be refused.
    customer.password_hash = None
    customer.temp_password = None
    customer.password_changed = True

    customer.is_active = False

    # And any token already in the wild must stop working now, rather than
    # continuing to authenticate a member who no longer exists. Deactivation
    # alone covers this today, but the two are independent switches and an
    # erased account should not depend on the other one staying set.
    from app.services.session_service import revoke_sessions
    revoke_sessions(customer)

    # Any device still holding a push token for them must stop receiving.
    from app.models.device_token import DeviceToken
    DeviceToken.query.filter_by(customer_id=customer.id).update(
        {'is_active': False}, synchronize_session=False)

    # And their biometrics are personal data in their own right.
    from app.models.fingerprint import Fingerprint
    for fingerprint in Fingerprint.query.filter_by(customer_id=customer.id).all():
        fingerprint.is_active = False
        fingerprint.fingerprint_hash = f'purged-{fingerprint.id}'
        fingerprint.template_hash = f'purged-{fingerprint.id}'
        fingerprint.deactivation_reason = 'Account deleted'


def purge_due_accounts(now=None, limit=200):
    """Erase every account whose grace period has elapsed.

    Returns the number erased. Bounded by ``limit`` so an opportunistic caller
    on a request path can never turn into a long transaction.
    """
    from app.models.customer import Customer

    now = now or datetime.utcnow()
    cutoff = now - timedelta(days=GRACE_DAYS)

    # Narrow in SQL to rows that carry the marker at all; the exact timestamp
    # is parsed per row because it lives inside a text field.
    candidates = Customer.query.filter(
        Customer.health_notes.like(f'%{DELETE_REQUEST_PREFIX}%')
    ).limit(limit).all()

    purged = 0
    for customer in candidates:
        requested = _requested_at(customer)
        if requested is None or requested > cutoff:
            continue
        anonymise(customer)
        purged += 1

    if purged:
        db.session.commit()
    return purged
