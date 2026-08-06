"""Signing out for real, and getting back in after forgetting a password.

Two gaps this pins:

* ``/logout`` returned "Logged out successfully" and did nothing. The token
  stayed valid for its full life — 12 hours for staff, 7 days for a member.
* A member who forgot their password had no route back into the app at all.
  ``/change-password`` requires the current one, and nothing else set a
  password after registration.

Run with:  pytest backend/tests/test_sessions_and_reset.py
"""
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='module')
def app():
    os.environ['DATABASE_URL'] = (
        'sqlite:///' + tempfile.mktemp(suffix='.db').replace(os.sep, '/')
    )
    from app import create_app
    from app.extensions import db

    application = create_app('testing')
    with application.app_context():
        db.create_all()
        _seed()
    return application


def _seed():
    from app.extensions import db
    from app.models.branch import Branch
    from app.models.customer import Customer
    from app.models.gym import Gym
    from app.models.user import User, UserRole

    ids = {}

    owner = User(username='sess_owner', email='sess_owner@example.com',
                 full_name='Session Owner', role=UserRole.OWNER, is_active=True)
    owner.set_password('secret123')
    db.session.add(owner)
    db.session.flush()

    gym = Gym(name='Session Gym', owner_id=owner.id, is_setup_complete=True)
    db.session.add(gym)
    db.session.flush()
    owner.gym_id = gym.id

    branch = Branch(name='Session Branch', code='SESS', gym_id=gym.id, is_active=True)
    other_branch = Branch(name='Far Branch', code='FAR', gym_id=gym.id, is_active=True)
    db.session.add_all([branch, other_branch])
    db.session.flush()
    owner.branch_id = branch.id

    desk = User(username='sess_desk', email='sess_desk@example.com',
                full_name='Front Desk', role=UserRole.FRONT_DESK,
                gym_id=gym.id, branch_id=branch.id, is_active=True)
    desk.set_password('secret123')

    trainer = User(username='sess_trainer', email='sess_trainer@example.com',
                   full_name='Captain', role=UserRole.TRAINER,
                   gym_id=gym.id, branch_id=branch.id, is_active=True)
    trainer.set_password('secret123')
    db.session.add_all([desk, trainer])
    db.session.flush()

    member = Customer(full_name='Forgetful Member', phone='01555000111',
                      email='forgetful@example.com', branch_id=branch.id,
                      is_active=True)
    member.set_password('oldpassword1')
    db.session.add(member)

    elsewhere = Customer(full_name='Other Branch Member', phone='01555000222',
                         branch_id=other_branch.id, is_active=True)
    elsewhere.set_password('oldpassword1')
    db.session.add(elsewhere)
    db.session.flush()

    ids.update(gym=gym.id, branch=branch.id, other_branch=other_branch.id,
               owner=owner.id, desk=desk.id, trainer=trainer.id,
               member=member.id, elsewhere=elsewhere.id)

    db.session.commit()
    globals()['IDS'] = ids


def _staff_token(app, username, password='secret123'):
    response = app.test_client().post(
        '/api/auth/login', json={'username': username, 'password': password})
    assert response.status_code == 200, response.get_json()
    return response.get_json()['data']['access_token']


def _headers(token):
    return {'Authorization': f'Bearer {token}'}


def _member_token(app, phone='01555000111', password='oldpassword1'):
    response = app.test_client().post(
        '/api/client/auth/login', json={'phone': phone, 'password': password})
    assert response.status_code == 200, response.get_json()
    return response.get_json()['data']['access_token']


# ──────────────────────────── signing out ───────────────────────────────────

def test_logging_out_actually_ends_the_session(app):
    """The end-to-end proof, and the reason for the one sleep in this file.

    A JWT's ``iat`` has one-second resolution, so a token minted and revoked
    inside the same second is indistinguishable from one minted just after the
    revocation. The cutoff resolves that ambiguity in favour of the *newer*
    token, so that logging out and straight back in does not hand you a dead
    session (see test below). Proving the real mechanism therefore needs the
    logout to land in a later second than the login.
    """
    client = app.test_client()
    token = _staff_token(app, 'sess_owner')

    assert client.get('/api/auth/me', headers=_headers(token)).status_code == 200

    time.sleep(1.05)
    assert client.post('/api/auth/logout',
                       headers=_headers(token)).status_code == 200

    after = client.get('/api/auth/me', headers=_headers(token))
    assert after.status_code == 401, (
        'the token still worked after logging out — logout was a no-op'
    )


