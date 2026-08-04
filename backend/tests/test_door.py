"""The door: biometrics and who may open it.

Phase 3 of the project audit. The highest-frequency path in the product — every
member, every visit — and the place where a mistake lets the wrong person in.

Run with:  pytest backend/tests/test_door.py
"""
import os
import sys
import tempfile
from datetime import date, timedelta

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
    from app.models.fingerprint import Fingerprint
    from app.models.gym import Gym
    from app.models.service import Service, ServiceType
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.user import User, UserRole

    ids = {}
    service = Service(name='Door Gym', service_type=ServiceType.GYM, price=500,
                      duration_days=30, allowed_days_per_week=7,
                      grants_gym_entry=True)
    db.session.add(service)
    db.session.flush()

    for tag in ('D', 'E'):
        owner = User(username=f'downer_{tag}', email=f'd{tag}@example.com',
                     full_name=f'Owner {tag}', role=UserRole.OWNER, is_active=True)
        owner.set_password('secret123')
        db.session.add(owner)
        db.session.flush()

        gym = Gym(name=f'Door Gym {tag}', owner_id=owner.id, is_setup_complete=True)
        db.session.add(gym)
        db.session.flush()
        owner.gym_id = gym.id

        branch = Branch(name=f'Branch {tag}', code=f'D{tag}', gym_id=gym.id,
                        is_active=True)
        db.session.add(branch)
        db.session.flush()
        owner.branch_id = branch.id

        desk = User(username=f'ddesk_{tag}', email=f'ddesk{tag}@example.com',
                    full_name=f'Desk {tag}', role=UserRole.FRONT_DESK,
                    gym_id=gym.id, branch_id=branch.id, is_active=True)
        desk.set_password('secret123')
        db.session.add(desk)

        member = Customer(full_name=f'Door Member {tag}', phone=f'077{tag}000000',
                          branch_id=branch.id, is_active=True)
        db.session.add(member)
        db.session.flush()

        db.session.add(Subscription(
            customer_id=member.id, service_id=service.id, branch_id=branch.id,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            status=SubscriptionStatus.ACTIVE, subscription_type='time_based',
        ))

        print_hash = f'fp-hash-{tag}'
        db.session.add(Fingerprint(
            customer_id=member.id, fingerprint_hash=print_hash,
            template_hash=f'tmpl-{tag}', is_active=True,
        ))
        db.session.flush()

        ids[tag] = {'gym': gym.id, 'branch': branch.id, 'member': member.id,
                    'hash': print_hash}

    trainer = User(username='dtrainer_D', email='dtr@example.com',
                   full_name='Captain D', role=UserRole.TRAINER,
                   gym_id=ids['D']['gym'], branch_id=ids['D']['branch'],
                   is_active=True)
    trainer.set_password('secret123')
    db.session.add(trainer)

    db.session.commit()
    globals()['IDS'] = ids


def _headers(app, username):
    response = app.test_client().post(
        '/api/auth/login', json={'username': username, 'password': 'secret123'})
    assert response.status_code == 200, response.get_json()
    return {'Authorization': 'Bearer ' + response.get_json()['data']['access_token']}


@pytest.fixture
def desk_d(app):
    return _headers(app, 'ddesk_D')


# ────────────────────────────── biometrics ──────────────────────────────────

def test_validating_a_fingerprint_requires_authentication(app):
    """It was a public endpoint: hand it a hash and it opened the door and
    returned the member's full profile."""
    response = app.test_client().post(
        '/api/fingerprints/validate', json={'fingerprint_hash': IDS['D']['hash']})
    assert response.status_code in (401, 422), response.get_json()


def test_a_trainer_cannot_open_a_door_or_list_prints(app):
    headers = _headers(app, 'dtrainer_D')
    client = app.test_client()

    assert client.get('/api/fingerprints', headers=headers).status_code == 403
    assert client.post('/api/fingerprints/validate',
                       json={'fingerprint_hash': IDS['D']['hash']},
                       headers=headers).status_code == 403


def test_the_listing_never_hands_out_the_hash_that_opens_the_door(app, desk_d):
    """The listing dumped fingerprint_hash, which is exactly what /validate
    accepts — so reading this endpoint produced a working key."""
    body = app.test_client().get('/api/fingerprints', headers=desk_d).get_json()
    assert IDS['D']['hash'] not in str(body), (
        'the credential is still being handed out'
    )


def test_one_gyms_prints_are_invisible_to_another(app, desk_d):
    body = app.test_client().get('/api/fingerprints', headers=desk_d).get_json()
    ids_returned = [row['customer_id'] for row in body['data']['items']]
    assert IDS['E']['member'] not in ids_returned
    assert IDS['D']['member'] in ids_returned


def test_a_reader_cannot_admit_another_gyms_member(app, desk_d):
    response = app.test_client().post(
        '/api/fingerprints/validate',
        json={'fingerprint_hash': IDS['E']['hash']}, headers=desk_d)
    assert response.status_code == 404, response.get_json()


def test_the_desk_can_still_admit_its_own_member(app, desk_d):
    """Fails closed — prove the lock-down did not shut the door on everyone."""
    response = app.test_client().post(
        '/api/fingerprints/validate',
        json={'fingerprint_hash': IDS['D']['hash']}, headers=desk_d)
    assert response.status_code == 200, response.get_json()
    assert response.get_json()['data']['access_granted'] is True


def test_a_desk_cannot_enrol_a_biometric_for_another_gyms_member(app, desk_d):
    response = app.test_client().post(
        '/api/fingerprints/register',
        json={'customer_id': IDS['E']['member'], 'unique_data': 'stolen-biometric-data'},
        headers=desk_d)
    assert response.status_code == 404, response.get_json()


def test_a_desk_cannot_reactivate_another_gyms_print(app, desk_d):
    """Reactivating one deactivated for cause is the dangerous direction."""
    from app.extensions import db
    from app.models.fingerprint import Fingerprint

    with app.app_context():
        foreign = Fingerprint.query.filter_by(
            customer_id=IDS['E']['member']).first()
        foreign_id = foreign.id

    response = app.test_client().post(
        f'/api/fingerprints/{foreign_id}/reactivate', headers=desk_d)
    assert response.status_code == 404, response.get_json()
