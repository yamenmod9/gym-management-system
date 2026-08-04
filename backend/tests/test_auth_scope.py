"""Token scope: a member's token must never act as a staff account.

Phase 1 of the project audit.

The system issues two kinds of JWT from the same secret: staff tokens, whose
identity is a `users.id`, and client (member) tokens, whose identity is a
`customers.id` with a `scope: client` claim. Both id spaces start at 1 and
count up independently, so they collide constantly.

Nothing on the staff side looked at `scope`. `get_current_user()` took the
identity, called `int()` on it, and loaded that row out of `users` — so a
member holding customer id 7 presented a perfectly valid token that resolved
to staff user 7, inheriting whatever role that user has.

Run with:  pytest backend/tests/test_auth_scope.py
"""
import os
import sys
import tempfile

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
    """One gym whose owner is users.id=1, and a member who is customers.id=1."""
    from app.extensions import db
    from app.models.branch import Branch
    from app.models.customer import Customer
    from app.models.gym import Gym
    from app.models.user import User, UserRole

    owner = User(username='scope_owner', email='scope@example.com',
                 full_name='Scope Owner', role=UserRole.OWNER, is_active=True)
    owner.set_password('secret123')
    db.session.add(owner)
    db.session.flush()

    gym = Gym(name='Scope Gym', owner_id=owner.id, is_setup_complete=True)
    db.session.add(gym)
    db.session.flush()
    owner.gym_id = gym.id

    branch = Branch(name='Scope Branch', code='SC1', gym_id=gym.id, is_active=True)
    db.session.add(branch)
    db.session.flush()
    owner.branch_id = branch.id

    member = Customer(full_name='Scope Member', phone='01555000000',
                      branch_id=branch.id, is_active=True)
    db.session.add(member)
    db.session.commit()

    globals()['IDS'] = {
        'owner_user_id': owner.id,
        'member_customer_id': member.id,
        'branch': branch.id,
    }


@pytest.fixture
def member_token_headers(app):
    """A genuine member token whose customer id collides with a staff user id."""
    from app.utils.client_auth import create_client_token

    with app.app_context():
        token = create_client_token(IDS['member_customer_id'])
    return {'Authorization': f'Bearer {token}'}


def test_the_ids_really_do_collide(app):
    """The premise. If these ever diverge the tests below prove nothing."""
    assert IDS['owner_user_id'] == IDS['member_customer_id']


#: Staff endpoints spanning the three ways a route resolves the caller:
#: role_required, a bare jwt_required + get_current_user, and branch scoping.
STAFF_ENDPOINTS = [
    '/api/customers',
    '/api/users',
    '/api/branches',
    '/api/transactions',
    '/api/subscriptions',
    '/api/dashboards/owner',
    '/api/reports/revenue',
    '/api/gyms/settings',
]


@pytest.mark.parametrize('endpoint', STAFF_ENDPOINTS)
def test_a_member_token_cannot_act_as_staff(app, member_token_headers, endpoint):
    """Privilege escalation across audiences: member -> gym owner."""
    response = app.test_client().get(endpoint, headers=member_token_headers)
    assert response.status_code in (401, 403), (
        f'{endpoint} accepted a member token and answered '
        f'{response.status_code} — a member was served as staff user '
        f"{IDS['owner_user_id']}"
    )


def test_a_member_token_cannot_write_as_staff(app, member_token_headers):
    """Reads are bad enough; writes would let a member sell themselves a
    subscription or bank a transaction."""
    response = app.test_client().post(
        '/api/transactions',
        json={'amount': 1, 'payment_method': 'cash',
              'transaction_type': 'other', 'branch_id': IDS['branch']},
        headers=member_token_headers)
    assert response.status_code in (401, 403), response.get_json()


def test_a_staff_token_still_cannot_use_the_client_api(app):
    """The mirror image, which was already enforced — asserted so a fix to one
    direction does not quietly open the other."""
    client = app.test_client()
    login = client.post('/api/auth/login',
                        json={'username': 'scope_owner', 'password': 'secret123'})
    headers = {'Authorization': 'Bearer ' + login.get_json()['data']['access_token']}

    response = client.get('/api/client/me', headers=headers)
    assert response.status_code in (401, 403), response.get_json()


def test_staff_endpoints_still_work_for_staff(app):
    """The fix fails closed, so prove it did not close on everyone."""
    client = app.test_client()
    login = client.post('/api/auth/login',
                        json={'username': 'scope_owner', 'password': 'secret123'})
    headers = {'Authorization': 'Bearer ' + login.get_json()['data']['access_token']}

    for endpoint in STAFF_ENDPOINTS:
        response = client.get(endpoint, headers=headers)
        assert response.status_code == 200, (
            f'{endpoint} returned {response.status_code} to its own gym owner: '
            f'{response.get_json()}'
        )


def test_the_member_api_still_works_for_members(app, member_token_headers):
    response = app.test_client().get('/api/client/me',
                                     headers=member_token_headers)
    assert response.status_code == 200, response.get_json()