def test_logging_straight_back_in_gives_a_working_session(app):
    """The regression the flooring exists to prevent: a fresh login must not
    be killed by the revocation that just happened."""
    client = app.test_client()
    _staff_token(app, 'sess_desk')
    client.post('/api/auth/logout', headers=_headers(_staff_token(app, 'sess_desk')))

    fresh = _staff_token(app, 'sess_desk')
    assert client.get('/api/auth/me',
                      headers=_headers(fresh)).status_code == 200


def test_a_members_logout_ends_their_session_too(app):
    client = app.test_client()
    token = _member_token(app)

    assert client.get('/api/client/me',
                      headers=_headers(token)).status_code == 200

    time.sleep(1.05)
    assert client.post('/api/client/auth/logout',
                       headers=_headers(token)).status_code == 200

    after = client.get('/api/client/me', headers=_headers(token))
    assert after.status_code == 401, "the member's token outlived their logout"


def test_logging_out_needs_a_token(app):
    """It has an effect now, so it cannot be anonymous: otherwise anyone could
    sign any member out."""
    assert app.test_client().post('/api/client/auth/logout').status_code == 401


def test_changing_a_password_evicts_other_devices_but_not_this_one(app):
    """Someone changing their password may be doing it because another person
    knows the old one. That person's session has to go."""
    client = app.test_client()

    stolen = _staff_token(app, 'sess_trainer')
    time.sleep(1.05)
    changing_from = _staff_token(app, 'sess_trainer')

    response = client.post(
        '/api/auth/change-password',
        json={'old_password': 'secret123', 'new_password': 'brandnew123'},
        headers=_headers(changing_from))
    assert response.status_code == 200, response.get_json()

    assert client.get('/api/auth/me',
                      headers=_headers(stolen)).status_code == 401, (
        'the other session survived the password change'
    )

    replacement = response.get_json()['data']['access_token']
    assert client.get('/api/auth/me',
                      headers=_headers(replacement)).status_code == 200, (
        'the person who changed their own password was signed out by it'
    )

    # Leave the fixture as we found it.
    client.post('/api/auth/change-password',
                json={'old_password': 'brandnew123', 'new_password': 'secret123'},
                headers=_headers(replacement))


def test_a_token_predating_the_cutoff_is_refused(app):
    """The guard's half of the mechanism, without the clock."""
    from app.extensions import db
    from app.models.user import User

    client = app.test_client()
    token = _staff_token(app, 'sess_owner')

    with app.app_context():
        user = db.session.get(User, IDS['owner'])
        user.sessions_valid_from = datetime.utcnow() + timedelta(seconds=30)
        db.session.commit()

    assert client.get('/api/auth/me', headers=_headers(token)).status_code == 401

    with app.app_context():
        user = db.session.get(User, IDS['owner'])
        user.sessions_valid_from = None
        db.session.commit()

    assert client.get('/api/auth/me', headers=_headers(token)).status_code == 200, (
        'an account that has never revoked anything must accept its tokens'
    )


def test_erasing_an_account_ends_its_sessions(app):
    from app.extensions import db
    from app.models.customer import Customer
    from app.services.retention_service import anonymise

    with app.app_context():
        member = db.session.get(Customer, IDS['elsewhere'])
        assert member.sessions_valid_from is None
        anonymise(member)
        db.session.commit()
        assert db.session.get(
            Customer, IDS['elsewhere']).sessions_valid_from is not None


# ───────────────────────── reception-issued reset ───────────────────────────

