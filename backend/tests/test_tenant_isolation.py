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
        _make_tenant('A')
        _make_tenant('B')
    return application


def _make_tenant(name):
    """One gym: an owner, a branch, a member, and one of every record type
    that is scoped by branch — including the money ones, which is where a
    hand-rolled filter is most expensive to get wrong."""
    from app.extensions import db
    from app.models.branch import Branch
    from app.models.complaint import Complaint, ComplaintStatus, ComplaintType
    from app.models.customer import Customer
    from app.models.daily_closing import DailyClosing
    from app.models.expense import Expense, ExpenseCategory
    from app.models.gym import Gym
    from app.models.service import Service, ServiceType
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.transaction import (
        Transaction, PaymentMethod, TransactionType,
    )
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

    member = Customer(full_name=f'Member {name}', phone=f'0{name}0000000',
                      branch_id=branch.id, is_active=True)
    db.session.add(member)
    db.session.flush()
    db.session.add(Complaint(title=f'Complaint {name}',
                             description=f'description for {name}',
                             complaint_type=ComplaintType.SERVICE,
                             branch_id=branch.id, status=ComplaintStatus.OPEN))
    db.session.add(Expense(title=f'Expense {name}', description=f'Expense {name}',
                           amount=100, category=ExpenseCategory.OTHER,
                           branch_id=branch.id, created_by_id=owner.id,
                           expense_date=date.today()))
    db.session.add(Transaction(
        amount=250, discount=0, payment_method=PaymentMethod.CASH,
        transaction_type=TransactionType.SUBSCRIPTION, branch_id=branch.id,
        created_by=owner.id, description=f'Transaction {name}',
    ))

    service = Service(name=f'Service {name}', service_type=ServiceType.GYM,
                      price=500, duration_days=30, allowed_days_per_week=7)
    db.session.add(service)
    db.session.flush()
    db.session.add(Subscription(
        customer_id=member.id, service_id=service.id, branch_id=branch.id,
        start_date=date.today(), end_date=date.today() + timedelta(days=30),
        status=SubscriptionStatus.ACTIVE, subscription_type='time_based',
    ))
    db.session.add(DailyClosing(
        branch_id=branch.id, closing_date=date.today(),
        expected_cash=250, actual_cash=250, cash_difference=0,
        network_total=0, transfer_total=0, total_revenue=250,
        closed_by=owner.id, notes=f'Closing {name}',
    ))
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
    # Money. Every one of these is branch-scoped and none of them was covered,
    # which is how a hand-rolled filter in transactions_routes survived.
    ('/api/transactions', 'Transaction'),
    ('/api/payments', 'Transaction'),
    ('/api/daily-closings', 'Closing'),
    ('/api/finance/cash-differences', 'Closing'),
    ('/api/subscriptions', 'Member'),
]


@pytest.mark.parametrize('endpoint,label', SCOPED_ENDPOINTS)
def test_owner_cannot_see_other_gyms_data(app, owner_a_headers, endpoint, label):
    body = str(app.test_client().get(endpoint, headers=owner_a_headers).get_json())
    assert f'{label} B' not in body, f'{endpoint} leaked gym B data'


def test_no_endpoint_returns_a_record_from_another_gyms_branch(app, owner_a_headers):
    """Names are not a reliable tell.

    /api/subscriptions leaked every gym's rows and the name-based check above
    passed anyway, because its schema serialises ids only. Branch id is on
    every one of these payloads and cannot be omitted.
    """
    from app.extensions import db
    from app.models.branch import Branch
    from app.models.gym import Gym

    with app.app_context():
        gym_a = Gym.query.filter_by(name='Gym A').one()
        own = {b.id for b in Branch.query.filter_by(gym_id=gym_a.id).all()}
        foreign = {b.id for b in Branch.query.filter(Branch.gym_id != gym_a.id).all()}

    client = app.test_client()
    for endpoint, _label in SCOPED_ENDPOINTS:
        payload = client.get(endpoint, headers=owner_a_headers).get_json()
        seen = _branch_ids(payload)
        assert not (seen & foreign), (
            f'{endpoint} returned rows from branches {sorted(seen & foreign)}, '
            f'outside this owner\'s gym {sorted(own)}'
        )


def _branch_ids(node):
    """Every branch_id anywhere in a response payload."""
    found = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key == 'branch_id' and isinstance(value, int):
                found.add(value)
            else:
                found |= _branch_ids(value)
    elif isinstance(node, list):
        for item in node:
            found |= _branch_ids(item)
    return found


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
    # 750 net from the discounted subscription above (1000 - 250), plus the
    # flat 250 cash transaction every tenant gets in _make_tenant.
    assert dashboard_revenue == pytest.approx(1000.0)


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
