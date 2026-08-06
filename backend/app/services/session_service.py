"""Ending sessions that should no longer work.

Logging out did nothing. ``/api/auth/logout`` and ``/api/client/auth/logout``
both returned "Logged out successfully" and left the token entirely valid — up
to 12 hours for staff and 7 days for a member. The same was true of changing a
password: the thief who already had a session kept it.

Deactivating an account *is* enforced per-request (see
``register_active_account_guard``), so firing someone locks them out
immediately. What was left was the lost phone, the shared front-desk PC, and
the password changed precisely because someone else knew the old one.

The mechanism is a per-account cutoff rather than a table of revoked token ids:

* It costs no extra query. The guard already reads ``is_active`` as a scalar on
  every request; this rides along in the same SELECT.
* It needs no cleanup job. A blocklist of jtis grows forever and has to be
  swept; one timestamp per account never grows.
* It revokes the refresh token too. A jti blocklist only knows about the token
  it was handed — ``/logout`` receives the access token, so the refresh token
  would have survived and could mint a fresh access token seconds later.

The cost is that it is all-or-nothing per account: you cannot sign out one
device and leave another signed in. For a gym's staff terminals and a member's
single phone, "sign out everywhere" is the behaviour you want anyway — it is
what makes the button useful when the phone is the thing you have lost.
"""
from datetime import datetime

from app.extensions import db


def _cutoff_now():
    """The revocation cutoff, floored to a whole second.

    A JWT's ``iat`` is integer seconds, so a token minted at 10:00:00.9 records
    10:00:00. Storing an un-floored cutoff of 10:00:00.4 from a logout would
    then reject a token issued *after* it, in the same second — log out, log
    straight back in, and the new session is dead on arrival.

    Flooring makes the comparison consistent with the resolution of the value
    it is compared against. The residual window is under a second, and closing
    it would need the password anyway.
    """
    return datetime.utcnow().replace(microsecond=0)


def revoke_sessions(account):
    """Invalidate every token issued to this user or customer so far.

    Takes either a ``User`` or a ``Customer`` — both carry the column. Does not
    commit; the caller decides the transaction boundary.
    """
    account.sessions_valid_from = _cutoff_now()
    return account.sessions_valid_from


def revoke_sessions_and_commit(account):
    cutoff = revoke_sessions(account)
    db.session.commit()
    return cutoff


def token_is_revoked(issued_at, sessions_valid_from):
    """Was this token issued before its account's revocation cutoff?

    ``issued_at`` is the raw ``iat`` claim (integer epoch seconds), and
    ``sessions_valid_from`` the stored naive-UTC cutoff. Accounts that have
    never revoked anything carry NULL and are always current, which is what
    makes this safe to add to a live system: every existing session keeps
    working until its owner does something that ends it.
    """
    if sessions_valid_from is None or issued_at is None:
        return False

    try:
        issued = datetime.utcfromtimestamp(int(issued_at))
    except (TypeError, ValueError, OSError, OverflowError):
        # An unparseable iat is not a licence to ignore a revocation, but it is
        # also not proof of one. Treat the token as current and leave the
        # decision to the signature check that already passed.
        return False

    return issued < sessions_valid_from