def test_reception_can_put_a_locked_out_member_back_in(app):
    """The path that works with no SMS or email provider configured, because
    the member is standing at the desk."""
    client = app.test_client()
    desk = _staff_token(app, 'sess_desk')

    response = client.post(f"/api/customers/{IDS['member']}/reset-password",
                           headers=_headers(desk))
    assert response.status_code == 200, response.get_json()

    issued = response.get_json()['data']['temporary_password']
    assert issued

    login = client.post('/api/client/auth/login',
                        json={'phone': '01555000111', 'password': issued})
    assert login.status_code == 200, login.get_json()
    assert login.get_json()['data']['password_changed'] is False, (
        'the member should be asked to set their own password'
    )


def test_issuing_a_new_password_ends_the_old_sessions(app):
    client = app.test_client()
    from app.extensions import db
    from app.models.customer import Customer

    with app.app_context():
        member = db.session.get(Customer, IDS['member'])
        member.set_password('knownpassword1')
        member.sessions_valid_from = None
        db.session.commit()

    token = _member_token(app, password='knownpassword1')
    assert client.get('/api/client/me',
                      headers=_headers(token)).status_code == 200

    time.sleep(1.05)
    assert client.post(f"/api/customers/{IDS['member']}/reset-password",
                       headers=_headers(_staff_token(app, 'sess_desk'))
                       ).status_code == 200

    assert client.get('/api/client/me',
                      headers=_headers(token)).status_code == 401, (
        'whoever was signed in on the old password kept their session'
    )


def test_a_trainer_cannot_issue_a_members_password(app):
    """It is a live credential for that member's account — a role with no
    reason to hand out credentials must not be able to mint one and sign in
    as them."""
    response = app.test_client().post(
        f"/api/customers/{IDS['member']}/reset-password",
        headers=_headers(_staff_token(app, 'sess_trainer')))
    assert response.status_code == 403, response.get_json()


def test_reception_cannot_reset_a_member_of_another_branch(app):
    from app.extensions import db
    from app.models.customer import Customer

    with app.app_context():
        # Undo the erasure from the retention test so this asserts scope, not
        # a deactivated account.
        member = db.session.get(Customer, IDS['elsewhere'])
        member.is_active = True
        db.session.commit()

    response = app.test_client().post(
        f"/api/customers/{IDS['elsewhere']}/reset-password",
        headers=_headers(_staff_token(app, 'sess_desk')))
    assert response.status_code == 403, response.get_json()


# ─────────────────────────── self-serve reset ───────────────────────────────

class _RecordingProvider:
    """A provider that delivers, and remembers what it delivered."""

    delivers = True

    def __init__(self):
        self.sent = []

    def supports(self, delivery_method):
        return delivery_method in ('sms', 'email')

    def send_sms(self, phone, message):
        self.sent.append(('sms', phone, message))
        return True

    def send_email(self, email, subject, body):
        self.sent.append(('email', email, body))
        return True


@pytest.fixture
def provider():
    from app.services.notification_service import get_notification_service

    service = get_notification_service()
    original = service.provider
    recording = _RecordingProvider()
    service.set_provider(recording)
    yield recording
    service.set_provider(original)


def _code_from(provider):
    """Pull the 6-digit code out of the message that was 'delivered'."""
    import re

    assert provider.sent, 'nothing was sent'
    body = provider.sent[-1][2]
    match = re.search(r'\b(\d{6})\b', body)
    assert match, f'no code found in delivered message: {body!r}'
    return match.group(1)


def test_without_a_provider_the_member_is_told_the_truth(app):
    """The console provider reports that it cannot deliver, so the endpoint
    says so rather than promising a code that will never arrive — which is
    exactly what the old code-login path did in production."""
    response = app.test_client().post(
        '/api/client/auth/forgot-password',
        json={'identifier': '01555000111'})

    assert response.status_code == 503, response.get_json()
    assert 'reception' in response.get_json()['error'].lower()


