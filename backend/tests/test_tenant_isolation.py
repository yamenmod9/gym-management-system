"""Tenant isolation and session-revocation regression tests.

These cover two bugs that were live in production:

1. ``get_accessible_branch_ids`` returned None for owners, meaning "no branch
   filter". Seven route modules scope only by branch, so the owner of one gym
   could read every other gym's members, complaints and expenses.
2. Only ``role_required`` checked ``is_active``; routes guarded by a bare
   ``@jwt_required()`` kept working for a deactivated account until its token
   expired.

Both fixes fail closed, so each test asserts the *positive* case too — that
the owner still sees their own gym. A fix that isolates tenants by locking
everyone out would otherwise pass.

Run with:  pytest backend/tests/test_tenant_isolation.py
"""
import os
import sys
import tempfile
from datetime import date

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
        _make_tenant('A')
        _make_tenant('B')
    return application


def _make_tenant(name):
    """One gym: an owner, a branch, a member, a complaint and an expense."""
    from app.extensions import db
    from app.models.branch import Branch
    from app.models.complaint import Complaint, ComplaintStatus, ComplaintType
    from app.models.customer import Customer
    from app.models.expense import Expense, ExpenseCategory
    from app.models.gym import Gym
    from app.models.user import User, UserRole

    owner = User(username=f'owner_{name}', email=f'{name}@example.com',
                 full_name=f'Owner {name}', role=UserRole.OWNER, is_active=True)
    owner.set_password('secret123')
    db.session.add(owner)
    db.session.flush()

    gym = Gym(name=f'Gym {name}', owner_id=owner.id, is_setup_complete=True)
    db.session.add(gym)
    db.session.flush()

    owner.gym_id = gym.id
    branch = Branch(name=f'Branch {name}', code=f'BR{name}', gym_id=gym.id,
                    address='addr', phone='1')
    db.session.add(branch)
    db.session.flush()

    db.session.add(Customer(full_name=f'Member {name}', phone=f'0{name}0000000',
                            branch_id=branch.id, is_active=True))
    db.session.add(Complaint(title=f'Complaint {name}',
                             description=f'description for {name}',
                             complaint_type=ComplaintType.SERVICE,
                             branch_id=branch.id, status=ComplaintStatus.OPEN))
    db.session.add(Expense(title=f'Expense {name}', description=f'Expense {name}',
                           amount=100, category=ExpenseCategory.OTHER,
                           branch_id=branch.id, created_by_id=owner.id,
                           expense_date=date.today()))
    db.session.commit()


@pytest.fixture
def owner_a_headers(app):
    client = app.test_client()
    response = client.post('/api/auth/login',
                           json={'username': 'owner_A', 'password': 'secret123'})
    assert response.status_code == 200, response.get_json()
    token = response.get_json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


SCOPED_ENDPOINTS = [
    ('/api/customers', 'Member'),
    ('/api/complaints', 'Complaint'),
    ('/api/expenses', 'Expense'),
    ('/api/finance/expenses', 'Expense'),
    ('/api/branches', 'Branch'),
]


@pytest.mark.parametrize('endpoint,label', SCOPED_ENDPOINTS)
def test_owner_cannot_see_other_gyms_data(app, owner_a_headers, endpoint, label):
    body = str(app.test_client().get(endpoint, headers=owner_a_headers).get_json())
    assert f'{label} B' not in body, f'{endpoint} leaked gym B data'


@pytest.mark.parametrize('endpoint,label', SCOPED_ENDPOINTS)
def test_owner_still_sees_own_gyms_data(app, owner_a_headers, endpoint, label):
    """The isolation fix fails closed — make sure it did not over-restrict."""
    body = str(app.test_client().get(endpoint, headers=owner_a_headers).get_json())
    assert f'{label} A' in body, f'{endpoint} hid the owner\'s own data'


def test_deactivating_a_user_revokes_their_live_token(app, owner_a_headers):
    from app.extensions import db
    from app.models.user import User

    client = app.test_client()
    assert client.get('/api/customers', headers=owner_a_headers).status_code == 200

    with app.app_context():
        owner = User.query.filter_by(username='owner_A').one()
        owner.is_active = False
        db.session.commit()
    try:
        response = client.get('/api/customers', headers=owner_a_headers)
        # 401, not 403: the clients force a logout on 401 but only show a
        # "no permission" toast on 403.
        assert response.status_code == 401, response.get_json()
    finally:
        with app.app_context():
            owner = User.query.filter_by(username='owner_A').one()
            owner.is_active = True
            db.session.commit()


