"""Who may create, edit and deactivate staff accounts.

Phase 1 of the project audit. The hierarchy and gym checks here are what stop
one gym administering another's staff, and what stop a manager promoting
themselves.

Run with:  pytest backend/tests/test_user_administration.py
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
    """Two gyms. Gym P has an owner, two branches, a regional manager whose
    scope is a branch *group* (so branch_id is NULL), and a branch manager."""
    from app.extensions import db
    from app.models.branch import Branch
    from app.models.gym import Gym
    from app.models.user import User, UserRole

    ids = {}
    for tag in ('P', 'Q'):
        owner = User(username=f'uowner_{tag}', email=f'u{tag}@example.com',
                     full_name=f'Owner {tag}', role=UserRole.OWNER, is_active=True)
        owner.set_password('secret123')
        db.session.add(owner)
        db.session.flush()

        gym = Gym(name=f'User Gym {tag}', owner_id=owner.id, is_setup_complete=True)
        db.session.add(gym)
        db.session.flush()
        owner.gym_id = gym.id

        first = Branch(name=f'{tag} One', code=f'U{tag}1', gym_id=gym.id, is_active=True)
        second = Branch(name=f'{tag} Two', code=f'U{tag}2', gym_id=gym.id, is_active=True)
        db.session.add_all([first, second])
        db.session.flush()
        owner.branch_id = first.id

        ids[tag] = {'gym': gym.id, 'owner': owner.id,
                    'branch1': first.id, 'branch2': second.id}

    # A regional manager in gym P: branch_id is NULL by design, scope comes
    # from managed_branches.
    from app.models.branch import Branch as B
    regional = User(username='uregional_P', email='ureg@example.com',
                    full_name='Regional P', role=UserRole.REGIONAL_MANAGER,
                    gym_id=ids['P']['gym'], branch_id=None, is_active=True)
    regional.set_password('secret123')
    regional.managed_branches = B.query.filter(
        B.id.in_([ids['P']['branch1'], ids['P']['branch2']])).all()
    db.session.add(regional)

    manager = User(username='umanager_P', email='umgr@example.com',
                   full_name='Manager P', role=UserRole.BRANCH_MANAGER,
                   gym_id=ids['P']['gym'], branch_id=ids['P']['branch1'],
                   is_active=True)
    manager.set_password('secret123')
    db.session.add(manager)
    db.session.flush()

    ids['regional_P'] = regional.id
    ids['manager_P'] = manager.id
    db.session.commit()
    globals()['IDS'] = ids


def _headers(app, username):
    response = app.test_client().post(
        '/api/auth/login', json={'username': username, 'password': 'secret123'})
    assert response.status_code == 200, response.get_json()
    return {'Authorization': 'Bearer ' + response.get_json()['data']['access_token']}


@pytest.fixture
def owner_p(app):
    return _headers(app, 'uowner_P')


# ────────────── an owner must be able to run their own gym ──────────────────

def test_an_owner_can_read_their_own_regional_manager(app, owner_p):
    """A regional manager has no branch_id — their scope is a branch group.

    The scope check narrowed to `target.branch_id in accessible_branches`,
    which NULL never satisfies, so an owner could not see, edit or deactivate
    their own regional managers or any other gym-wide staff.
    """
    response = app.test_client().get(
        f"/api/users/{IDS['regional_P']}", headers=owner_p)
    assert response.status_code == 200, response.get_json()


def test_an_owner_can_edit_their_own_regional_manager(app, owner_p):
    response = app.test_client().put(
        f"/api/users/{IDS['regional_P']}",
        json={'full_name': 'Regional P Renamed'}, headers=owner_p)
    assert response.status_code == 200, response.get_json()


def test_an_owner_can_create_gym_wide_staff_without_a_branch(app, owner_p):
    """A central accountant is gym-wide and carries no branch_id."""
    response = app.test_client().post(
        '/api/users',
        json={'username': 'ucentral_P', 'email': 'ucen@example.com',
              'full_name': 'Central P', 'password': 'secret123',
              'role': 'central_accountant'},
        headers=owner_p)
    assert response.status_code == 201, response.get_json()


# ───────────────────────── cross-gym administration ─────────────────────────

def test_an_owner_cannot_administer_another_gyms_staff(app, owner_p):
    client = app.test_client()
    assert client.get(f"/api/users/{IDS['Q']['owner']}",
                      headers=owner_p).status_code == 404
    assert client.put(f"/api/users/{IDS['Q']['owner']}",
                      json={'full_name': 'hijacked'},
                      headers=owner_p).status_code in (403, 404)


def test_a_regional_manager_cannot_be_given_another_gyms_branches(app, owner_p):
    """managed_branch_ids is a scope grant.

    The create path validated it against the caller's own branches; the update
    path did not check it at all — so an owner could widen their own regional
    manager's scope into another gym, and everything that manager then read was
    someone else's data.
    """
    response = app.test_client().put(
        f"/api/users/{IDS['regional_P']}",
        json={'managed_branch_ids': [IDS['P']['branch1'], IDS['Q']['branch1']]},
        headers=owner_p)
    assert response.status_code in (400, 403), response.get_json()

    # And the grant must not have been applied even partially.
    from app.extensions import db
    from app.models.user import User
    with app.app_context():
        regional = db.session.get(User, IDS['regional_P'])
        assert IDS['Q']['branch1'] not in regional.managed_branch_ids, (
            "a foreign branch was added to this manager's scope"
        )


def test_a_branch_manager_cannot_create_an_account_at_their_own_rank(app):
    headers = _headers(app, 'umanager_P')
    response = app.test_client().post(
        '/api/users',
        json={'username': 'usneak', 'email': 'usneak@example.com',
              'full_name': 'Sneak', 'password': 'secret123',
              'role': 'branch_manager', 'branch_id': IDS['P']['branch1']},
        headers=headers)
    assert response.status_code == 403, response.get_json()


# ──────────────────────────── password strength ─────────────────────────────

def test_a_trivial_password_is_refused(app, owner_p):
    """The member-facing password change requires eight characters; the staff
    one accepted anything at all, including a single digit."""
    response = app.test_client().post(
        '/api/auth/change-password',
        json={'old_password': 'secret123', 'new_password': '1'},
        headers=owner_p)
    assert response.status_code == 400, response.get_json()


def test_a_real_password_change_still_works(app):
    """Fails closed — prove the rule did not lock everyone out."""
    client = app.test_client()
    headers = _headers(app, 'umanager_P')

    changed = client.post(
        '/api/auth/change-password',
        json={'old_password': 'secret123', 'new_password': 'newsecret456'},
        headers=headers)
    assert changed.status_code == 200, changed.get_json()

    relogin = client.post('/api/auth/login',
                          json={'username': 'umanager_P',
                                'password': 'newsecret456'})
    assert relogin.status_code == 200, relogin.get_json()
