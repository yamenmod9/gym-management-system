"""
Database seeding script - Creates test data for development and testing
ENHANCED VERSION - Creates realistic large dataset
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
import random


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
        
        # Create daily closings
        print("  ↳ Creating daily closings...")
        create_daily_closings(branches, users)
        
        db.session.commit()
        
        # Print statistics
        print("\n✅ Database seeded successfully!")
        print("\n" + "="*60)
        print("📊 DATABASE STATISTICS")
        print("="*60)
        print(f"  Branches: {len(branches)}")
        print(f"  Users: {len(users)}")
        print(f"  Services: {len(services)}")
        print(f"  Customers: {len(customers)}")
        print(f"  Subscriptions: {len(subscriptions)}")
        print(f"  Transactions: {Transaction.query.count()}")
        print(f"  Expenses: {Expense.query.count()}")
        print(f"  Complaints: {Complaint.query.count()}")
        print(f"  Fingerprints: {Fingerprint.query.count()}")
        print("="*60)
        
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
    """Create test customers - ENHANCED with 100+ customers"""
    customers = []
    
    # Egyptian first names
    male_names = [
        'Ahmed', 'Mohamed', 'Mahmoud', 'Ali', 'Omar', 'Khaled', 'Youssef', 'Amr',
        'Hassan', 'Karim', 'Tarek', 'Sherif', 'Tamer', 'Hossam', 'Essam', 'Walid',
        'Adel', 'Sami', 'Nader', 'Ramy', 'Hany', 'Fady', 'Magdy', 'Samir',
        'Ibrahim', 'Mostafa', 'Osama', 'Wael', 'Hatem', 'Mazen', 'Basel', 'Ziad'
    ]
    
    female_names = [
        'Sara', 'Fatma', 'Mona', 'Noha', 'Heba', 'Mariam', 'Yasmin', 'Nour',
        'Aya', 'Dina', 'Rania', 'Mai', 'Salma', 'Hana', 'Layla', 'Amira',
        'Rana', 'Somaya', 'Nada', 'Hala', 'Iman', 'Reham', 'Nourhan', 'Hadeer',
        'Doaa', 'Eman', 'Maha', 'Reem', 'Shaimaa', 'Nagwa', 'Amal', 'Zeinab'
    ]
    
    last_names = [
        'Mohamed', 'Ali', 'Hassan', 'Ibrahim', 'Mahmoud', 'Youssef', 'Ahmed',
        'Sayed', 'Abdel Rahman', 'El-Sayed', 'Khalil', 'Mostafa', 'Saad',
        'Farid', 'Rashad', 'Nasser', 'Mansour', 'Saleh', 'Gaber', 'Zaki',
        'Ismail', 'Hamdy', 'Fathy', 'Salem', 'Morsy', 'Kamel', 'Shafik'
    ]
    
    # Create 150 customers for realistic data
    for i in range(1, 151):
        gender = random.choice(['male', 'female'])
        
        if gender == 'male':
            first_name = random.choice(male_names)
        else:
            first_name = random.choice(female_names)
        
        last_name = random.choice(last_names)
        full_name = f'{first_name} {last_name}'
        
        # Generate realistic birth dates (ages 18-55)
        age = random.randint(18, 55)
        birth_year = date.today().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = date(birth_year, birth_month, birth_day)
        
        # Height: 155-195 cm, Weight: 50-120 kg
        height = random.randint(155, 195)
        weight = random.randint(50, 120)
        
        customer = Customer(
            full_name=full_name,
            phone=f'010{random.randint(10000000, 99999999)}',
            email=f'customer{i}@example.com',
            national_id=f'290{random.randint(1000000000, 9999999999)}',
            date_of_birth=dob,
            gender=Gender(gender),
            address=f'{random.randint(1, 200)} Street, {random.choice(["Cairo", "Giza", "Alexandria", "Dokki", "Heliopolis"])}',
            height=height,
            weight=weight,
            health_notes=random.choice([
                'No health issues',
                'Previous knee injury',
                'Back pain - needs special attention',
                'Asthma - no heavy cardio',
                'Diabetes - monitor blood sugar',
                None
            ]),
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
    """Create test subscriptions - ENHANCED with realistic mix"""
    subscriptions = []
    reception_users = [u for u in users if u.role == UserRole.FRONT_DESK]
    
    # Create subscriptions for 80% of customers (120 out of 150)
    active_customers = random.sample(customers, 120)
    
    for customer in active_customers:
        # Get reception user from same branch
        reception = next((u for u in reception_users if u.branch_id == customer.branch_id), reception_users[0])
        
        # Choose random service
        service = random.choice(services)
        
        # Determine subscription age (days since start)
        days_old = random.randint(0, 60)
        
        # Calculate dates
        start_date = date.today() - timedelta(days=days_old)
        end_date = start_date + timedelta(days=service.duration_days)
        
        # Determine status based on dates
        if end_date < date.today():
            # Expired
            status = SubscriptionStatus.EXPIRED
        elif end_date < date.today() + timedelta(days=3):
            # Expiring soon - high priority alert
            status = SubscriptionStatus.ACTIVE
        elif end_date < date.today() + timedelta(days=7):
            # Expiring within week
            status = SubscriptionStatus.ACTIVE
        elif random.random() < 0.05:
            # 5% chance of frozen
            status = SubscriptionStatus.FROZEN
        elif random.random() < 0.03:
            # 3% chance of stopped
            status = SubscriptionStatus.STOPPED
        else:
            # Active
            status = SubscriptionStatus.ACTIVE
        
        subscription = Subscription(
            customer_id=customer.id,
            service_id=service.id,
            branch_id=customer.branch_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            freeze_count=random.randint(0, 2) if status == SubscriptionStatus.FROZEN else 0,
            total_frozen_days=random.randint(0, 7) if status == SubscriptionStatus.FROZEN else 0,
            classes_attended=random.randint(0, 12) if service.class_limit else 0
        )
        
        subscriptions.append(subscription)
        db.session.add(subscription)
    
    db.session.flush()
    return subscriptions


def create_fingerprints(customers):
    """Create test fingerprints - ENHANCED"""
    # Create fingerprints for 90% of customers with active/frozen subscriptions
    eligible_customers = random.sample(customers, int(len(customers) * 0.9))
    
    for customer in eligible_customers:
        fingerprint = Fingerprint(
            customer_id=customer.id,
            fingerprint_hash=Fingerprint.generate_fingerprint_hash(
                customer.id,
                f'fingerprint_data_{customer.id}_{random.randint(1000, 9999)}'
            ),
            is_active=True
        )
        db.session.add(fingerprint)
    
    db.session.flush()


def create_transactions(subscriptions, branches, users):
    """Create test transactions - ENHANCED with realistic payment history"""
    reception_users = [u for u in users if u.role == UserRole.FRONT_DESK]
    
    # Create initial subscription payment transactions
    for subscription in subscriptions:
        reception = next((u for u in reception_users if u.branch_id == subscription.branch_id), reception_users[0])
        
        # Random payment method with realistic distribution
        # 40% cash, 40% network, 20% transfer
        rand = random.random()
        if rand < 0.4:
            payment_method = PaymentMethod.CASH
        elif rand < 0.8:
            payment_method = PaymentMethod.NETWORK
        else:
            payment_method = PaymentMethod.TRANSFER
        
        transaction = Transaction(
            amount=subscription.service.price,
            payment_method=payment_method,
            transaction_type=TransactionType.SUBSCRIPTION,
            branch_id=subscription.branch_id,
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            created_by=reception.id,
            description=f'New subscription: {subscription.service.name}',
            transaction_date=subscription.start_date,
            reference_number=f'TXN{random.randint(100000, 999999)}' if payment_method != PaymentMethod.CASH else None
        )
        db.session.add(transaction)
    
    # Create renewal transactions for some subscriptions
    renewal_count = int(len(subscriptions) * 0.3)  # 30% renewals
    for subscription in random.sample(subscriptions, renewal_count):
        reception = next((u for u in reception_users if u.branch_id == subscription.branch_id), reception_users[0])
        
        rand = random.random()
        if rand < 0.4:
            payment_method = PaymentMethod.CASH
        elif rand < 0.8:
            payment_method = PaymentMethod.NETWORK
        else:
            payment_method = PaymentMethod.TRANSFER
        
        # Create renewal transaction (before current subscription)
        renewal_date = subscription.start_date - timedelta(days=random.randint(30, 90))
        
        transaction = Transaction(
            amount=subscription.service.price,
            payment_method=payment_method,
            transaction_type=TransactionType.RENEWAL,
            branch_id=subscription.branch_id,
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            created_by=reception.id,
            description=f'Renewal: {subscription.service.name}',
            transaction_date=renewal_date,
            reference_number=f'TXN{random.randint(100000, 999999)}' if payment_method != PaymentMethod.CASH else None
        )
        db.session.add(transaction)
    
    # Create freeze payment transactions
    freeze_count = int(len(subscriptions) * 0.1)  # 10% have freeze payments
    for subscription in random.sample(subscriptions, freeze_count):
        if subscription.service.freeze_is_paid:
            reception = next((u for u in reception_users if u.branch_id == subscription.branch_id), reception_users[0])
            
            transaction = Transaction(
                amount=subscription.service.freeze_cost,
                payment_method=random.choice(list(PaymentMethod)),
                transaction_type=TransactionType.FREEZE,
                branch_id=subscription.branch_id,
                customer_id=subscription.customer_id,
                subscription_id=subscription.id,
                created_by=reception.id,
                description=f'Freeze fee: {subscription.service.name}',
                transaction_date=subscription.start_date + timedelta(days=random.randint(5, 20))
            )
            db.session.add(transaction)
    
    # Create misc transactions (personal training, merchandise, etc.)
    for branch in branches:
        reception = next((u for u in reception_users if u.branch_id == branch.id), reception_users[0])
        
        # 15-25 misc transactions per branch
        for _ in range(random.randint(15, 25)):
            misc_types = [
                ('Personal training session', 150),
                ('Protein shake', 35),
                ('Gym merchandise', 80),
                ('Locker rental', 50),
                ('Towel service', 20),
                ('Private class', 200),
                ('Nutritionist consultation', 300)
            ]
            
            desc, base_amount = random.choice(misc_types)
            amount = base_amount + random.randint(-10, 20)
            
            # Random date within last 60 days
            trans_date = date.today() - timedelta(days=random.randint(0, 60))
            
            transaction = Transaction(
                amount=amount,
                payment_method=random.choice(list(PaymentMethod)),
                transaction_type=TransactionType.OTHER,
                branch_id=branch.id,
                customer_id=random.choice(subscriptions).customer_id if random.random() > 0.2 else None,
                created_by=reception.id,
                description=desc,
                transaction_date=trans_date,
                reference_number=f'TXN{random.randint(100000, 999999)}' if random.random() > 0.5 else None
            )
            db.session.add(transaction)
    
    db.session.flush()


def create_expenses(branches, users):
    """Create test expenses - ENHANCED with realistic expense data"""
    managers = [u for u in users if u.role == UserRole.BRANCH_MANAGER]
    accountant = [u for u in users if u.role == UserRole.CENTRAL_ACCOUNTANT][0]
    
    expense_templates = [
        ('Equipment Maintenance', 'Treadmill repair and maintenance', 500, 800, 'maintenance'),
        ('Cleaning Supplies', 'Monthly cleaning and sanitation supplies', 150, 300, 'supplies'),
        ('Electricity Bill', 'Monthly electricity consumption', 1200, 2000, 'utilities'),
        ('Water Bill', 'Monthly water usage', 250, 500, 'utilities'),
        ('Equipment Purchase', 'New gym equipment', 1500, 5000, 'equipment'),
        ('Pool Chemicals', 'Chlorine and pool maintenance chemicals', 300, 600, 'supplies'),
        ('Staff Training', 'Professional development and certifications', 800, 1500, 'training'),
        ('Marketing Materials', 'Flyers, banners, and promotional items', 200, 800, 'marketing'),
        ('Internet & Phone', 'Monthly communication bills', 400, 700, 'utilities'),
        ('Security Service', 'Monthly security guard service', 2000, 3000, 'services'),
        ('Insurance Payment', 'Monthly insurance premium', 1500, 2500, 'insurance'),
        ('Repair Work', 'General facility repairs', 300, 1200, 'maintenance'),
        ('AC Maintenance', 'Air conditioning service and repair', 800, 1500, 'maintenance'),
        ('Locker Replacement', 'New lockers for changing room', 2000, 4000, 'equipment'),
        ('Music System', 'Sound system upgrade', 1000, 2000, 'equipment'),
        ('Painting Work', 'Interior painting and decoration', 1500, 3000, 'maintenance'),
        ('Uniform Purchase', 'Staff uniforms', 500, 1000, 'supplies'),
        ('First Aid Supplies', 'Medical supplies and first aid kit', 200, 400, 'supplies'),
        ('Software License', 'Management software annual fee', 1000, 2000, 'software'),
        ('Pest Control', 'Monthly pest control service', 300, 500, 'services')
    ]
    
    # Create 50-70 expenses across all branches over last 90 days
    for _ in range(random.randint(50, 70)):
        branch = random.choice(branches)
        manager = next((u for u in managers if u.branch_id == branch.id), managers[0])
        
        template = random.choice(expense_templates)
        title, base_desc, min_amount, max_amount, category = template
        
        amount = random.randint(min_amount, max_amount)
        expense_date = date.today() - timedelta(days=random.randint(0, 90))
        
        # Determine status based on date
        # Recent expenses more likely to be pending
        days_old = (date.today() - expense_date).days
        
        if days_old < 7:
            # Recent expenses - 60% pending
            status = ExpenseStatus.PENDING if random.random() < 0.6 else ExpenseStatus.APPROVED
        elif days_old < 15:
            # Medium age - 30% pending
            status = ExpenseStatus.PENDING if random.random() < 0.3 else ExpenseStatus.APPROVED
        else:
            # Old expenses - mostly approved, some rejected
            rand = random.random()
            if rand < 0.85:
                status = ExpenseStatus.APPROVED
            elif rand < 0.95:
                status = ExpenseStatus.REJECTED
            else:
                status = ExpenseStatus.PENDING
        
        expense = Expense(
            title=title,
            description=f'{base_desc} - {branch.name}',
            amount=amount,
            category=category,
            branch_id=branch.id,
            status=status,
            expense_date=expense_date,
            created_by_id=manager.id
        )
        
        if status in [ExpenseStatus.APPROVED, ExpenseStatus.REJECTED]:
            expense.reviewed_by_id = accountant.id
            expense.reviewed_at = expense_date + timedelta(days=random.randint(1, 5))
            
            if status == ExpenseStatus.APPROVED:
                expense.review_notes = random.choice([
                    'Approved',
                    'Approved - necessary expense',
                    'Approved - within budget',
                    'Approved as per policy'
                ])
            else:
                expense.review_notes = random.choice([
                    'Not in budget this month',
                    'Needs more documentation',
                    'Exceeds approval limit',
                    'Duplicate expense'
                ])
        
        db.session.add(expense)
    
    db.session.flush()


def create_complaints(branches, customers):
    """Create test complaints - ENHANCED with realistic complaint data"""
    complaint_templates = [
        ('Broken Treadmill', 'Treadmill #{} is not working properly', ComplaintType.DEVICE),
        ('Pool Temperature Issue', 'Pool water temperature is {}', ComplaintType.POOL),
        ('Locker Room Cleanliness', 'Locker room needs better cleaning', ComplaintType.CLEANLINESS),
        ('Staff Behavior', 'Staff member was {} during my visit', ComplaintType.SERVICE),
        ('AC Not Working', 'Air conditioning not functioning in {} area', ComplaintType.DEVICE),
        ('Equipment Missing', 'Some gym equipment is missing or unavailable', ComplaintType.DEVICE),
        ('Pool Cleanliness', 'Pool water appears dirty and needs cleaning', ComplaintType.POOL),
        ('Bathroom Condition', 'Bathroom facilities need maintenance', ComplaintType.CLEANLINESS),
        ('Rude Reception', 'Reception staff was unprofessional', ComplaintType.SERVICE),
        ('Shower Issues', 'Shower water pressure is very low', ComplaintType.DEVICE),
        ('Wet Floor', 'Floor is wet and slippery - safety hazard', ComplaintType.CLEANLINESS),
        ('Music Too Loud', 'Music volume is disturbing', ComplaintType.OTHER),
        ('Class Overcrowded', 'Too many people in swimming class', ComplaintType.POOL),
        ('Trainer Absent', 'Scheduled trainer did not show up', ComplaintType.SERVICE),
        ('Parking Problem', 'Not enough parking spaces available', ComplaintType.OTHER),
        ('WiFi Not Working', 'Internet connection is not working', ComplaintType.DEVICE),
        ('Smell in Gym', 'Unpleasant smell in the gym area', ComplaintType.CLEANLINESS),
        ('Wrong Charge', 'I was charged incorrect amount', ComplaintType.SERVICE),
        ('Towel Service', 'No clean towels available', ComplaintType.CLEANLINESS),
        ('Lock Broken', 'My locker lock is broken', ComplaintType.DEVICE)
    ]
    
    descriptive_words = {
        'temperature': ['too cold', 'too hot', 'not comfortable'],
        'area': ['main gym', 'cardio section', 'weight area', 'group class room'],
        'staff': ['rude', 'unhelpful', 'not attentive', 'unprofessional'],
        'number': ['1', '2', '3', '5', '7', '12']
    }
    
    # Create 30-50 complaints
    for _ in range(random.randint(30, 50)):
        template = random.choice(complaint_templates)
        title, desc_template, comp_type = template
        
        # Fill in template with random details
        if '{}' in desc_template:
            if 'temperature' in desc_template.lower():
                detail = random.choice(descriptive_words['temperature'])
            elif 'area' in desc_template.lower():
                detail = random.choice(descriptive_words['area'])
            elif 'was {}' in desc_template:
                detail = random.choice(descriptive_words['staff'])
            elif '#{}'  in desc_template:
                detail = random.choice(descriptive_words['number'])
            else:
                detail = 'not satisfactory'
            
            description = desc_template.format(detail)
        else:
            description = desc_template
        
        # Random date within last 60 days
        complaint_date = datetime.utcnow() - timedelta(days=random.randint(0, 60))
        days_old = (datetime.utcnow() - complaint_date).days
        
        # Determine status based on age
        if days_old < 3:
            # Recent complaints - mostly open
            status = ComplaintStatus.OPEN if random.random() < 0.8 else ComplaintStatus.IN_PROGRESS
        elif days_old < 10:
            # Medium age - mix
            rand = random.random()
            if rand < 0.3:
                status = ComplaintStatus.OPEN
            elif rand < 0.7:
                status = ComplaintStatus.IN_PROGRESS
            else:
                status = ComplaintStatus.CLOSED
        else:
            # Old complaints - mostly closed
            rand = random.random()
            if rand < 0.8:
                status = ComplaintStatus.CLOSED
            elif rand < 0.95:
                status = ComplaintStatus.IN_PROGRESS
            else:
                status = ComplaintStatus.OPEN
        
        # 70% have customer info, 30% anonymous
        customer = random.choice(customers) if random.random() < 0.7 else None
        branch = random.choice(branches)
        
        complaint = Complaint(
            title=title,
            description=description,
            complaint_type=comp_type,
            status=status,
            branch_id=branch.id,
            customer_id=customer.id if customer else None,
            customer_name=customer.full_name if customer else f'Anonymous Customer',
            customer_phone=customer.phone if customer else None,
            created_at=complaint_date,
            resolution_notes=random.choice([
                'Issue resolved',
                'Equipment repaired',
                'Staff member trained',
                'Cleaning schedule updated',
                'Policy explained to customer',
                'Compensation provided'
            ]) if status == ComplaintStatus.CLOSED else None,
            resolved_at=complaint_date + timedelta(days=random.randint(1, 7)) if status == ComplaintStatus.CLOSED else None
        )
        db.session.add(complaint)
    
    db.session.flush()


def create_daily_closings(branches, users):
    """Create daily closing records for the last 30 days"""
    from app.models.daily_closing import DailyClosing
    from app.models.transaction import Transaction
    from sqlalchemy import func, and_
    
    reception_users = [u for u in users if u.role == UserRole.FRONT_DESK]
    
    # Create closings for last 30 days for each branch
    for branch in branches:
        reception = next((u for u in reception_users if u.branch_id == branch.id), reception_users[0])
        
        for days_ago in range(30, 0, -1):
            closing_date = date.today() - timedelta(days=days_ago)
            
            # Calculate actual totals from transactions for that day
            day_transactions = Transaction.query.filter(
                and_(
                    Transaction.branch_id == branch.id,
                    func.date(Transaction.transaction_date) == closing_date
                )
            ).all()
            
            expected_cash = 0
            network_total = 0
            transfer_total = 0
            
            for txn in day_transactions:
                amount = float(txn.amount)
                if txn.payment_method == PaymentMethod.CASH:
                    expected_cash += amount
                elif txn.payment_method == PaymentMethod.NETWORK:
                    network_total += amount
                elif txn.payment_method == PaymentMethod.TRANSFER:
                    transfer_total += amount
            
            # Skip days with no transactions
            if expected_cash == 0 and network_total == 0 and transfer_total == 0:
                continue
            
            # Actual cash has small random variance (±0-50 EGP)
            variance = random.randint(-50, 50)
            actual_cash = expected_cash + variance
            
            closing = DailyClosing(
                branch_id=branch.id,
                closing_date=closing_date,
                expected_cash=expected_cash,
                actual_cash=actual_cash,
                cash_difference=variance,
                network_total=network_total,
                transfer_total=transfer_total,
                total_revenue=expected_cash + network_total + transfer_total,
                closed_by=reception.id,
                notes=random.choice([
                    'Normal closing',
                    'All cash accounted',
                    'Busy day',
                    'Slow day',
                    None
                ]) if abs(variance) < 20 else f'Cash difference: {variance} EGP',
                created_at=datetime.combine(closing_date, datetime.min.time()) + timedelta(hours=22)
            )
            db.session.add(closing)
    
    db.session.flush()


if __name__ == '__main__':
    seed_database()
