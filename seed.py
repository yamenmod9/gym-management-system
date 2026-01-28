"""
Database seeding script - Creates test data for development and testing
"""
from datetime import datetime, date, timedelta
from app import create_app
from app.extensions import db
from app.models import (
    User, UserRole, Branch, Customer, Gender,
    Service, ServiceType, Subscription, SubscriptionStatus,
    Transaction, PaymentMethod, TransactionType,
    Expense, ExpenseStatus, Complaint, ComplaintType, ComplaintStatus,
    Fingerprint
)


def seed_database():
    """Seed the database with test data"""
    app = create_app('development')
    
    with app.app_context():
        print("🌱 Seeding database...")
        
        # Clear existing data
        print("  ↳ Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create branches
        print("  ↳ Creating branches...")
        branches = create_branches()
        
        # Create users
        print("  ↳ Creating users...")
        users = create_users(branches)
        
        # Create services
        print("  ↳ Creating services...")
        services = create_services()
        
        # Create customers
        print("  ↳ Creating customers...")
        customers = create_customers(branches)
        
        # Create subscriptions
        print("  ↳ Creating subscriptions...")
        subscriptions = create_subscriptions(customers, services, branches, users)
        
        # Create fingerprints
        print("  ↳ Creating fingerprints...")
        create_fingerprints(customers)
        
        # Create transactions
        print("  ↳ Creating transactions...")
        create_transactions(subscriptions, branches, users)
        
        # Create expenses
        print("  ↳ Creating expenses...")
        create_expenses(branches, users)
        
        # Create complaints
        print("  ↳ Creating complaints...")
        create_complaints(branches, customers)
        
        db.session.commit()
        
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print("\n" + "="*60)
        print("📋 TEST ACCOUNTS CREATED - All Roles Available")
        print("="*60)
        print("\n🔐 OWNER ROLE:")
        print("  Username: owner")
        print("  Password: owner123")
        print("  Role: System Owner (Full system access)")
        print("\n👔 BRANCH MANAGER ROLES:")
        print("  Username: manager1")
        print("  Password: manager123")
        print("  Branch: Downtown Branch")
        print("  ")
        print("  Username: manager2")
        print("  Password: manager123")
        print("  Branch: Mall Branch")
        print("\n👥 FRONT DESK / RECEPTION ROLES:")
        print("  Username: reception1")
        print("  Password: reception123")
        print("  Branch: Downtown Branch")
        print("  ")
        print("  Username: reception2")
        print("  Password: reception123")
        print("  Branch: Mall Branch")
        print("  ")
        print("  Username: reception3")
        print("  Password: reception123")
        print("  Branch: North Branch")
        print("\n💰 ACCOUNTANT ROLES:")
        print("  Username: accountant1")
        print("  Password: accountant123")
        print("  Role: Central Accountant")
        print("  ")
        print("  Username: baccountant1")
        print("  Password: accountant123")
        print("  Role: Branch Accountant")
        print("  Branch: Downtown Branch")
        print("="*60)


def create_branches():
    """Create test branches"""
    branches = [
        Branch(
            name='Downtown Branch',
            code='DT001',
            address='123 Main Street, Cairo',
            phone='0212345678',
            city='Cairo',
            is_active=True
        ),
        Branch(
            name='Mall Branch',
            code='ML001',
            address='456 Mall Road, Giza',
            phone='0212345679',
            city='Giza',
            is_active=True
        ),
        Branch(
            name='North Branch',
            code='NT001',
            address='789 North Avenue, Alexandria',
            phone='0212345680',
            city='Alexandria',
            is_active=True
        )
    ]
    
    for branch in branches:
        db.session.add(branch)
    
    db.session.flush()
    return branches


def create_users(branches):
    """Create test users"""
    users = []
    
    # Owner (only one)
    owner = User(
        username='owner',
        email='owner@gym.com',
        full_name='System Owner',
        phone='0201234567',
        role=UserRole.OWNER,
        is_active=True
    )
    owner.set_password('owner123')
    users.append(owner)
    
    # Branch Managers
    for i, branch in enumerate(branches[:2], 1):
        manager = User(
            username=f'manager{i}',
            email=f'manager{i}@gym.com',
            full_name=f'Branch Manager {i}',
            phone=f'020123456{i}',
            role=UserRole.BRANCH_MANAGER,
            branch_id=branch.id,
            is_active=True
        )
        manager.set_password('manager123')
        users.append(manager)
    
    # Receptionists
    for i, branch in enumerate(branches, 1):
        reception = User(
            username=f'reception{i}',
            email=f'reception{i}@gym.com',
            full_name=f'Receptionist {i}',
            phone=f'020223456{i}',
            role=UserRole.FRONT_DESK,
            branch_id=branch.id,
            is_active=True
        )
        reception.set_password('reception123')
        users.append(reception)
    
    # Accountants
    accountant = User(
        username='accountant1',
        email='accountant@gym.com',
        full_name='Central Accountant',
        phone='0203234567',
        role=UserRole.CENTRAL_ACCOUNTANT,
        is_active=True
    )
    accountant.set_password('accountant123')
    users.append(accountant)
    
    branch_accountant = User(
        username='baccountant1',
        email='baccountant1@gym.com',
        full_name='Branch Accountant 1',
        phone='0204234567',
        role=UserRole.BRANCH_ACCOUNTANT,
        branch_id=branches[0].id,
        is_active=True
    )
    branch_accountant.set_password('accountant123')
    users.append(branch_accountant)
    
    for user in users:
        db.session.add(user)
    
    db.session.flush()
    return users


def create_services():
    """Create test services"""
    services = [
        # Gym services
        Service(
            name='Monthly Gym Membership',
            service_type=ServiceType.GYM,
            description='Full gym access for 30 days',
            price=500,
            duration_days=30,
            allowed_days_per_week=7,
            freeze_count_limit=2,
            freeze_max_days=15,
            freeze_is_paid=False,
            is_active=True
        ),
        Service(
            name='Quarterly Gym Membership',
            service_type=ServiceType.GYM,
            description='Full gym access for 90 days',
            price=1350,
            duration_days=90,
            allowed_days_per_week=7,
            freeze_count_limit=3,
            freeze_max_days=30,
            freeze_is_paid=False,
            is_active=True
        ),
        
        # Swimming services
        Service(
            name='Swimming Education - Monthly',
            service_type=ServiceType.SWIMMING_EDUCATION,
            description='Learn to swim - 8 classes per month',
            price=600,
            duration_days=30,
            allowed_days_per_week=2,
            class_limit=8,
            freeze_count_limit=1,
            freeze_max_days=7,
            freeze_is_paid=True,
            freeze_cost=50,
            is_active=True
        ),
        Service(
            name='Swimming Recreation - Monthly',
            service_type=ServiceType.SWIMMING_RECREATION,
            description='Recreational swimming access',
            price=400,
            duration_days=30,
            allowed_days_per_week=7,
            freeze_count_limit=2,
            freeze_max_days=10,
            freeze_is_paid=False,
            is_active=True
        ),
        
        # Karate
        Service(
            name='Karate Classes - Monthly',
            service_type=ServiceType.KARATE,
            description='Karate training - 12 classes per month',
            price=550,
            duration_days=30,
            allowed_days_per_week=3,
            class_limit=12,
            freeze_count_limit=1,
            freeze_max_days=7,
            freeze_is_paid=True,
            freeze_cost=50,
            is_active=True
        ),
        
        # Bundle
        Service(
            name='Gym + Swimming Bundle',
            service_type=ServiceType.BUNDLE,
            description='Full gym and swimming pool access',
            price=800,
            duration_days=30,
            allowed_days_per_week=7,
            freeze_count_limit=2,
            freeze_max_days=15,
            freeze_is_paid=False,
            is_active=True
        )
    ]
    
    for service in services:
        db.session.add(service)
    
    db.session.flush()
    return services


def create_customers(branches):
    """Create test customers"""
    customers = []
    
    names = [
        ('Ahmed Mohamed', 'male', '1990-05-15'),
        ('Sara Ali', 'female', '1992-08-20'),
        ('Mohamed Hassan', 'male', '1988-03-10'),
        ('Fatma Ibrahim', 'female', '1995-11-25'),
        ('Khaled Mahmoud', 'male', '1985-07-30'),
        ('Mona Youssef', 'female', '1993-02-14'),
        ('Omar Samir', 'male', '1991-09-05'),
        ('Noha Ahmed', 'female', '1994-12-18'),
        ('Mahmoud Fathy', 'male', '1987-06-22'),
        ('Heba Khaled', 'female', '1996-04-08')
    ]
    
    for i, (name, gender, dob) in enumerate(names, 1):
        customer = Customer(
            full_name=name,
            phone=f'0101234567{i:02d}',
            email=f'customer{i}@example.com',
            national_id=f'2900112345{i:02d}',
            date_of_birth=datetime.strptime(dob, '%Y-%m-%d').date(),
            gender=Gender(gender),
            address=f'Address {i}, Cairo',
            height=165 + (i % 20),
            weight=65 + (i % 25),
            health_notes='No health issues',
            branch_id=branches[i % len(branches)].id,
            is_active=True
        )
        
        # Calculate health metrics
        customer.calculate_health_metrics()
        
        customers.append(customer)
        db.session.add(customer)
    
    db.session.flush()
    return customers


def create_subscriptions(customers, services, branches, users):
    """Create test subscriptions"""
    subscriptions = []
    reception = [u for u in users if u.role == UserRole.FRONT_DESK][0]
    
    # Create active subscriptions for most customers
    for i, customer in enumerate(customers[:7]):
        service = services[i % len(services)]
        
        subscription = Subscription(
            customer_id=customer.id,
            service_id=service.id,
            branch_id=customer.branch_id,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=20),
            status=SubscriptionStatus.ACTIVE,
            freeze_count=0,
            total_frozen_days=0,
            classes_attended=0
        )
        
        subscriptions.append(subscription)
        db.session.add(subscription)
    
    # Create some expiring soon
    for customer in customers[7:9]:
        subscription = Subscription(
            customer_id=customer.id,
            service_id=services[0].id,
            branch_id=customer.branch_id,
            start_date=date.today() - timedelta(days=25),
            end_date=date.today() + timedelta(days=5),
            status=SubscriptionStatus.ACTIVE,
            freeze_count=0,
            total_frozen_days=0
        )
        
        subscriptions.append(subscription)
        db.session.add(subscription)
    
    # Create one frozen subscription
    subscription = Subscription(
        customer_id=customers[9].id,
        service_id=services[1].id,
        branch_id=customers[9].branch_id,
        start_date=date.today() - timedelta(days=15),
        end_date=date.today() + timedelta(days=30),
        status=SubscriptionStatus.FROZEN,
        freeze_count=1,
        total_frozen_days=7
    )
    subscriptions.append(subscription)
    db.session.add(subscription)
    
    db.session.flush()
    return subscriptions