def test_unauthenticated_routes_are_unaffected_by_the_active_guard(app):
    """A stale token in the header must not block logging in again."""
    response = app.test_client().post(
        '/api/auth/login',
        json={'username': 'owner_A', 'password': 'wrong-password'},
        headers={'Authorization': 'Bearer garbage.token.here'},
    )
    assert response.status_code == 401


def test_dashboard_and_report_revenue_agree(app):
    """Revenue must be net of discount everywhere it is shown.

    The dashboards summed the gross `amount` while the reports subtracted
    `discount`, so the owner's headline figure read higher than the report for
    the same period by exactly the discounts given.
    """
    from datetime import date, timedelta

    from app.extensions import db
    from app.models.branch import Branch
    from app.models.customer import Customer
    from app.models.service import Service, ServiceType
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.transaction import (
        PaymentMethod, Transaction, TransactionType)
    from app.models.user import User

    with app.app_context():
        owner = User.query.filter_by(username='owner_A').one()
        branch = Branch.query.filter_by(code='BRA').one()
        customer = Customer.query.filter_by(full_name='Member A').one()

        service = Service(name='Net check', service_type=ServiceType.GYM,
                          price=1000, duration_days=30, is_active=True)
        db.session.add(service)
        db.session.flush()

        subscription = Subscription(
            customer_id=customer.id, service_id=service.id, branch_id=branch.id,
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
            status=SubscriptionStatus.ACTIVE, subscription_type='coins',
            remaining_coins=10, total_coins=10)
        db.session.add(subscription)
        db.session.flush()

        # Gross 1000 with 250 discounted away — net revenue is 750.
        db.session.add(Transaction(
            amount=1000, discount=250, payment_method=PaymentMethod.CASH,
            transaction_type=TransactionType.SUBSCRIPTION, branch_id=branch.id,
            customer_id=customer.id, subscription_id=subscription.id,
            created_by=owner.id))
        db.session.commit()

    client = app.test_client()
    login = client.post('/api/auth/login',
                        json={'username': 'owner_A', 'password': 'secret123'})
    headers = {'Authorization': 'Bearer ' + login.get_json()['data']['access_token']}

    dashboard = client.get('/api/dashboards/owner', headers=headers).get_json()
    report = client.get('/api/reports/revenue', headers=headers).get_json()

    dashboard_revenue = dashboard['data']['revenue']['total_30_days']
    report_revenue = report['data']['total_revenue']

    assert dashboard_revenue == pytest.approx(report_revenue), (
        f'dashboard says {dashboard_revenue}, report says {report_revenue}'
    )
    assert dashboard_revenue == pytest.approx(750.0)


def test_role_notifications_do_not_cross_gyms(app):
    """notify_role must not push one gym's events to another gym's staff.

    Filing a complaint pushes its title to owners and branch managers. Before
    this was scoped, that broadcast reached every holder of the role on the
    platform, so one gym's complaint text landed on every other gym's phones.
    """
    from app.extensions import db
    from app.models.device_token import DeviceToken
    from app.models.gym import Gym
    from app.models.user import User

    sent_to = []

    with app.app_context():
        owner_a = User.query.filter_by(username='owner_A').one()
        owner_b = User.query.filter_by(username='owner_B').one()
        for owner in (owner_a, owner_b):
            db.session.add(DeviceToken(
                user_id=owner.id, fcm_token=f'token-{owner.username}',
                app_type='staff', platform='android', is_active=True))
        db.session.commit()
        gym_a_id = Gym.query.filter_by(owner_id=owner_a.id).one().id

    import app.services.fcm_service as fcm

    original = fcm.send_push_to_tokens

    def capture(tokens, *args, **kwargs):
        sent_to.extend(tokens)
        return len(tokens)

    fcm.send_push_to_tokens = capture
    try:
        with app.app_context():
            fcm.notify_role('owner', 'title', 'body', gym_id=gym_a_id)
    finally:
        fcm.send_push_to_tokens = original

    assert 'token-owner_A' in sent_to, 'gym A owner should have been notified'
    assert 'token-owner_B' not in sent_to, "gym B's owner was notified about gym A"
