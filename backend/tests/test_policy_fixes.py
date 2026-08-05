"""The three design-level fixes: business day, account erasure, service scope.

Each of these was flagged during the audit and deferred because it was a policy
decision rather than a defect. These pin the decisions once made.

Run with:  pytest backend/tests/test_policy_fixes.py
"""
import os
import sys
import tempfile
from datetime import date, datetime, timedelta

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
    from app.models.service import Service, ServiceType
    from app.models.user import User, UserRole

    ids = {}
    for tag in ('R', 'S'):
        owner = User(username=f'powner_{tag}', email=f'p{tag}@example.com',
                     full_name=f'Owner {tag}', role=UserRole.OWNER, is_active=True)
        owner.set_password('secret123')
        db.session.add(owner)
        db.session.flush()

        gym = Gym(name=f'Policy Gym {tag}', owner_id=owner.id, is_setup_complete=True)
        db.session.add(gym)
        db.session.flush()
        owner.gym_id = gym.id

        branch = Branch(name=f'Branch {tag}', code=f'P{tag}', gym_id=gym.id,
                        is_active=True)
        db.session.add(branch)
        db.session.flush()
        owner.branch_id = branch.id

        own_service = Service(name=f'Own Package {tag}', service_type=ServiceType.GYM,
                              price=500, duration_days=30, allowed_days_per_week=7,
                              gym_id=gym.id)
        db.session.add(own_service)
        db.session.flush()

        ids[tag] = {'gym': gym.id, 'branch': branch.id, 'owner': owner.id,
                    'service': own_service.id}

    # A package with no gym: the catalogue that predates the column.
    shared = Service(name='Shared Legacy Package', service_type=ServiceType.GYM,
                     price=400, duration_days=30, allowed_days_per_week=7,
                     gym_id=None)
    db.session.add(shared)
    db.session.flush()
    ids['shared_service'] = shared.id

    member = Customer(full_name='Leaving Member', phone='01999000111',
                      email='leaving@example.com', national_id='NAT-123',
                      address='1 Somewhere St', health_notes='knee injury',
                      branch_id=ids['R']['branch'], is_active=True)
    member.set_password('secret123')
    db.session.add(member)
    db.session.flush()
    ids['member'] = member.id

    db.session.commit()
    globals()['IDS'] = ids


def _headers(app, username):
    response = app.test_client().post(
        '/api/auth/login', json={'username': username, 'password': 'secret123'})
    assert response.status_code == 200, response.get_json()
    return {'Authorization': 'Bearer ' + response.get_json()['data']['access_token']}


@pytest.fixture
def owner_r(app):
    return _headers(app, 'powner_R')


# ───────────────────────────── the business day ─────────────────────────────

def test_the_business_day_follows_the_gym_not_the_server(app):
    """Cairo is UTC+2/+3, so 00:30 local on the 11th is 22:30 UTC on the 10th.

    Reporting on UTC dates put those takings in the wrong day's closing: a
    branch trading past midnight was short on the night and over the morning
    after.
    """
    from app.services.business_time import day_bounds_utc, gym_timezone

    start, end = day_bounds_utc(IDS['R']['gym'], date(2026, 3, 11))

    # The local day starts before UTC midnight, because the gym is ahead.
    assert start < datetime(2026, 3, 11, 0, 0), (
        f'local day started at {start} UTC, which is not ahead of UTC midnight'
    )
    assert end - start == timedelta(days=1)
    assert 'Cairo' in str(gym_timezone(IDS['R']['gym']))


def test_late_night_takings_land_in_the_right_days_closing(app, owner_r):
    """A sale at 00:30 local belongs to that local day, not the previous one."""
    from app.extensions import db
    from app.models.transaction import (
        Transaction, PaymentMethod, TransactionType,
    )

    # 00:30 on 12 March in Cairo == 22:30 on 11 March UTC.
    with app.app_context():
        db.session.add(Transaction(
            amount=300, discount=0, payment_method=PaymentMethod.CASH,
            transaction_type=TransactionType.SUBSCRIPTION,
            branch_id=IDS['R']['branch'], created_by=IDS['R']['owner'],
            transaction_date=datetime(2026, 3, 11, 22, 30),
            created_at=datetime(2026, 3, 11, 22, 30),
        ))
        db.session.commit()

    client = app.test_client()

    twelfth = client.post('/api/daily-closings/calculate',
                          json={'branch_id': IDS['R']['branch'], 'date': '2026-03-12'},
                          headers=owner_r).get_json()['data']
    eleventh = client.post('/api/daily-closings/calculate',
                           json={'branch_id': IDS['R']['branch'], 'date': '2026-03-11'},
                           headers=owner_r).get_json()['data']

    assert twelfth['expected_cash'] == pytest.approx(300.0), (
        'a sale at 00:30 local was not counted in that local day'
    )
    assert eleventh['expected_cash'] == pytest.approx(0.0), (
        'it was counted in the previous day as well'
    )


def test_an_unusable_timezone_setting_does_not_break_the_till(app):
    """A bad setting must degrade, not take down a reconciliation."""
    from app.services.business_time import DEFAULT_TIMEZONE, gym_timezone
    from app.services.gym_rules import db as rules_db  # noqa: F401
    from app.extensions import db
    from app.models.gym_setting import GymSetting

    with app.app_context():
        db.session.add(GymSetting(gym_id=IDS['S']['gym'], key='timezone',
                                  value='Not/AZone'))
        db.session.commit()

        assert str(gym_timezone(IDS['S']['gym'])) == DEFAULT_TIMEZONE


# ──────────────────────────── account erasure ───────────────────────────────