def create_fingerprints(customers):
    """Create test fingerprints"""
    # Create fingerprints for active customers
    for i, customer in enumerate(customers[:8], 1):
        fingerprint = Fingerprint(
            customer_id=customer.id,
            fingerprint_hash=Fingerprint.generate_fingerprint_hash(
                customer.id,
                f'test_fingerprint_data_{i}'
            ),
            is_active=True
        )
        db.session.add(fingerprint)
    
    db.session.flush()


def create_transactions(subscriptions, branches, users):
    """Create test transactions"""
    reception = [u for u in users if u.role == UserRole.FRONT_DESK][0]
    
    # Create transactions for subscriptions
    for subscription in subscriptions:
        transaction = Transaction(
            amount=subscription.service.price,
            payment_method=PaymentMethod.CASH if subscription.id % 2 == 0 else PaymentMethod.NETWORK,
            transaction_type=TransactionType.SUBSCRIPTION,
            branch_id=subscription.branch_id,
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            created_by=reception.id,
            description=f'New subscription: {subscription.service.name}',
            transaction_date=datetime.utcnow() - timedelta(days=subscription.id)
        )
        db.session.add(transaction)
    
    # Create some misc transactions
    for i, branch in enumerate(branches, 1):
        transaction = Transaction(
            amount=100 + (i * 50),
            payment_method=PaymentMethod.CASH,
            transaction_type=TransactionType.OTHER,
            branch_id=branch.id,
            created_by=reception.id,
            description=f'Miscellaneous payment {i}',
            transaction_date=datetime.utcnow() - timedelta(days=i)
        )
        db.session.add(transaction)
    
    db.session.flush()