def test_a_member_can_reset_their_own_password_with_a_code(app, provider):
    client = app.test_client()

    from app.extensions import db
    from app.models.customer import Customer
    with app.app_context():
        member = db.session.get(Customer, IDS['member'])
        member.set_password('oldpassword1')
        db.session.commit()

    requested = client.post('/api/client/auth/forgot-password',
                            json={'identifier': '01555000111'})
    assert requested.status_code == 200, requested.get_json()

    code = _code_from(provider)

    reset = client.post('/api/client/auth/reset-password',
                        json={'identifier': '01555000111', 'code': code,
                              'new_password': 'freshpassword1'})
    assert reset.status_code == 200, reset.get_json()

    assert client.post('/api/client/auth/login',
                       json={'phone': '01555000111',
                             'password': 'freshpassword1'}).status_code == 200
    assert client.post('/api/client/auth/login',
                       json={'phone': '01555000111',
                             'password': 'oldpassword1'}).status_code == 401


def test_a_reset_code_cannot_be_used_to_log_in(app, provider):
    """Otherwise "I forgot my password" becomes a second, quieter way in —
    one whose delivery assumptions are weaker than the login path's."""
    client = app.test_client()

    client.post('/api/client/auth/forgot-password',
                json={'identifier': '01555000111'})
    code = _code_from(provider)

    response = client.post('/api/client/auth/verify-code',
                           json={'identifier': '01555000111', 'code': code})
    assert response.status_code == 401, response.get_json()


def test_resetting_a_password_ends_existing_sessions(app, provider):
    client = app.test_client()

    from app.extensions import db
    from app.models.customer import Customer
    with app.app_context():
        member = db.session.get(Customer, IDS['member'])
        member.set_password('knownpassword1')
        member.sessions_valid_from = None
        db.session.commit()

    token = _member_token(app, password='knownpassword1')
    assert client.get('/api/client/me',
                      headers=_headers(token)).status_code == 200

    time.sleep(1.05)
    client.post('/api/client/auth/forgot-password',
                json={'identifier': '01555000111'})
    code = _code_from(provider)
    assert client.post('/api/client/auth/reset-password',
                       json={'identifier': '01555000111', 'code': code,
                             'new_password': 'anotherpassword1'}
                       ).status_code == 200

    assert client.get('/api/client/me',
                      headers=_headers(token)).status_code == 401


def test_a_wrong_code_does_not_reset_anything(app, provider):
    client = app.test_client()

    client.post('/api/client/auth/forgot-password',
                json={'identifier': '01555000111'})

    response = client.post('/api/client/auth/reset-password',
                           json={'identifier': '01555000111', 'code': '000000',
                                 'new_password': 'attackerpassword1'})
    assert response.status_code == 401, response.get_json()

    assert client.post('/api/client/auth/login',
                       json={'phone': '01555000111',
                             'password': 'attackerpassword1'}).status_code == 401


def test_an_unknown_member_gets_the_same_answer_as_a_real_one(app, provider):
    """Otherwise the endpoint tells anyone who asks which phone numbers belong
    to members of this gym."""
    client = app.test_client()

    real = client.post('/api/client/auth/forgot-password',
                       json={'identifier': '01555000111'})
    unknown = client.post('/api/client/auth/forgot-password',
                          json={'identifier': '01999888777'})

    assert real.status_code == unknown.status_code == 200
    assert (real.get_json()['data']['message']
            == unknown.get_json()['data']['message'])

    invalid_real = client.post(
        '/api/client/auth/reset-password',
        json={'identifier': '01555000111', 'code': '123456',
              'new_password': 'somepassword1'})
    invalid_unknown = client.post(
        '/api/client/auth/reset-password',
        json={'identifier': '01999888777', 'code': '123456',
              'new_password': 'somepassword1'})

    assert invalid_real.status_code == invalid_unknown.status_code == 401
    assert invalid_real.get_json()['error'] == invalid_unknown.get_json()['error']


def test_a_short_password_is_refused(app, provider):
    client = app.test_client()

    client.post('/api/client/auth/forgot-password',
                json={'identifier': '01555000111'})
    code = _code_from(provider)

    response = client.post('/api/client/auth/reset-password',
                           json={'identifier': '01555000111', 'code': code,
                                 'new_password': 'short'})
    assert response.status_code == 400, response.get_json()
