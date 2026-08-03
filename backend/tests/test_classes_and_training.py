"""Classes, attendance, feedback, private training and the dispute path.

Stages 2-4 shipped without coverage, which is how a duplicate id in one
attendance payload reached production as a 500. These tests pin the behaviour
each fix restored, and the main flows around them.

Run with:  pytest backend/tests/test_classes_and_training.py
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
    from app.models.gym_class import GymClass
    from app.models.service import Service, ServiceType
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.user import User, UserRole

    owner = User(username='owner_ct', email='ct@example.com', full_name='Owner',
                 role=UserRole.OWNER, is_active=True)
    owner.set_password('secret123')
    db.session.add(owner)
    db.session.flush()

    gym = Gym(name='CT Gym', owner_id=owner.id, is_setup_complete=True)
    db.session.add(gym)
    db.session.flush()
    owner.gym_id = gym.id

    branch = Branch(name='Main', code='CT1', gym_id=gym.id, is_active=True)
    other_branch = Branch(name='Other', code='CT2', gym_id=gym.id, is_active=True)
    db.session.add_all([branch, other_branch])
    db.session.flush()
    owner.branch_id = branch.id

    trainer = User(username='cap_ct', email='cap_ct@example.com', full_name='Captain',
                   role=UserRole.TRAINER, gym_id=gym.id, branch_id=branch.id,
                   is_active=True)
    trainer.set_password('secret123')
    other_trainer = User(username='cap_ct2', email='cap_ct2@example.com',
                         full_name='Other Captain', role=UserRole.TRAINER,
                         gym_id=gym.id, branch_id=branch.id, is_active=True)
    other_trainer.set_password('secret123')
    db.session.add_all([trainer, other_trainer])
    db.session.flush()

    gym_svc = Service(name='Gym', service_type=ServiceType.GYM, price=500,
                      duration_days=30, allowed_days_per_week=7,
                      grants_gym_entry=True)
    pt_svc = Service(name='PT', service_type=ServiceType.PERSONAL_TRAINING,
                     price=2000, duration_days=90, allowed_days_per_week=7,
                     grants_gym_entry=False)
    db.session.add_all([gym_svc, pt_svc])
    db.session.flush()

    def member(name, branch_obj=branch, coins=10):
        customer = Customer(full_name=name,
                            phone=f'02{abs(hash(name)) % 100000000:08d}',
                            branch_id=branch_obj.id, is_active=True)
        db.session.add(customer)
        db.session.flush()
        db.session.add(Subscription(
            customer_id=customer.id, service_id=gym_svc.id, branch_id=branch_obj.id,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            status=SubscriptionStatus.ACTIVE, subscription_type='coins',
            remaining_coins=coins, total_coins=coins,
        ))
        db.session.flush()
        return customer

    alice = member('Alice CT')
    bob = member('Bob CT')
    outsider = member('Outsider CT', other_branch)

    # Alice also trains privately with the captain.
    pt_sub = Subscription(
        customer_id=alice.id, service_id=pt_svc.id, branch_id=branch.id,
        start_date=date.today(), end_date=date.today() + timedelta(days=90),
        status=SubscriptionStatus.ACTIVE, subscription_type='sessions',
        remaining_sessions=10, total_sessions=10, trainer_id=trainer.id,
    )
    db.session.add(pt_sub)
    db.session.flush()

    # Scheduled on every weekday so it always runs "today".
    spinning = GymClass(name='Spinning', branch_id=branch.id, gym_id=gym.id,
                        trainer_id=trainer.id, capacity=2,
                        days_of_week='0,1,2,3,4,5,6', is_active=True)
    # Assigned to someone else, to prove a captain cannot start another's class.
    yoga = GymClass(name='Yoga', branch_id=branch.id, gym_id=gym.id,
                    trainer_id=other_trainer.id, days_of_week='0,1,2,3,4,5,6',
                    is_active=True)
    db.session.add_all([spinning, yoga])
    db.session.flush()

    globals()['IDS'] = {
        'gym_id': gym.id,
        'branch_id': branch.id,
        'trainer_id': trainer.id,
        'alice': alice.id,
        'bob': bob.id,
        'outsider': outsider.id,
        'pt_sub': pt_sub.id,
        'gym_service_id': gym_svc.id,
        'pt_service_id': pt_svc.id,
        'spinning': spinning.id,
        'yoga': yoga.id,
    }
    db.session.commit()


def _headers(app, username):
    client = app.test_client()
    response = client.post('/api/auth/login',
                           json={'username': username, 'password': 'secret123'})
    assert response.status_code == 200, response.get_json()
    return {'Authorization': 'Bearer ' + response.get_json()['data']['access_token']}


@pytest.fixture
def trainer_headers(app):
    return _headers(app, 'cap_ct')


@pytest.fixture
def owner_headers(app):
    return _headers(app, 'owner_ct')


@pytest.fixture
def session_id(app, trainer_headers):
    """A freshly started sitting of Spinning, with an empty register."""
    from app.extensions import db
    from app.models.gym_class import ClassAttendance, ClassSession

    with app.app_context():
        # Each test wants a clean register, so clear any prior sitting.
        for s in ClassSession.query.filter_by(class_id=IDS['spinning']).all():
            ClassAttendance.query.filter_by(session_id=s.id).delete()
            db.session.delete(s)
        db.session.commit()

    response = app.test_client().post(
        f"/api/classes/{IDS['spinning']}/sessions", headers=trainer_headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()['data']['id']


# ─────────────────────── attendance: the 500 that shipped ───────────────────

def test_repeated_id_in_one_payload_is_skipped_not_a_500(app, trainer_headers, session_id):
    """The regression: {"customer_ids": [x, x]} used to break the unique
    constraint on (session, customer) and surface as a 500."""
    response = app.test_client().post(
        f'/api/classes/sessions/{session_id}/attendance',
        json={'customer_ids': [IDS['alice'], IDS['alice']]},
        headers=trainer_headers,
    )
    assert response.status_code == 200, response.get_json()
    data = response.get_json()['data']

    assert data['added'] == [IDS['alice']]
    assert data['attendance_count'] == 1
    assert [s['reason'] for s in data['skipped']] == ['already marked']


def test_marking_someone_already_on_the_register_is_skipped(app, trainer_headers, session_id):
    client = app.test_client()
    client.post(f'/api/classes/sessions/{session_id}/attendance',
                json={'customer_id': IDS['alice']}, headers=trainer_headers)
    second = client.post(f'/api/classes/sessions/{session_id}/attendance',
                         json={'customer_id': IDS['alice']}, headers=trainer_headers)

    assert second.status_code == 200
    data = second.get_json()['data']
    assert data['added'] == []
    assert data['attendance_count'] == 1


def test_capacity_is_enforced_across_one_payload(app, trainer_headers, session_id):
    """Spinning seats 2. A payload of three must fill it and skip the rest."""
    response = app.test_client().post(
        f'/api/classes/sessions/{session_id}/attendance',
        json={'customer_ids': [IDS['alice'], IDS['bob'], IDS['outsider']]},
        headers=trainer_headers,
    )
    data = response.get_json()['data']

    assert data['attendance_count'] == 2
    assert set(data['added']) == {IDS['alice'], IDS['bob']}
    # The outsider is rejected on branch, not capacity — either way, not added.
    assert IDS['outsider'] not in data['added']


def test_a_member_of_another_branch_cannot_be_marked_present(app, trainer_headers, session_id):
    response = app.test_client().post(
        f'/api/classes/sessions/{session_id}/attendance',
        json={'customer_id': IDS['outsider']}, headers=trainer_headers,
    )
    data = response.get_json()['data']
    assert data['added'] == []
    assert data['skipped'][0]['reason'] == 'not a member of this branch'


# ────────────────────────────── the coin rule ───────────────────────────────

def test_coin_is_only_deducted_when_the_gym_switched_the_rule_on(app, trainer_headers, session_id):
    from app.extensions import db
    from app.models.customer import Customer
    from app.models.subscription import Subscription
    from app.services.gym_rules import set_rules

    def coins():
        with app.app_context():
            return Subscription.entry_subscription_for(IDS['bob']).remaining_coins

    client = app.test_client()
    before = coins()

    # Default is off: attending costs nothing.
    client.post(f'/api/classes/sessions/{session_id}/attendance',
                json={'customer_id': IDS['bob']}, headers=trainer_headers)
    assert coins() == before

    client.delete(f"/api/classes/sessions/{session_id}/attendance/{IDS['bob']}",
                  headers=trainer_headers)

    with app.app_context():
        set_rules(IDS['gym_id'], {'class_attendance_deducts_coin': True})
    try:
        client.post(f'/api/classes/sessions/{session_id}/attendance',
                    json={'customer_id': IDS['bob']}, headers=trainer_headers)
        assert coins() == before - 1

        # Removing a mistaken mark hands the coin back.
        client.delete(f"/api/classes/sessions/{session_id}/attendance/{IDS['bob']}",
                      headers=trainer_headers)
        assert coins() == before
    finally:
        with app.app_context():
            set_rules(IDS['gym_id'], {'class_attendance_deducts_coin': False})


# ────────────────────────── who may run which class ─────────────────────────

def test_a_captain_cannot_start_someone_elses_class(app, trainer_headers):
    response = app.test_client().post(
        f"/api/classes/{IDS['yoga']}/sessions", headers=trainer_headers)
    assert response.status_code == 403


def test_starting_the_same_class_twice_reuses_the_sitting(app, trainer_headers, session_id):
    """Two taps must not split the register in two."""
    response = app.test_client().post(
        f"/api/classes/{IDS['spinning']}/sessions", headers=trainer_headers)
    assert response.status_code == 200
    assert response.get_json()['data']['id'] == session_id


def test_a_class_not_scheduled_today_cannot_be_started(app, trainer_headers):
    from app.extensions import db
    from app.models.gym_class import GymClass

    with app.app_context():
        gym_class = db.session.get(GymClass, IDS['spinning'])
        original = gym_class.days_of_week
        # Schedule it on every weekday except today.
        gym_class.days_of_week = ','.join(
            str(d) for d in range(7) if d != date.today().weekday())
        db.session.commit()
    try:
        response = app.test_client().post(
            f"/api/classes/{IDS['spinning']}/sessions", headers=trainer_headers)
        assert response.status_code == 400
        assert 'not scheduled' in response.get_json()['error']
    finally:
        with app.app_context():
            db.session.get(GymClass, IDS['spinning']).days_of_week = original
            db.session.commit()


# ──────────────────────────────── feedback ──────────────────────────────────

def test_only_attendees_can_rate_and_only_once(app, trainer_headers, session_id):
    from app.utils.client_auth import create_client_token

    client = app.test_client()
    client.post(f'/api/classes/sessions/{session_id}/attendance',
                json={'customer_id': IDS['alice']}, headers=trainer_headers)
    client.post(f'/api/classes/sessions/{session_id}/close', headers=trainer_headers)

    with app.app_context():
        alice_headers = {'Authorization': 'Bearer ' + create_client_token(IDS['alice'])}
        bob_headers = {'Authorization': 'Bearer ' + create_client_token(IDS['bob'])}

    # Bob never turned up.
    refused = client.post('/api/client/class-feedback',
                          json={'session_id': session_id, 'rating': 5},
                          headers=bob_headers)
    assert refused.status_code == 403

    accepted = client.post('/api/client/class-feedback',
                           json={'session_id': session_id, 'rating': 4,
                                 'comment': 'good session'},
                           headers=alice_headers)
    assert accepted.status_code == 201, accepted.get_json()

    again = client.post('/api/client/class-feedback',
                        json={'session_id': session_id, 'rating': 1},
                        headers=alice_headers)
    assert again.status_code == 409

    summary = client.get(f'/api/classes/sessions/{session_id}/feedback',
                         headers=trainer_headers).get_json()['data']
    assert summary['count'] == 1
    assert summary['average_rating'] == 4


@pytest.mark.parametrize('rating', [0, 6, -1, 'five'])
def test_a_rating_outside_one_to_five_is_rejected(app, trainer_headers, session_id, rating):
    from app.utils.client_auth import create_client_token

    client = app.test_client()
    client.post(f'/api/classes/sessions/{session_id}/attendance',
                json={'customer_id': IDS['alice']}, headers=trainer_headers)
    client.post(f'/api/classes/sessions/{session_id}/close', headers=trainer_headers)

    with app.app_context():
        headers = {'Authorization': 'Bearer ' + create_client_token(IDS['alice'])}

    response = client.post('/api/client/class-feedback',
                           json={'session_id': session_id, 'rating': rating},
                           headers=headers)
    assert response.status_code == 400


# ───────────────────────────── private training ─────────────────────────────

def test_awaiting_confirmation_ignores_sessions_past_the_window(app, trainer_headers):
    """The captain's badge must not count sessions the system already treats
    as confirmed — otherwise it only ever climbs."""
    from app.extensions import db
    from app.models.private_session import (
        AUTO_CONFIRM_AFTER, PrivateSession, PrivateSessionStatus,
    )

    with app.app_context():
        PrivateSession.query.delete()
        db.session.add(PrivateSession(
            subscription_id=IDS['pt_sub'], customer_id=IDS['alice'],
            trainer_id=IDS['trainer_id'], branch_id=IDS['branch_id'],
            status=PrivateSessionStatus.PENDING,
            logged_at=datetime.utcnow() - AUTO_CONFIRM_AFTER - timedelta(hours=1),
        ))
        db.session.add(PrivateSession(
            subscription_id=IDS['pt_sub'], customer_id=IDS['alice'],
            trainer_id=IDS['trainer_id'], branch_id=IDS['branch_id'],
            status=PrivateSessionStatus.PENDING, logged_at=datetime.utcnow(),
        ))
        db.session.commit()

    clients = app.test_client().get('/api/private-training/clients',
                                    headers=trainer_headers).get_json()['data']
    row = next(c for c in clients if c['subscription_id'] == IDS['pt_sub'])
    assert row['awaiting_confirmation'] == 1, (
        'the lapsed session should no longer be counted as awaiting an answer'
    )


def test_logging_a_session_deducts_it_and_a_refund_gives_it_back(app, trainer_headers, owner_headers):
    from app.extensions import db
    from app.models.private_session import PrivateSession
    from app.models.subscription import Subscription
    from app.utils.client_auth import create_client_token

    def remaining():
        with app.app_context():
            return db.session.get(Subscription, IDS['pt_sub']).remaining_sessions

    with app.app_context():
        PrivateSession.query.delete()
        db.session.commit()

    client = app.test_client()
    before = remaining()

    logged = client.post('/api/private-training/sessions',
                         json={'subscription_id': IDS['pt_sub'], 'notes': 'legs'},
                         headers=trainer_headers)
    assert logged.status_code == 201, logged.get_json()
    session_id = logged.get_json()['data']['id']
    assert remaining() == before - 1, 'deducted when logged, not when confirmed'

    with app.app_context():
        alice_headers = {'Authorization': 'Bearer ' + create_client_token(IDS['alice'])}

    disputed = client.post(
        f'/api/private-training/client/sessions/{session_id}/dispute',
        json={'reason': 'I was not there that day'}, headers=alice_headers)
    assert disputed.status_code == 200, disputed.get_json()

    queue = client.get('/api/private-training/disputes',
                       headers=owner_headers).get_json()['data']
    assert [d['id'] for d in queue] == [session_id]

    resolved = client.post(
        f'/api/private-training/disputes/{session_id}/resolve',
        json={'decision': 'refund'}, headers=owner_headers)
    assert resolved.status_code == 200, resolved.get_json()
    assert remaining() == before, 'a refund credits the session back'


def test_upholding_a_dispute_leaves_the_session_deducted(app, trainer_headers, owner_headers):
    from app.extensions import db
    from app.models.private_session import PrivateSession
    from app.models.subscription import Subscription
    from app.utils.client_auth import create_client_token

    def remaining():
        with app.app_context():
            return db.session.get(Subscription, IDS['pt_sub']).remaining_sessions

    with app.app_context():
        PrivateSession.query.delete()
        db.session.commit()

    client = app.test_client()
    before = remaining()

    session_id = client.post(
        '/api/private-training/sessions', json={'subscription_id': IDS['pt_sub']},
        headers=trainer_headers).get_json()['data']['id']

    with app.app_context():
        alice_headers = {'Authorization': 'Bearer ' + create_client_token(IDS['alice'])}

    client.post(f'/api/private-training/client/sessions/{session_id}/dispute',
                json={'reason': 'did not happen'}, headers=alice_headers)
    client.post(f'/api/private-training/disputes/{session_id}/resolve',
                json={'decision': 'uphold'}, headers=owner_headers)

    assert remaining() == before - 1


def test_a_captain_cannot_log_against_a_package_that_is_not_theirs(app):
    """The subscription names a captain; another captain must not bill it."""
    other = _headers(app, 'cap_ct2')
    response = app.test_client().post(
        '/api/private-training/sessions', json={'subscription_id': IDS['pt_sub']},
        headers=other)
    assert response.status_code == 404


# ───────────────────────────── the door, again ──────────────────────────────

def test_an_explicitly_named_training_package_cannot_open_the_door(app):
    """validate_entry trusts a subscription id it is handed (a QR token carries
    one), so the grants-entry rule has to be re-applied there too."""
    from app.services.qr_service import QRService

    with app.app_context():
        ok, reason, _sub, _coins = QRService.validate_entry(
            customer_id=IDS['alice'], subscription_id=IDS['pt_sub'])

        assert ok is False
        assert 'does not grant gym entry' in reason


def test_a_membership_with_no_visit_counter_is_not_a_crash(app):
    """Regression: every subscription in production stores NULL for
    remaining_visits/remaining_classes, and `None <= 0` raised TypeError —
    a 500 at the front desk instead of an admitted member."""
    from app.extensions import db
    from app.models.subscription import Subscription
    from app.services.qr_service import QRService

    with app.app_context():
        entry = Subscription.entry_subscription_for(IDS['bob'])
        assert entry.remaining_visits is None
        assert entry.remaining_classes is None

        ok, reason, _sub, coins = QRService.validate_entry(
            customer_id=IDS['bob'], subscription_id=entry.id)
        assert ok is True, reason
        assert coins == 0, 'an untracked counter must not be metered'

        # And deducting against it must not raise either.
        QRService.deduct_entry(entry, coins=1)
        assert entry.remaining_visits is None
        assert db.session.get(Subscription, entry.id).status.value == 'active'


def test_the_gym_package_still_opens_the_door(app):
    from app.models.subscription import Subscription
    from app.services.qr_service import QRService

    with app.app_context():
        entry = Subscription.entry_subscription_for(IDS['alice'])
        assert entry.service_id == IDS['gym_service_id']

        ok, reason, _sub, _coins = QRService.validate_entry(
            customer_id=IDS['alice'], subscription_id=entry.id)
        assert ok is True, reason


# ──────────────────── the rule that used to do nothing ──────────────────────

def test_switching_off_multiple_subscriptions_blocks_a_second_one(app):
    from app.extensions import db
    from app.models.user import User
    from app.services.gym_rules import set_rules
    from app.services.subscription_service import SubscriptionService

    payload = {
        'customer_id': IDS['bob'],
        'service_id': IDS['gym_service_id'],
        'branch_id': IDS['branch_id'],
    }

    with app.app_context():
        staff_id = User.query.filter_by(username='owner_ct').one().id

        # On (the default): Bob already holds one, a second is allowed.
        sub, error = SubscriptionService.create_subscription(payload, staff_id)
        assert error is None, error
        assert sub is not None
        db.session.commit()

        set_rules(IDS['gym_id'], {'allow_multiple_active_subscriptions': False})
        try:
            sub, error = SubscriptionService.create_subscription(payload, staff_id)
            assert sub is None
            assert 'only one at a time' in error
        finally:
            db.session.rollback()
            set_rules(IDS['gym_id'], {'allow_multiple_active_subscriptions': True})


def test_every_rule_is_actually_consulted_somewhere(app):
    """A switch on the owner's settings screen that no code reads is a lie.

    Guards the whole set rather than one rule, so a rule added later cannot be
    shipped as decoration.
    """
    import pathlib
    from app.services.gym_rules import RULES

    backend = pathlib.Path(__file__).resolve().parent.parent
    sources = [
        p for p in backend.rglob('*.py')
        if '__pycache__' not in p.parts
        and p.name != 'gym_rules.py'
        and 'tests' not in p.parts
    ]
    blob = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in sources)

    unused = [key for key in RULES if key not in blob]
    assert not unused, f'gym rules with no effect anywhere: {unused}'