def create_expenses(branches, users):
    """Create test expenses"""
    manager = [u for u in users if u.role == UserRole.BRANCH_MANAGER][0]
    accountant = [u for u in users if u.role == UserRole.CENTRAL_ACCOUNTANT][0]
    
    expenses_data = [
        ('Equipment Maintenance', 'Treadmill repair', 500, 'maintenance', ExpenseStatus.APPROVED),
        ('Cleaning Supplies', 'Monthly cleaning supplies', 200, 'supplies', ExpenseStatus.APPROVED),
        ('Electricity Bill', 'Monthly electricity', 1500, 'utilities', ExpenseStatus.PENDING),
        ('Water Bill', 'Monthly water', 300, 'utilities', ExpenseStatus.PENDING),
        ('Equipment Purchase', 'New dumbbells set', 2000, 'equipment', ExpenseStatus.APPROVED),
    ]
    
    for i, (title, desc, amount, category, status) in enumerate(expenses_data):
        expense = Expense(
            title=title,
            description=desc,
            amount=amount,
            category=category,
            branch_id=branches[i % len(branches)].id,
            status=status,
            expense_date=date.today() - timedelta(days=i),
            created_by_id=manager.id
        )
        
        if status == ExpenseStatus.APPROVED:
            expense.reviewed_by_id = accountant.id
            expense.reviewed_at = datetime.utcnow() - timedelta(days=i-1)
            expense.review_notes = 'Approved'
        
        db.session.add(expense)
    
    db.session.flush()


