"""Body composition history, and the captain-to-member message centre.

Both hang off one rule — does this trainer privately coach this member — so
both are tested together, and the rule is tested from every direction that
could leak: another captain's client, a member at the same branch who has no
private training, and a member whose package has lapsed.

Run with:  pytest backend/tests/test_coaching.py
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
    from app.models.customer import Customer, Gender
    from app.models.gym import Gym
    from app.models.service import Service, ServiceType
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.user import User, UserRole

    ids = {}

    owner = User(username='coach_owner', email='co@example.com',
                 full_name='Coach Owner', role=UserRole.OWNER, is_active=True)
    owner.set_password('secret123')
    db.session.add(owner)
    db.session.flush()

    gym = Gym(name='Coaching Gym', owner_id=owner.id, is_setup_complete=True)
    db.session.add(gym)
    db.session.flush()
    owner.gym_id = gym.id

    branch = Branch(name='Coaching Branch', code='COACH', gym_id=gym.id,
                    is_active=True)
    db.session.add(branch)
    db.session.flush()
    owner.branch_id = branch.id

    def staff(username, role):
        user = User(username=username, email=f'{username}@example.com',
                    full_name=username.replace('_', ' ').title(), role=role,
                    gym_id=gym.id, branch_id=branch.id, is_active=True)
        user.set_password('secret123')
        db.session.add(user)
        db.session.flush()
        return user

    captain = staff('captain_ali', UserRole.TRAINER)
    other_captain = staff('captain_sara', UserRole.TRAINER)
    desk = staff('coach_desk', UserRole.FRONT_DESK)

    def member(name, phone):
        customer = Customer(
            full_name=name, phone=phone, branch_id=branch.id, is_active=True,
            gender=Gender.MALE, date_of_birth=date(1995, 5, 20),
            height=180, weight=85, health_notes='old knee injury',
        )
        customer.set_password('secret123')
        db.session.add(customer)
        db.session.flush()
        return customer

    mine = member('My PT Client', '01777000111')
    theirs = member('Another Captains Client', '01777000222')
    plain = member('Plain Gym Member', '01777000333')
    lapsed = member('Lapsed PT Client', '01777000444')

    pt_service = Service(name='PT Package', service_type=ServiceType.PERSONAL_TRAINING,
                         price=1000, duration_days=30, gym_id=gym.id)
    db.session.add(pt_service)
    db.session.flush()

    def subscribe(customer, trainer, status):
        sub = Subscription(
            customer_id=customer.id, service_id=pt_service.id,
            branch_id=branch.id, trainer_id=trainer.id if trainer else None,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=25),
            status=status,
        )
        db.session.add(sub)
        db.session.flush()
        return sub

    subscribe(mine, captain, SubscriptionStatus.ACTIVE)
    subscribe(theirs, other_captain, SubscriptionStatus.ACTIVE)
    subscribe(plain, None, SubscriptionStatus.ACTIVE)
    subscribe(lapsed, captain, SubscriptionStatus.EXPIRED)

    ids.update(
        gym=gym.id, branch=branch.id, owner=owner.id,
        captain=captain.id, other_captain=other_captain.id, desk=desk.id,
        mine=mine.id, theirs=theirs.id, plain=plain.id, lapsed=lapsed.id,
    )
    db.session.commit()
    globals()['IDS'] = ids


def _staff(app, username):
    r = app.test_client().post('/api/auth/login',
                               json={'username': username, 'password': 'secret123'})
    assert r.status_code == 200, r.get_json()
    return {'Authorization': 'Bearer ' + r.get_json()['data']['access_token']}


def _member(app, phone):
    r = app.test_client().post('/api/client/auth/login',
                               json={'phone': phone, 'password': 'secret123'})
    assert r.status_code == 200, r.get_json()
    return {'Authorization': 'Bearer ' + r.get_json()['data']['access_token']}


@pytest.fixture
def captain(app):
    return _staff(app, 'captain_ali')


@pytest.fixture
def desk(app):
    return _staff(app, 'coach_desk')


@pytest.fixture
def owner(app):
    return _staff(app, 'coach_owner')


# ───────────────────────── recording measurements ───────────────────────────

def test_a_weigh_in_is_recorded_and_derived(app, desk):
    response = app.test_client().post(
        f"/api/customers/{IDS['mine']}/measurements",
        json={'weight_kg': 84.2, 'height_cm': 180, 'body_fat_percent': 22.5,
              'skeletal_muscle_mass_kg': 36.1, 'visceral_fat_level': 9,
              'inbody_score': 74, 'notes': 'first InBody'},
        headers=desk)
    assert response.status_code == 201, response.get_json()

    data = response.get_json()['data']
    assert data['weight_kg'] == 84.2
    assert data['body_fat_percent'] == 22.5
    # Derived, not supplied.
    assert data['bmi'] == pytest.approx(25.99, abs=0.01)
    assert data['bmi_category'] == 'Overweight'
    assert data['bmr'] is not None
    assert data['body_fat_mass_kg'] == pytest.approx(18.95, abs=0.01)
    assert data['recorded_by_name'] == 'Coach Desk'


def test_history_accumulates_instead_of_overwriting(app, desk):
    """The whole point. Weight was a single column on the member's row that
    every edit destroyed, so a member training for a year had one number."""
    client = app.test_client()

    for weight, when in ((90.0, '2026-01-10T09:00:00'),
                         (88.0, '2026-02-10T09:00:00')):
        r = client.post(f"/api/customers/{IDS['plain']}/measurements",
                        json={'weight_kg': weight, 'height_cm': 175,
                              'measured_at': when},
                        headers=desk)
        assert r.status_code == 201, r.get_json()

    body = client.get(f"/api/customers/{IDS['plain']}/measurements",
                      headers=desk).get_json()['data']
    assert body['count'] == 2
    # Newest first.
    assert [row['weight_kg'] for row in body['items']] == [88.0, 90.0]


def test_the_members_current_values_track_the_latest_reading(app, desk):
    """Existing screens read customer.bmi. They have to keep showing the newest
    number, or recording history would make the member record go stale."""
    from app.extensions import db
    from app.models.customer import Customer

    client = app.test_client()
    client.post(f"/api/customers/{IDS['plain']}/measurements",
                json={'weight_kg': 80.0, 'height_cm': 175,
                      'measured_at': '2026-03-10T09:00:00'},
                headers=desk)

    with app.app_context():
        assert db.session.get(Customer, IDS['plain']).weight == 80.0

    # Back-filling an older reading must not drag the current values backwards.
    client.post(f"/api/customers/{IDS['plain']}/measurements",
                json={'weight_kg': 99.0, 'height_cm': 175,
                      'measured_at': '2025-01-01T09:00:00'},
                headers=desk)

    with app.app_context():
        assert db.session.get(Customer, IDS['plain']).weight == 80.0, (
            'an older measurement overwrote the current weight'
        )


def test_a_fat_fingered_number_is_refused(app, desk):
    client = app.test_client()
    for payload in ({'weight_kg': 8500}, {'weight_kg': 80, 'height_cm': 1750},
                    {'weight_kg': 80, 'body_fat_percent': 950}):
        r = client.post(f"/api/customers/{IDS['mine']}/measurements",
                        json=payload, headers=desk)
        assert r.status_code == 400, (payload, r.get_json())


def test_weight_is_required_and_the_future_is_not(app, desk):
    client = app.test_client()
    assert client.post(f"/api/customers/{IDS['mine']}/measurements",
                       json={'height_cm': 180}, headers=desk).status_code == 400

    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    assert client.post(f"/api/customers/{IDS['mine']}/measurements",
                       json={'weight_kg': 80, 'measured_at': tomorrow},
                       headers=desk).status_code == 400


# ───────────────────── who may read a measurement ───────────────────────────

def test_a_member_sees_their_own_history(app):
    body = app.test_client().get(
        '/api/client/measurements',
        headers=_member(app, '01777000111')).get_json()['data']
    assert body['count'] >= 1
    assert body['latest']['weight_kg'] is not None


def test_a_member_sees_only_their_own(app):
    """There is no customer_id parameter to tamper with — the member's history
    is derived from their token. This pins that it stays that way."""
    mine = app.test_client().get(
        '/api/client/measurements',
        headers=_member(app, '01777000111')).get_json()['data']
    theirs = app.test_client().get(
        '/api/client/measurements',
        headers=_member(app, '01777000333')).get_json()['data']

    mine_ids = {row['id'] for row in mine['items']}
    theirs_ids = {row['id'] for row in theirs['items']}
    assert mine_ids and theirs_ids
    assert not (mine_ids & theirs_ids)


def test_a_captain_reads_the_history_of_their_own_client(app, captain):
    r = app.test_client().get(f"/api/customers/{IDS['mine']}/measurements",
                              headers=captain)
    assert r.status_code == 200, r.get_json()
    assert r.get_json()['data']['count'] >= 1


def test_a_captain_cannot_read_another_captains_client(app, captain):
    r = app.test_client().get(f"/api/customers/{IDS['theirs']}/measurements",
                              headers=captain)
    assert r.status_code == 404, r.get_json()


def test_a_captain_cannot_read_a_member_they_do_not_coach(app, captain):
    """Same branch, no private training. A trainer is otherwise an ordinary
    branch-scoped staff member, so this is the rule doing the work."""
    r = app.test_client().get(f"/api/customers/{IDS['plain']}/measurements",
                              headers=captain)
    assert r.status_code == 404, r.get_json()


def test_reception_reads_any_member_at_their_branch(app, desk):
    for member_id in (IDS['mine'], IDS['theirs'], IDS['plain']):
        r = app.test_client().get(f"/api/customers/{member_id}/measurements",
                                  headers=desk)
        assert r.status_code == 200, (member_id, r.get_json())


def test_a_captain_cannot_record_against_someone_elses_client(app, captain):
    r = app.test_client().post(f"/api/customers/{IDS['theirs']}/measurements",
                               json={'weight_kg': 70}, headers=captain)
    assert r.status_code == 404, r.get_json()


# ─────────────── the same rule on the members list itself ───────────────────

def test_a_captain_does_not_see_health_data_of_members_they_do_not_coach(app, captain):
    """Otherwise the restriction above is decorative: the members list is
    branch-scoped with no role gate, so a captain could read weight, BMI and
    health notes for the whole branch and never touch the history endpoint."""
    client = app.test_client()

    mine = client.get(f"/api/customers/{IDS['mine']}", headers=captain).get_json()['data']
    assert mine['weight'] is not None
    assert 'health_notes' in mine

    plain = client.get(f"/api/customers/{IDS['plain']}", headers=captain).get_json()['data']
    assert 'weight' not in plain, 'health data leaked for a member they do not coach'
    assert 'bmi' not in plain
    assert 'health_notes' not in plain
    # Everything else about the member is still visible — they are a colleague
    # at the same branch, not a stranger.
    assert plain['full_name'] == 'Plain Gym Member'


def test_the_members_list_applies_the_same_rule(app, captain):
    body = app.test_client().get('/api/customers?per_page=100',
                                 headers=captain).get_json()['data']
    by_id = {row['id']: row for row in body['items']}

    assert 'weight' in by_id[IDS['mine']]
    assert 'weight' not in by_id[IDS['plain']]
    assert 'weight' not in by_id[IDS['theirs']]


def test_reception_still_sees_health_data(app, desk):
    """The people who record it must keep seeing it."""
    data = app.test_client().get(f"/api/customers/{IDS['plain']}",
                                 headers=desk).get_json()['data']
    assert data['weight'] is not None
    assert data['bmi'] is not None


# ──────────────────────────── the message centre ────────────────────────────

def test_a_captain_and_their_client_can_talk(app, captain):
    client = app.test_client()
    member = _member(app, '01777000111')

    sent = client.post(f"/api/private-training/messages/{IDS['mine']}",
                       json={'body': 'See you at 6pm for legs.'}, headers=captain)
    assert sent.status_code == 201, sent.get_json()

    thread = client.get(f'/api/client/messages/{IDS["captain"]}',
                        headers=member).get_json()['data']
    assert [m['body'] for m in thread['items']] == ['See you at 6pm for legs.']
    assert thread['items'][0]['sender'] == 'trainer'
    assert thread['can_send'] is True

    replied = client.post(f'/api/client/messages/{IDS["captain"]}',
                          json={'body': 'I will be there.'}, headers=member)
    assert replied.status_code == 201, replied.get_json()

    back = client.get(f"/api/private-training/messages/{IDS['mine']}",
                      headers=captain).get_json()['data']
    assert [m['body'] for m in back['items']] == [
        'See you at 6pm for legs.', 'I will be there.'
    ]


def test_a_captain_cannot_message_someone_elses_client(app, captain):
    r = app.test_client().post(f"/api/private-training/messages/{IDS['theirs']}",
                               json={'body': 'hello'}, headers=captain)
    assert r.status_code == 403, r.get_json()


def test_a_captain_cannot_message_a_member_with_no_private_training(app, captain):
    r = app.test_client().post(f"/api/private-training/messages/{IDS['plain']}",
                               json={'body': 'hello'}, headers=captain)
    assert r.status_code == 403, r.get_json()


def test_a_member_cannot_message_a_captain_they_do_not_train_with(app):
    r = app.test_client().post(f'/api/client/messages/{IDS["other_captain"]}',
                               json={'body': 'hello'},
                               headers=_member(app, '01777000111'))
    assert r.status_code == 403, r.get_json()


def test_a_stranger_cannot_read_the_conversation(app):
    """Reading someone else's thread by guessing the id in the path."""
    r = app.test_client().get(f'/api/client/messages/{IDS["captain"]}',
                              headers=_member(app, '01777000333'))
    assert r.status_code == 404, r.get_json()


