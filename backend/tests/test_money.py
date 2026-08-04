"""Money: takings, expenses, and the daily cash reconciliation.

Phase 4 of the project audit. This is the largest body of code in the system
that had no tests at all, and it is the code that decides what a branch says it
earned and whether the till balances.

Run with:  pytest backend/tests/test_money.py
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
    from app.models.transaction import (
        Transaction, PaymentMethod, TransactionType,
    )
    from app.models.user import User, UserRole

    ids = {}

    for tag in ('X', 'Y'):
        owner = User(username=f'mowner_{tag}', email=f'm{tag}@example.com',
                     full_name=f'Owner {tag}', role=UserRole.OWNER, is_active=True)
        owner.set_password('secret123')
        db.session.add(owner)
        db.session.flush()

        gym = Gym(name=f'Money Gym {tag}', owner_id=owner.id, is_setup_complete=True)
        db.session.add(gym)
        db.session.flush()
        owner.gym_id = gym.id

        branch = Branch(name=f'Branch {tag}', code=f'M{tag}', gym_id=gym.id,
                        is_active=True)
        db.session.add(branch)
        db.session.flush()
        owner.branch_id = branch.id

        customer = Customer(full_name=f'Member {tag}', phone=f'09{tag}0000000',
                            branch_id=branch.id, is_active=True)
        db.session.add(customer)
        db.session.flush()

        # Two takings on a known day: one discounted, one not.
        # Net for the day is (1000 - 250) + 500 = 1250; gross is 1500.
        day = datetime(2026, 3, 10, 12, 0, 0)
        db.session.add(Transaction(
            amount=1000, discount=250, payment_method=PaymentMethod.CASH,
            transaction_type=TransactionType.SUBSCRIPTION, branch_id=branch.id,
            customer_id=customer.id, created_by=owner.id,
            description=f'Discounted {tag}',
            transaction_date=day, created_at=day,
        ))
        db.session.add(Transaction(
            amount=500, discount=0, payment_method=PaymentMethod.NETWORK,
            transaction_type=TransactionType.SUBSCRIPTION, branch_id=branch.id,
            customer_id=customer.id, created_by=owner.id,
            description=f'Full price {tag}',
            transaction_date=day, created_at=day,
        ))

        ids[tag] = {'gym': gym.id, 'branch': branch.id, 'owner': owner.id}

    # A trainer and an accountant in gym X, to pin who may read the books.
    trainer = User(username='mtrainer_X', email='mtx@example.com',
                   full_name='Captain X', role=UserRole.TRAINER,
                   gym_id=ids['X']['gym'], branch_id=ids['X']['branch'],
                   is_active=True)
    trainer.set_password('secret123')
    accountant = User(username='macct_X', email='mac@example.com',
                      full_name='Accountant X', role=UserRole.BRANCH_ACCOUNTANT,
                      gym_id=ids['X']['gym'], branch_id=ids['X']['branch'],
                      is_active=True)
    accountant.set_password('secret123')
    db.session.add_all([trainer, accountant])

    db.session.commit()
    globals()['IDS'] = ids


def _headers(app, username):
    response = app.test_client().post(
        '/api/auth/login', json={'username': username, 'password': 'secret123'})
    assert response.status_code == 200, response.get_json()
    return {'Authorization': 'Bearer ' + response.get_json()['data']['access_token']}


@pytest.fixture
def owner_x(app):
    return _headers(app, 'mowner_X')


@pytest.fixture
def trainer_x(app):
    return _headers(app, 'mtrainer_X')


@pytest.fixture
def accountant_x(app):
    return _headers(app, 'macct_X')


# ───────────────────────── who may read the books ───────────────────────────

MONEY_READ_ENDPOINTS = [
    '/api/transactions',
    '/api/payments',
    '/api/expenses',
    '/api/finance/expenses',
    '/api/finance/daily-sales',
    '/api/finance/cash-differences',
    '/api/daily-closings',
]


@pytest.mark.parametrize('endpoint', MONEY_READ_ENDPOINTS)
def test_a_trainer_cannot_read_the_books(app, trainer_x, endpoint):
    """A captain's job is members and sessions, not takings.

    Every one of these carries amounts, discounts and who paid what. Most were
    guarded by a bare @jwt_required(), which any staff login satisfies.
    """
    response = app.test_client().get(endpoint, headers=trainer_x)
    assert response.status_code == 403, (
        f'{endpoint} returned {response.status_code} to a trainer'
    )


@pytest.mark.parametrize('endpoint', MONEY_READ_ENDPOINTS)
def test_an_accountant_still_can(app, accountant_x, endpoint):
    """The lock-down must not lock out the people whose job this is."""
    response = app.test_client().get(endpoint, headers=accountant_x)
    assert response.status_code == 200, (
        f'{endpoint} returned {response.status_code} to a branch accountant: '
        f'{response.get_json()}'
    )


# ──────────────────────────── tenant isolation ──────────────────────────────

def test_daily_sales_does_not_total_another_gyms_takings(app, owner_x):
    """Gym X and gym Y each took 1250 net that day. X must see 1250, not 2500."""
    response = app.test_client().get(
        '/api/finance/daily-sales?date=2026-03-10', headers=owner_x)
    assert response.status_code == 200, response.get_json()
    data = response.get_json()['data']

    assert data['total_sales'] == pytest.approx(1250.0), (
        'daily sales summed every gym on the platform'
    )
    assert data['transaction_count'] == 2


# ─────────────────────────── net vs gross revenue ───────────────────────────

def test_payments_total_is_net_of_discount_and_covers_the_whole_range(app, owner_x):
    """The listed total must mean what every other revenue figure means.

    Two traps here: it summed the gross `amount`, so it read high by exactly
    the discounts given; and it summed only the rows on the current page while
    sitting next to a `total` count for the whole set, so it changed as you
    paged.
    """
    client = app.test_client()

    full = client.get('/api/payments?date_from=2026-03-10&date_to=2026-03-10',
                      headers=owner_x).get_json()['data']
    assert full['total_amount'] == pytest.approx(1250.0), (
        'expected net revenue (1000-250) + 500'
    )

    # One row per page — the reported total must not shrink to that row.
    paged = client.get(
        '/api/payments?date_from=2026-03-10&date_to=2026-03-10&limit=1',
        headers=owner_x).get_json()['data']
    assert paged['total_amount'] == pytest.approx(full['total_amount']), (
        'the total changed when the page size did'
    )


def test_a_single_day_range_includes_that_day(app, owner_x):
    """date_to is a day, not an instant.

    Parsed as midnight and compared with <=, `date_to=2026-03-10` excluded
    everything that happened on the 10th — so asking for one day returned
    nothing at all.
    """
    response = app.test_client().get(
        '/api/payments?date_from=2026-03-10&date_to=2026-03-10', headers=owner_x)
    body = response.get_json()['data']
    assert body['pagination']['total'] == 2, (
        'a same-day from/to range returned nothing'
    )


# ─────────────────────── the daily cash reconciliation ──────────────────────

def test_expected_cash_is_net_and_split_by_method(app, owner_x):
    response = app.test_client().post(
        '/api/daily-closings/calculate',
        json={'branch_id': IDS['X']['branch'], 'date': '2026-03-10'},
        headers=owner_x)
    assert response.status_code == 200, response.get_json()
    data = response.get_json()['data']

    assert data['expected_cash'] == pytest.approx(750.0)   # 1000 - 250
    assert data['network_total'] == pytest.approx(500.0)
    assert data['total_revenue'] == pytest.approx(1250.0)


def test_a_non_numeric_cash_count_is_rejected_not_a_500(app, owner_x):
    """The till count is typed by a human at the end of a shift."""
    response = app.test_client().post(
        '/api/daily-closings',
        json={'branch_id': IDS['X']['branch'], 'date': '2026-03-11',
              'actual_cash': 'seven hundred'},
        headers=owner_x)
    assert response.status_code == 400, response.get_json()


def test_a_negative_cash_count_is_rejected(app, owner_x):
    response = app.test_client().post(
        '/api/daily-closings',
        json={'branch_id': IDS['X']['branch'], 'date': '2026-03-12',
              'actual_cash': -50},
        headers=owner_x)
    assert response.status_code == 400, response.get_json()


def test_a_day_cannot_be_closed_twice(app, owner_x):
    """Two closings for one day double-count that day's revenue everywhere it
    is summed, and leave two contradictory cash differences on record."""
    client = app.test_client()
    payload = {'branch_id': IDS['X']['branch'], 'date': '2026-03-10',
               'actual_cash': 750}

    first = client.post('/api/daily-closings', json=payload, headers=owner_x)
    assert first.status_code == 201, first.get_json()

    second = client.post('/api/daily-closings', json=payload, headers=owner_x)
    assert second.status_code in (400, 409), second.get_json()

    # And the other endpoint that writes closings must agree.
    third = client.post('/api/payments/daily-closing', json=payload, headers=owner_x)
    assert third.status_code in (400, 409), third.get_json()


def test_the_database_itself_refuses_a_duplicate_closing(app):
    """The route checks first and then inserts, which two shifts closing at
    once can both pass. The constraint is what actually holds."""
    from app.extensions import db
    from app.models.daily_closing import DailyClosing

    with app.app_context():
        db.session.add(DailyClosing(
            branch_id=IDS['Y']['branch'], closing_date=date(2026, 3, 20),
            expected_cash=0, actual_cash=0, cash_difference=0,
            network_total=0, transfer_total=0, total_revenue=0,
            closed_by=IDS['Y']['owner'],
        ))
        db.session.commit()

        db.session.add(DailyClosing(
            branch_id=IDS['Y']['branch'], closing_date=date(2026, 3, 20),
            expected_cash=0, actual_cash=0, cash_difference=0,
            network_total=0, transfer_total=0, total_revenue=0,
            closed_by=IDS['Y']['owner'],
        ))
        with pytest.raises(Exception) as caught:
            db.session.commit()
        assert 'unique' in str(caught.value).lower()
        db.session.rollback()


def test_a_closing_cannot_be_written_for_another_gyms_branch(app, owner_x):
    response = app.test_client().post(
        '/api/daily-closings',
        json={'branch_id': IDS['Y']['branch'], 'date': '2026-03-13',
              'actual_cash': 100},
        headers=owner_x)
    assert response.status_code == 403, response.get_json()


def test_every_revenue_figure_for_one_day_agrees(app, owner_x):
    """Gross 1500, discounts 250, so every screen must say 1250.

    The figures come from four different code paths — the payments list, the
    finance daily-sales summary, the daily-closing calculation and the
    accountant dashboard — and each one had its own opinion about whether
    revenue was net of discount. A number that changes depending on which
    screen you open is worse than one that is simply wrong.
    """
    client = app.test_client()
    branch = IDS['X']['branch']

    payments = client.get(
        '/api/payments?date_from=2026-03-10&date_to=2026-03-10',
        headers=owner_x).get_json()['data']['total_amount']

    daily_sales = client.get(
        '/api/finance/daily-sales?date=2026-03-10',
        headers=owner_x).get_json()['data']['total_sales']

    closing = client.post(
        '/api/daily-closings/calculate',
        json={'branch_id': branch, 'date': '2026-03-10'},
        headers=owner_x).get_json()['data']['total_revenue']

    from app.utils.helpers import (
        calculate_branch_revenue, get_daily_transactions_summary,
    )
    with app.app_context():
        helper_total = get_daily_transactions_summary(
            branch, date(2026, 3, 10))['total']
        branch_total = calculate_branch_revenue(
            branch, datetime(2026, 3, 10), datetime(2026, 3, 10, 23, 59, 59))

    figures = {
        'payments list': payments,
        'daily sales': daily_sales,
        'daily closing': closing,
        'daily summary helper': helper_total,
        'branch revenue helper': branch_total,
    }
    for name, value in figures.items():
        assert value == pytest.approx(1250.0), (
            f'{name} says {value}, expected 1250 (1500 gross - 250 discount); '
            f'all figures: {figures}'
        )


def test_the_accountant_dashboard_nets_today_like_it_nets_the_month(app):
    """Today and this month sit next to each other on the same screen, and
    were computed on different bases — today gross, the month net."""
    from app.extensions import db
    from app.models.transaction import (
        Transaction, PaymentMethod, TransactionType,
    )
    from app.services.dashboard_service import DashboardService

    with app.app_context():
        # 400 gross, 150 discounted away, dated today so it lands in both
        # figures at once. Anything summing gross reports 400.
        today_txn = Transaction(
            amount=400, discount=150, payment_method=PaymentMethod.CASH,
            transaction_type=TransactionType.RENEWAL,
            branch_id=IDS['X']['branch'], created_by=IDS['X']['owner'],
            description='Today discounted X',
            transaction_date=datetime.now(), created_at=datetime.now(),
        )
        db.session.add(today_txn)
        db.session.commit()
        try:
            data = DashboardService.get_accountant_dashboard(
                branch_id=IDS['X']['branch'])

            assert data['today']['total'] == pytest.approx(250.0), (
                'today was summed gross while the month beside it was net'
            )
            assert data['today']['cash'] == pytest.approx(250.0)
        finally:
            db.session.delete(today_txn)
            db.session.commit()


# ──────────────────────────────── expenses ──────────────────────────────────

def test_expense_totals_cover_the_whole_filtered_set_not_one_page(app, owner_x):
    """Same trap as the payments total: a figure labelled as the total that
    only added up the rows on screen."""
    from app.extensions import db
    from app.models.expense import Expense, ExpenseCategory, ExpenseStatus

    with app.app_context():
        for i in range(3):
            db.session.add(Expense(
                title=f'Rent {i}', amount=100,
                category=ExpenseCategory.RENT, branch_id=IDS['X']['branch'],
                created_by_id=IDS['X']['owner'], expense_date=date(2026, 3, 10),
                status=ExpenseStatus.PENDING,
            ))
        db.session.commit()

    paged = app.test_client().get(
        '/api/finance/expenses?limit=1', headers=owner_x).get_json()['data']
    assert paged['total_pending'] == pytest.approx(300.0), (
        'the pending total only added up the current page'
    )
