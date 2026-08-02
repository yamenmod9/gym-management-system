"""Door entry when a member holds more than one subscription.

Members can hold several subscriptions at once — gym entry, private training
with a named captain, or a package covering both. Every check-in path used to
take the *first* active one it found, so a member holding gym + training could
have a door scan deduct a session from their training package instead.

The four scenarios below are the rules the gym actually operates by:

    gym + training  -> in, on the gym subscription
    gym only        -> in
    training only   -> refused (it buys a captain's time, not floor access)
    combined package-> in

Plus the owner override that lets a gym admit training-only members if that is
how they run the place.

Run with:  pytest backend/tests/test_multi_subscription.py
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
        'sqlite:///' + tempfile.mktemp(suffix='.db').replace('\\', '/')
    )
    from app import create_app
    from app.extensions import db

    application = create_app('development')
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
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.user import User, UserRole

    owner = User(username='owner_ms', email='ms@example.com', full_name='Owner',
                 role=UserRole.OWNER, is_active=True)
    owner.set_password('secret123')
    db.session.add(owner)
    db.session.flush()

    gym = Gym(name='MS Gym', owner_id=owner.id, is_setup_complete=True)
    db.session.add(gym)
    db.session.flush()
    owner.gym_id = gym.id

    branch = Branch(name='Main', code='MS1', gym_id=gym.id, is_active=True)
    db.session.add(branch)
    db.session.flush()

    trainer = User(username='cap_ms', email='cap@example.com', full_name='Captain',
                   role=UserRole.TRAINER, gym_id=gym.id, branch_id=branch.id,
                   is_active=True)
    trainer.set_password('secret123')
    db.session.add(trainer)

    gym_svc = Service(name='Gym', service_type=ServiceType.GYM, price=500,
                      duration_days=30, allowed_days_per_week=7,
                      grants_gym_entry=True)
    pt_svc = Service(name='PT', service_type=ServiceType.PERSONAL_TRAINING,
                     price=2000, duration_days=90, allowed_days_per_week=7,
                     grants_gym_entry=False)
    combo = Service(name='Combo', service_type=ServiceType.BUNDLE, price=2400,
                    duration_days=90, allowed_days_per_week=7,
                    grants_gym_entry=True)
    db.session.add_all([gym_svc, pt_svc, combo])
    db.session.flush()

    def member(name, services):
        customer = Customer(full_name=name, phone=f'01{abs(hash(name)) % 100000000:08d}',
                            branch_id=branch.id, is_active=True)
        db.session.add(customer)
        db.session.flush()
        for svc in services:
            db.session.add(Subscription(
                customer_id=customer.id, service_id=svc.id, branch_id=branch.id,
                start_date=date.today(), end_date=date.today() + timedelta(days=30),
                status=SubscriptionStatus.ACTIVE,
                subscription_type='sessions' if svc is pt_svc else 'coins',
                remaining_coins=None if svc is pt_svc else 10,
                remaining_sessions=10 if svc is pt_svc else None,
                trainer_id=trainer.id if svc is pt_svc else None,
            ))
        db.session.flush()
        return customer

    globals()['IDS'] = {
        'both': member('Both', [gym_svc, pt_svc]).id,
        'gym_only': member('Gym Only', [gym_svc]).id,
        'pt_only': member('PT Only', [pt_svc]).id,
        'combo': member('Combo Holder', [combo]).id,
        'gym_id': gym.id,
        'gym_service_id': gym_svc.id,
        'combo_service_id': combo.id,
    }
    db.session.commit()


@pytest.mark.parametrize('who, admitted, expected_service_key', [
    ('both', True, 'gym_service_id'),
    ('gym_only', True, 'gym_service_id'),
    ('pt_only', False, None),
    ('combo', True, 'combo_service_id'),
])
def test_door_entry_scenarios(app, who, admitted, expected_service_key):
    """The four ways a member can be subscribed, and who gets through."""
    from app.models.subscription import Subscription

    with app.app_context():
        found = Subscription.entry_subscription_for(IDS[who])
        assert (found is not None) is admitted, (
            f'{who}: expected admitted={admitted}'
        )
        if admitted:
            # The *right* subscription, not merely any one. A member holding
            # gym + training must be metered on the gym package.
            assert found.service_id == IDS[expected_service_key]


def test_training_package_is_never_the_one_metered_at_the_door(app):
    """The specific regression: gym + training must not meter the training."""
    from app.extensions import db
    from app.models.service import Service
    from app.models.subscription import Subscription

    with app.app_context():
        found = Subscription.entry_subscription_for(IDS['both'])
        service = db.session.get(Service, found.service_id)
        assert service.grants_gym_entry is True
        assert service.service_type.value != 'personal_training'


def test_owner_can_admit_training_only_members(app):
    """The override rule flips scenario 3 without touching the others."""
    from app.models.subscription import Subscription
    from app.services.gym_rules import gym_rule, set_rules

    with app.app_context():
        assert Subscription.entry_subscription_for(IDS['pt_only']) is None

        set_rules(IDS['gym_id'], {'pt_only_members_may_enter': True})
        allow = gym_rule(IDS['gym_id'], 'pt_only_members_may_enter')
        assert allow is True
        assert Subscription.entry_subscription_for(
            IDS['pt_only'], allow_non_entry=allow
        ) is not None

        # Members who already had entry are unaffected by the override.
        assert Subscription.entry_subscription_for(
            IDS['both'], allow_non_entry=allow
        ).service_id == IDS['gym_service_id']

        set_rules(IDS['gym_id'], {'pt_only_members_may_enter': False})


def test_active_for_returns_every_subscription(app):
    """Display paths must show the whole picture, not one arbitrary row."""
    from app.models.subscription import Subscription

    with app.app_context():
        assert len(Subscription.active_for(IDS['both'])) == 2
        assert len(Subscription.active_for(IDS['gym_only'])) == 1


def test_unknown_gym_rule_is_rejected(app):
    """A typo in a rule name must fail loudly rather than silently default."""
    from app.services.gym_rules import gym_rule

    with app.app_context():
        with pytest.raises(KeyError):
            gym_rule(IDS['gym_id'], 'no_such_rule')


def test_rules_fall_back_to_defaults_for_a_gym_that_never_set_them(app):
    """A gym that has never opened the settings screen still behaves sanely."""
    from app.services.gym_rules import RULES, gym_rule

    with app.app_context():
        for key, (default, _en, _ar) in RULES.items():
            assert gym_rule(999999, key) == default