def create_complaints(branches, customers):
    """Create test complaints"""
    complaints_data = [
        ('Broken Treadmill', 'Treadmill #3 is not working', ComplaintType.DEVICE, ComplaintStatus.OPEN),
        ('Pool Temperature', 'Pool water is too cold', ComplaintType.POOL, ComplaintStatus.IN_PROGRESS),
        ('Locker Room Cleanliness', 'Locker room needs cleaning', ComplaintType.CLEANLINESS, ComplaintStatus.CLOSED),
        ('Staff Behavior', 'Receptionist was rude', ComplaintType.SERVICE, ComplaintStatus.OPEN),
        ('AC Not Working', 'Air conditioning in gym area', ComplaintType.DEVICE, ComplaintStatus.IN_PROGRESS),
    ]
    
    for i, (title, desc, comp_type, status) in enumerate(complaints_data):
        complaint = Complaint(
            title=title,
            description=desc,
            complaint_type=comp_type,
            status=status,
            branch_id=branches[i % len(branches)].id,
            customer_id=customers[i].id if i < len(customers) else None,
            customer_name=customers[i].full_name if i < len(customers) else f'Anonymous {i}',
            customer_phone=customers[i].phone if i < len(customers) else None,
            resolution_notes='Resolved' if status == ComplaintStatus.CLOSED else None,
            resolved_at=datetime.utcnow() - timedelta(days=1) if status == ComplaintStatus.CLOSED else None
        )
        db.session.add(complaint)
    
    db.session.flush()


if __name__ == '__main__':
    seed_database()