def test_a_lapsed_client_keeps_the_thread_but_loses_the_composer(app, captain):
    """Deleting the conversation the day a package expires would be a worse
    answer than letting it go quiet."""
    from app.extensions import db
    from app.models.message import Message, MessageSender

    with app.app_context():
        db.session.add(Message(
            trainer_id=IDS['captain'], customer_id=IDS['lapsed'],
            sender=MessageSender.TRAINER, body='Well done on the last block.',
            branch_id=IDS['branch'],
        ))
        db.session.commit()

    thread = app.test_client().get(
        f"/api/private-training/messages/{IDS['lapsed']}",
        headers=captain).get_json()['data']

    assert [m['body'] for m in thread['items']] == ['Well done on the last block.']
    assert thread['can_send'] is False, (
        'the composer stayed open after the coaching relationship ended'
    )

    blocked = app.test_client().post(
        f"/api/private-training/messages/{IDS['lapsed']}",
        json={'body': 'and another thing'}, headers=captain)
    assert blocked.status_code == 403


def test_an_empty_or_enormous_message_is_refused(app, captain):
    client = app.test_client()
    assert client.post(f"/api/private-training/messages/{IDS['mine']}",
                       json={'body': '   '}, headers=captain).status_code == 400
    assert client.post(f"/api/private-training/messages/{IDS['mine']}",
                       json={'body': 'x' * 2001}, headers=captain).status_code == 400