def test_a_due_deletion_erases_the_member_without_them_logging_in(app):
    """The purge used to be triggered from the member's own login and profile
    read — and someone who asked to be deleted is the one person who never
    comes back."""
    from app.extensions import db
    from app.models.customer import Customer
    from app.services.retention_service import (
        DELETE_REQUEST_PREFIX, purge_due_accounts,
    )

    with app.app_context():
        member = db.session.get(Customer, IDS['member'])
        requested = datetime.utcnow() - timedelta(days=91)
        member.health_notes = f'{DELETE_REQUEST_PREFIX} {requested.isoformat()}'
        db.session.commit()

        assert purge_due_accounts() == 1

        member = db.session.get(Customer, IDS['member'])
        assert member is not None, 'the row must survive; money references it'
        assert member.is_active is False
        assert member.full_name == 'Deleted member'
        assert member.email is None
        assert member.national_id is None
        assert member.address is None
        assert member.health_notes is None
        assert member.password_hash is None
        assert 'leaving@example.com' not in str(member.to_dict())


def test_purging_is_idempotent(app):
    from app.services.retention_service import purge_due_accounts

    with app.app_context():
        assert purge_due_accounts() == 0


def test_a_member_still_inside_the_grace_period_is_untouched(app):
    from app.extensions import db
    from app.models.customer import Customer
    from app.services.retention_service import (
        DELETE_REQUEST_PREFIX, purge_due_accounts,
    )

    with app.app_context():
        keeper = Customer(full_name='Undecided Member', phone='01999000222',
                          branch_id=IDS['R']['branch'], is_active=True)
        keeper.health_notes = (
            f'{DELETE_REQUEST_PREFIX} '
            f'{(datetime.utcnow() - timedelta(days=10)).isoformat()}'
        )
        db.session.add(keeper)
        db.session.commit()
        keeper_id = keeper.id

        assert purge_due_accounts() == 0
        assert db.session.get(Customer, keeper_id).full_name == 'Undecided Member'


# ──────────────────────────── service ownership ─────────────────────────────

def test_a_gym_cannot_see_another_gyms_packages(app, owner_r):
    body = app.test_client().get('/api/services', headers=owner_r).get_json()
    names = [s['name'] for s in body['data']['items']]

    assert 'Own Package R' in names
    assert 'Own Package S' not in names, "another gym's catalogue is visible"
    assert 'Shared Legacy Package' in names, (
        'the pre-existing shared catalogue must stay visible to everyone'
    )


def test_a_gym_cannot_read_another_gyms_package_by_id(app, owner_r):
    response = app.test_client().get(
        f"/api/services/{IDS['S']['service']}", headers=owner_r)
    assert response.status_code == 404, response.get_json()


def test_a_new_package_belongs_to_its_creators_gym(app, owner_r):
    from app.extensions import db
    from app.models.service import Service

    client = app.test_client()

    response = client.post(
        '/api/services',
        json={'name': 'Brand New R', 'service_type': 'gym', 'price': '600',
              'duration_days': 30},
        headers=owner_r)
    assert response.status_code == 201, response.get_json()

    with app.app_context():
        created = db.session.get(Service, response.get_json()['data']['id'])
        assert created.gym_id == IDS['R']['gym'], (
            'the package was not stamped with its creator\'s gym'
        )

    # And the id cannot be supplied: the schema declares no gym_id field, so
    # marshmallow rejects the attempt outright rather than the route having to
    # remember to strip it.
    injected = client.post(
        '/api/services',
        json={'name': 'Planted in S', 'service_type': 'gym', 'price': '600',
              'duration_days': 30, 'gym_id': IDS['S']['gym']},
        headers=owner_r)
    assert injected.status_code == 400, injected.get_json()


def test_a_shared_package_cannot_be_edited_from_one_gym(app, owner_r):
    """Editing it would change the price and entry rights for every other gym
    still selling it."""
    response = app.test_client().put(
        f"/api/services/{IDS['shared_service']}",
        json={'price': '1'}, headers=owner_r)
    assert response.status_code == 403, response.get_json()


def test_a_gym_can_still_edit_its_own_package(app, owner_r):
    response = app.test_client().put(
        f"/api/services/{IDS['R']['service']}",
        json={'price': '550'}, headers=owner_r)
    assert response.status_code == 200, response.get_json()


def test_creating_a_package_works_at_all(app, owner_r):
    """Regression: the route does Service(**data), and the schema handed it
    service_type as the string 'gym' while the column stores member names — so
    every attempt to create a service raised out of the handler as a 500. No
    gym could add a package, which is why all of them were still selling the
    seeded catalogue."""
    response = app.test_client().post(
        '/api/services',
        json={'name': 'Sanity Package', 'service_type': 'personal_training',
              'price': '900', 'duration_days': 60},
        headers=owner_r)
    assert response.status_code == 201, response.get_json()
    assert response.get_json()['data']['service_type'] == 'personal_training'


def test_an_unknown_service_type_is_still_rejected(app, owner_r):
    """Dropping the redundant OneOf must not drop the validation with it."""
    response = app.test_client().post(
        '/api/services',
        json={'name': 'Nonsense', 'service_type': 'quidditch',
              'price': '100', 'duration_days': 30},
        headers=owner_r)
    assert response.status_code == 400, response.get_json()


def test_a_transaction_can_still_be_created_through_its_schema(app, owner_r):
    """TransactionSchema loads two EnumValue fields; the same validator bug
    would have blocked every write through it."""
    response = app.test_client().post(
        '/api/transactions',
        json={'amount': '75', 'payment_method': 'cash',
              'transaction_type': 'other', 'branch_id': IDS['R']['branch']},
        headers=owner_r)
    assert response.status_code == 201, response.get_json()
    assert response.get_json()['data']['payment_method'] == 'cash'