def test_unread_counts_are_per_thread_and_clear_on_read(app, captain):
    client = app.test_client()
    member = _member(app, '01777000111')

    client.post(f'/api/client/messages/{IDS["captain"]}',
                json={'body': 'One question about my diet'}, headers=member)

    threads = client.get('/api/private-training/messages/threads',
                         headers=captain).get_json()['data']
    mine = next(t for t in threads['items'] if t['customer_id'] == IDS['mine'])
    assert mine['unread_count'] >= 1
    assert mine['last_message']['body'] == 'One question about my diet'
    assert threads['total_unread'] >= 1

    client.get(f"/api/private-training/messages/{IDS['mine']}", headers=captain)

    after = client.get('/api/private-training/messages/threads',
                       headers=captain).get_json()['data']
    mine_after = next(t for t in after['items'] if t['customer_id'] == IDS['mine'])
    assert mine_after['unread_count'] == 0


def test_a_captains_thread_list_shows_clients_with_no_messages_yet(app, app_owner=None):
    """A list of only existing threads gives the captain nowhere to start one."""
    from app.extensions import db
    from app.models.customer import Customer
    from app.models.service import Service
    from app.models.subscription import Subscription, SubscriptionStatus

    with app.app_context():
        fresh = Customer(full_name='Brand New Client', phone='01777000555',
                         branch_id=IDS['branch'], is_active=True)
        fresh.set_password('secret123')
        db.session.add(fresh)
        db.session.flush()
        service = Service.query.filter_by(name='PT Package').first()
        db.session.add(Subscription(
            customer_id=fresh.id, service_id=service.id, branch_id=IDS['branch'],
            trainer_id=IDS['captain'],
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            status=SubscriptionStatus.ACTIVE,
        ))
        db.session.commit()
        fresh_id = fresh.id

    threads = app.test_client().get(
        '/api/private-training/messages/threads',
        headers=_staff(app, 'captain_ali')).get_json()['data']

    entry = next((t for t in threads['items'] if t['customer_id'] == fresh_id), None)
    assert entry is not None, 'a client with no messages is missing from the list'
    assert entry['last_message'] is None
    assert entry['unread_count'] == 0


def test_erasing_an_account_takes_the_health_and_the_conversations(app):
    from app.extensions import db
    from app.models.body_measurement import BodyMeasurement
    from app.models.customer import Customer
    from app.models.message import Message
    from app.services.retention_service import anonymise

    with app.app_context():
        assert BodyMeasurement.query.filter_by(customer_id=IDS['mine']).count() > 0
        assert Message.query.filter_by(customer_id=IDS['mine']).count() > 0

        anonymise(db.session.get(Customer, IDS['mine']))
        db.session.commit()

        assert BodyMeasurement.query.filter_by(customer_id=IDS['mine']).count() == 0
        assert Message.query.filter_by(customer_id=IDS['mine']).count() == 0
