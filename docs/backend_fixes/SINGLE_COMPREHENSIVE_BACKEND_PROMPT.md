# 🚀 SINGLE COMPREHENSIVE PROMPT FOR CLAUDE SONNET 4.5

**Copy and paste this ENTIRE prompt to Claude Sonnet 4.5 for backend implementation**

---

## 🎯 OBJECTIVE

Implement a complete backend API for a Gym Management System with:
- Staff app (Owner, Manager, Accountant, Reception)
- Client app (Customer mobile app)
- Comprehensive seed data for testing

The Flutter frontend is **100% complete**. We need the backend to match its expectations.

---

## 🔐 AUTHENTICATION SYSTEM

### Two Separate Auth Systems:

#### 1. STAFF AUTHENTICATION
- Users: Owner, Managers, Receptionists, Accountants
- Login: Username + Password
- Token: JWT with `type: 'staff'`, expires in 1 day
- Endpoint: `POST /api/auth/login`

#### 2. CLIENT AUTHENTICATION  
- Users: Gym customers/members
- Login: Phone Number + Password (temporary or permanent)
- Token: JWT with `type: 'client'`, expires in 7 days
- Endpoint: `POST /api/client/auth/login`
- **Special:** First-time users have temporary password that MUST be changed

---

## ⚠️ CRITICAL: TEMPORARY PASSWORD SYSTEM

### The Problem We're Solving:

When reception staff register a new customer, they need to:
1. Get a temporary password from the system
2. Give it to the customer for first login
3. Customer logs in and is FORCED to change password
4. Staff can see temporary passwords in customer list (ONLY for first-time users)

### Implementation Requirements:

#### Database Schema:
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR(255),
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(255),
    qr_code VARCHAR(50) UNIQUE,
    branch_id INTEGER,
    gender VARCHAR(10),
    date_of_birth DATE,
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- PASSWORD FIELDS (CRITICAL!)
    temporary_password VARCHAR(255),  -- Hashed password for authentication
    plain_temporary_password VARCHAR(10),  -- Plain text for staff viewing ONLY
    password_changed BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Password Generation Logic:
```python
import string
import random
from werkzeug.security import generate_password_hash, check_password_hash

def generate_temp_password(length=6):
    """Generate 6-character temporary password: uppercase letters + digits only"""
    chars = string.ascii_uppercase + string.digits  # A-Z, 0-9
    return ''.join(random.choice(chars) for _ in range(length))
    # Examples: "RX04AF", "AB12CD", "SI19IC", "PS02HC"

# When registering new customer:
plain_password = generate_temp_password()  # e.g., "RX04AF"

customer = Customer(
    full_name="Mohamed Salem",
    phone="01077827638",
    email="customer1@example.com",
    temporary_password=generate_password_hash(plain_password),  # Hashed for auth
    plain_temporary_password=plain_password,  # Plain for staff viewing
    password_changed=False
)
```

#### Customer Model - to_dict_for_staff():
```python
class Customer(db.Model):
    # ... fields defined above ...
    
    def to_dict_for_staff(self):
        """Return customer data for STAFF viewing (includes plain password if not changed)"""
        data = {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'qr_code': self.qr_code,
            'branch_id': self.branch_id,
            'is_active': self.is_active,
            'password_changed': self.password_changed,
            'height': self.height,
            'weight': self.weight,
            'gender': self.gender,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        # CRITICAL: Return plain password ONLY if customer hasn't changed it yet
        if not self.password_changed and self.plain_temporary_password:
            data['temporary_password'] = self.plain_temporary_password  # e.g., "RX04AF"
        
        return data
    
    def to_dict_for_client(self):
        """Return customer data for CLIENT viewing (NEVER includes password)"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'qr_code': self.qr_code,
            'branch_id': self.branch_id,
            'is_active': self.is_active,
            'password_changed': self.password_changed,
            # ... other fields but NEVER password fields
        }
```

#### Customer Registration Endpoint:
```python
@customers_bp.route('/register', methods=['POST'])
@jwt_required()
def register_customer():
    """Register new customer (STAFF ONLY)"""
    data = request.get_json()
    
    # Generate temporary password
    plain_password = generate_temp_password()  # e.g., "AB12CD"
    
    # Create customer
    customer = Customer(
        full_name=data['full_name'],
        phone=data['phone'],
        email=data.get('email'),
        branch_id=data['branch_id'],
        qr_code=f"CUST-{get_next_id():03d}-{get_branch_code(data['branch_id'])}",
        gender=data.get('gender'),
        date_of_birth=data.get('date_of_birth'),
        height=data.get('height'),
        weight=data.get('weight'),
        temporary_password=generate_password_hash(plain_password),  # Hashed
        plain_temporary_password=plain_password,  # Plain
        password_changed=False,
        is_active=True
    )
    
    db.session.add(customer)
    db.session.commit()
    
    # IMPORTANT: Return plain password to staff so they can give it to customer
    return jsonify({
        'status': 'success',
        'message': 'Customer registered successfully',
        'data': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,
            'temporary_password': plain_password,  # ← Staff sees this
            'password_changed': False,
            'note': 'Give these credentials to the customer for their mobile app login'
        }
    }), 201
```

#### Get Customers Endpoint (Staff View):
```python
@customers_bp.route('/', methods=['GET'])
@jwt_required()
def get_customers():
    """Get all customers (STAFF ONLY)"""
    branch_id = request.args.get('branch_id', type=int)
    
    query = Customer.query
    if branch_id:
        query = query.filter_by(branch_id=branch_id)
    
    customers = query.all()
    
    # IMPORTANT: Use to_dict_for_staff() to include plain passwords
    result = [customer.to_dict_for_staff() for customer in customers]
    
    return jsonify({
        'status': 'success',
        'data': {
            'items': result,
            'total': len(result)
        }
    }), 200
```

#### Client Login Endpoint:
```python
@clients_bp.route('/auth/login', methods=['POST'])
def client_login():
    """Client authentication"""
    data = request.get_json()
    identifier = data.get('phone') or data.get('email')
    password = data.get('password')
    
    # Find customer by phone or email
    customer = Customer.query.filter(
        (Customer.phone == identifier) | (Customer.email == identifier)
    ).first()
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone/email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401
    
    if not customer.is_active:
        return jsonify({
            'status': 'error',
            'message': 'Your account is not active. Please contact reception.',
            'code': 'ACCOUNT_INACTIVE'
        }), 403
    
    # Verify password (uses hashed temporary_password)
    if not customer.temporary_password or not check_password_hash(customer.temporary_password, password):
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone/email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401
    
    # Generate JWT token
    token = create_access_token(
        identity=customer.id,
        additional_claims={'type': 'client'},
        expires_delta=timedelta(days=7)
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'token': token,
            'customer': customer.to_dict_for_client(),
            'password_changed': customer.password_changed  # ← Frontend checks this
        }
    }), 200
```

#### Change Password Endpoint:
```python
@clients_bp.route('/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change customer password (CLIENT ONLY)"""
    customer_id = get_jwt_identity()
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    customer = Customer.query.get(customer_id)
    
    # Verify current password
    if not check_password_hash(customer.temporary_password, old_password):
        return jsonify({
            'status': 'error',
            'message': 'Current password is incorrect',
            'code': 'INVALID_PASSWORD'
        }), 401
    
    if len(new_password) < 6:
        return jsonify({
            'status': 'error',
            'message': 'New password must be at least 6 characters',
            'code': 'PASSWORD_TOO_SHORT'
        }), 400
    
    if old_password == new_password:
        return jsonify({
            'status': 'error',
            'message': 'New password must be different from current password',
            'code': 'SAME_PASSWORD'
        }), 400
    
    # Update password
    customer.temporary_password = generate_password_hash(new_password)
    customer.plain_temporary_password = None  # ✅ CLEAR PLAIN PASSWORD
    customer.password_changed = True  # ✅ MARK AS CHANGED
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Password changed successfully',
        'data': {
            'password_changed': True
        }
    }), 200
```

---

## 📱 COMPLETE API ENDPOINTS LIST

### STAFF APP ENDPOINTS (~45 endpoints)

#### Authentication (3)
- `POST /api/auth/login` - Staff login
- `GET /api/auth/profile` - Get staff profile
- `POST /api/auth/logout` - Staff logout

#### Customers (6)
- `GET /api/customers` - List customers (with `temporary_password` if not changed)
- `GET /api/customers/{id}` - Get single customer
- `POST /api/customers/register` - Register new customer (returns plain password)
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer
- `GET /api/customers/{id}/qr-code` - Get customer QR code

#### Subscriptions (5)
- `GET /api/subscriptions` - List subscriptions
- `GET /api/subscriptions/{id}` - Get single subscription
- `POST /api/subscriptions` - Create subscription
- `PATCH /api/subscriptions/{id}/status` - Update status
- `POST /api/subscriptions/{id}/deduct` - Deduct session/coin (QR scan check-in)

#### Attendance (2)
- `POST /api/attendance` - Record attendance/check-in
- `GET /api/attendance` - Get attendance history

#### Payments (2)
- `POST /api/payments` - Record payment
- `GET /api/payments` - List payments

#### Expenses (3)
- `GET /api/expenses` - List expenses
- `POST /api/expenses` - Create expense
- `PATCH /api/expenses/{id}/status` - Approve/reject expense

#### Complaints (2)
- `GET /api/complaints` - List complaints
- `PATCH /api/complaints/{id}/status` - Update complaint status

#### Branches (3)
- `GET /api/branches` - List all branches
- `GET /api/branches/{id}` - Get branch details
- `GET /api/branches/{id}/stats` - Get branch statistics

#### Users/Staff (3)
- `GET /api/users` - List staff members
- `GET /api/users/{id}` - Get staff member details
- `POST /api/users` - Create staff member

#### Reports (5)
- `GET /api/reports/revenue` - Revenue report
- `GET /api/reports/customers` - Customer analytics
- `GET /api/reports/subscriptions` - Subscription analytics
- `GET /api/reports/attendance` - Attendance report
- `GET /api/reports/expenses` - Expense report

#### Dashboard (2)
- `GET /api/smart-alerts` - Get alerts for owner/manager
- `GET /api/dashboard/stats` - Get dashboard statistics

### CLIENT APP ENDPOINTS (~15 endpoints)

#### Authentication (3)
- `POST /api/client/auth/login` - Client login (phone + temp password)
- `POST /api/client/auth/change-password` - Change password (forced on first login)
- `POST /api/client/auth/logout` - Client logout

#### Profile (3)
- `GET /api/client/profile` - Get my profile
- `PUT /api/client/profile` - Update my profile
- `GET /api/client/qr-code` - Get my QR code

#### Subscription (2)
- `GET /api/client/subscription` - Get my active subscription
- `GET /api/client/subscriptions/history` - Get subscription history

#### Attendance (1)
- `GET /api/client/attendance` - Get my attendance history

#### Complaints (2)
- `POST /api/client/complaints` - Submit complaint
- `GET /api/client/complaints` - Get my complaints

#### Health Metrics (1)
- `GET /api/client/health-metrics` - Get BMI, BMR, calories

---

## 🌱 COMPREHENSIVE SEED DATA SCRIPT

### Requirements Summary:
- **14 staff users** (1 owner, 3 managers, 6 receptionists, 4 accountants)
- **3 branches** (Dragon Club, Phoenix Fitness, Tiger Gym)
- **150 customers** with temporary passwords (75 first-time, 75 changed)
- **87 active subscriptions** (45 branch 1, 27 branch 2, 15 branch 3)
- **150+ payments**
- **45 expenses** (10 pending, 25 approved, 10 rejected)
- **500+ attendance records**
- **20 complaints**

### Seed Script Implementation:

```python
# seed.py
import random
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Branch, Customer, Subscription, Payment, Expense, Attendance, Complaint

def generate_temp_password(length=6):
    """Generate 6-character temporary password"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def seed_all():
    """Run all seed functions"""
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        print("\n" + "="*80)
        print(" GYM MANAGEMENT SYSTEM - DATABASE SEEDING")
        print("="*80)
        
        seed_branches()
        seed_staff()
        seed_customers()
        seed_subscriptions()
        seed_payments()
        seed_expenses()
        seed_attendance()
        seed_complaints()
        
        print("\n" + "="*80)
        print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*80)

def seed_branches():
    """Create 3 branches"""
    print("\n🏢 CREATING BRANCHES")
    print("-" * 80)
    
    branches = [
        {
            'name': 'Dragon Club',
            'location': 'Downtown Cairo',
            'address': '123 Main Street, Cairo, Egypt',
            'phone': '021234567890',
            'email': 'dragon@gym.com',
            'capacity': 150,
            'status': 'active'
        },
        {
            'name': 'Phoenix Fitness',
            'location': 'Nasr City',
            'address': '456 Nasr Street, Cairo, Egypt',
            'phone': '021234567891',
            'email': 'phoenix@gym.com',
            'capacity': 120,
            'status': 'active'
        },
        {
            'name': 'Tiger Gym',
            'location': 'Heliopolis',
            'address': '789 Heliopolis Ave, Cairo, Egypt',
            'phone': '021234567892',
            'email': 'tiger@gym.com',
            'capacity': 100,
            'status': 'active'
        }
    ]
    
    for branch_data in branches:
        branch = Branch(**branch_data)
        db.session.add(branch)
        print(f"  ✓ {branch_data['name']} - {branch_data['location']}")
    
    db.session.commit()
    print(f"\n✅ Created {len(branches)} branches")

def seed_staff():
    """Create 14 staff members"""
    print("\n👥 CREATING STAFF MEMBERS")
    print("-" * 80)
    
    staff = [
        # 1 Owner
        {
            'username': 'owner',
            'password': 'owner123',
            'role': 'owner',
            'full_name': 'System Owner',
            'email': 'owner@gym.com',
            'phone': '01000000000',
            'branch_id': None
        },
        # 3 Branch Managers
        {
            'username': 'manager_dragon',
            'password': 'manager123',
            'role': 'manager',
            'full_name': 'Ahmed Manager',
            'email': 'manager.dragon@gym.com',
            'phone': '01234567890',
            'branch_id': 1
        },
        {
            'username': 'manager_phoenix',
            'password': 'manager123',
            'role': 'manager',
            'full_name': 'Sara Manager',
            'email': 'manager.phoenix@gym.com',
            'phone': '01234567891',
            'branch_id': 2
        },
        {
            'username': 'manager_tiger',
            'password': 'manager123',
            'role': 'manager',
            'full_name': 'Mohamed Manager',
            'email': 'manager.tiger@gym.com',
            'phone': '01234567892',
            'branch_id': 3
        },
        # 6 Receptionists (2 per branch)
        {
            'username': 'reception_dragon_1',
            'password': 'reception123',
            'role': 'reception',
            'full_name': 'Fatma Reception',
            'email': 'reception1.dragon@gym.com',
            'phone': '01234567893',
            'branch_id': 1
        },
        {
            'username': 'reception_dragon_2',
            'password': 'reception123',
            'role': 'reception',
            'full_name': 'Yasmin Reception',
            'email': 'reception2.dragon@gym.com',
            'phone': '01234567894',
            'branch_id': 1
        },
        {
            'username': 'reception_phoenix_1',
            'password': 'reception123',
            'role': 'reception',
            'full_name': 'Amira Reception',
            'email': 'reception1.phoenix@gym.com',
            'phone': '01234567895',
            'branch_id': 2
        },
        {
            'username': 'reception_phoenix_2',
            'password': 'reception123',
            'role': 'reception',
            'full_name': 'Huda Reception',
            'email': 'reception2.phoenix@gym.com',
            'phone': '01234567896',
            'branch_id': 2
        },
        {
            'username': 'reception_tiger_1',
            'password': 'reception123',
            'role': 'reception',
            'full_name': 'Nour Reception',
            'email': 'reception1.tiger@gym.com',
            'phone': '01234567897',
            'branch_id': 3
        },
        {
            'username': 'reception_tiger_2',
            'password': 'reception123',
            'role': 'reception',
            'full_name': 'Laila Reception',
            'email': 'reception2.tiger@gym.com',
            'phone': '01234567898',
            'branch_id': 3
        },
        # 4 Accountants (1 central + 3 branch)
        {
            'username': 'accountant_central',
            'password': 'accountant123',
            'role': 'accountant',
            'full_name': 'Heba Accountant',
            'email': 'accountant.central@gym.com',
            'phone': '01234567899',
            'branch_id': None
        },
        {
            'username': 'accountant_dragon',
            'password': 'accountant123',
            'role': 'accountant',
            'full_name': 'Omar Accountant',
            'email': 'accountant.dragon@gym.com',
            'phone': '01234567900',
            'branch_id': 1
        },
        {
            'username': 'accountant_phoenix',
            'password': 'accountant123',
            'role': 'accountant',
            'full_name': 'Mona Accountant',
            'email': 'accountant.phoenix@gym.com',
            'phone': '01234567901',
            'branch_id': 2
        },
        {
            'username': 'accountant_tiger',
            'password': 'accountant123',
            'role': 'accountant',
            'full_name': 'Karim Accountant',
            'email': 'accountant.tiger@gym.com',
            'phone': '01234567902',
            'branch_id': 3
        }
    ]
    
    for staff_data in staff:
        password = staff_data.pop('password')
        user = User(**staff_data)
        user.password = generate_password_hash(password)
        db.session.add(user)
        branch_text = f"Branch {staff_data['branch_id']}" if staff_data['branch_id'] else "Central"
        print(f"  ✓ {staff_data['username']} ({staff_data['role']}) - {branch_text}")
    
    db.session.commit()
    print(f"\n✅ Created {len(staff)} staff members")

def seed_customers():
    """Create 150 customers with temporary passwords"""
    print("\n" + "="*80)
    print("👤 CREATING 150 CUSTOMERS WITH TEMPORARY PASSWORDS")
    print("="*80)
    print("\n📋 FIRST-TIME LOGIN CREDENTIALS (password_changed=False):")
    print("-" * 80)
    
    customer_id = 1
    first_names = ["Mohamed", "Ahmed", "Fatma", "Sara", "Ali", "Yasmin", "Omar", "Layla", 
                   "Hassan", "Nour", "Karim", "Huda", "Ibrahim", "Amira", "Khaled"]
    last_names = ["Salem", "Hassan", "Rashad", "Youssef", "Mahmoud", "Khalil", "Farid", 
                  "Nasser", "Kamel", "Zaki", "Badawi", "Gaber", "Fouad"]
    
    # Branch 1: Dragon Club (60 customers)
    for i in range(60):
        plain_password = generate_temp_password()
        password_changed = i >= 30  # First 30: not changed, last 30: changed
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        customer = Customer(
            full_name=f"{first_name} {last_name}",
            phone=f"010{77827638 + customer_id}",
            email=f"customer{customer_id}@example.com",
            qr_code=f"CUST-{customer_id:03d}-DRAGON",
            branch_id=1,
            gender=random.choice(["male", "female"]),
            date_of_birth=f"{random.randint(1985, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            height=round(random.uniform(160, 190), 2),
            weight=round(random.uniform(60, 100), 1),
            temporary_password=generate_password_hash(plain_password),
            plain_temporary_password=plain_password if not password_changed else None,
            password_changed=password_changed,
            is_active=True
        )
        
        db.session.add(customer)
        
        if not password_changed:
            print(f"  Phone: {customer.phone} | Password: {plain_password} | QR: {customer.qr_code}")
        
        customer_id += 1
    
    # Branch 2: Phoenix Fitness (55 customers)
    for i in range(55):
        plain_password = generate_temp_password()
        password_changed = i >= 27
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        customer = Customer(
            full_name=f"{first_name} {last_name}",
            phone=f"010{77827638 + customer_id}",
            email=f"customer{customer_id}@example.com",
            qr_code=f"CUST-{customer_id:03d}-PHOENIX",
            branch_id=2,
            gender=random.choice(["male", "female"]),
            date_of_birth=f"{random.randint(1985, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            height=round(random.uniform(160, 190), 2),
            weight=round(random.uniform(60, 100), 1),
            temporary_password=generate_password_hash(plain_password),
            plain_temporary_password=plain_password if not password_changed else None,
            password_changed=password_changed,
            is_active=True
        )
        
        db.session.add(customer)
        
        if not password_changed:
            print(f"  Phone: {customer.phone} | Password: {plain_password} | QR: {customer.qr_code}")
        
        customer_id += 1
    
    # Branch 3: Tiger Gym (35 customers)
    for i in range(35):
        plain_password = generate_temp_password()
        password_changed = i >= 18
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        customer = Customer(
            full_name=f"{first_name} {last_name}",
            phone=f"010{77827638 + customer_id}",
            email=f"customer{customer_id}@example.com",
            qr_code=f"CUST-{customer_id:03d}-TIGER",
            branch_id=3,
            gender=random.choice(["male", "female"]),
            date_of_birth=f"{random.randint(1985, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            height=round(random.uniform(160, 190), 2),
            weight=round(random.uniform(60, 100), 1),
            temporary_password=generate_password_hash(plain_password),
            plain_temporary_password=plain_password if not password_changed else None,
            password_changed=password_changed,
            is_active=True
        )
        
        db.session.add(customer)
        
        if not password_changed:
            print(f"  Phone: {customer.phone} | Password: {plain_password} | QR: {customer.qr_code}")
        
        customer_id += 1
    
    db.session.commit()
    print("-" * 80)
    print(f"\n✅ Created 150 customers")
    print(f"   - Dragon Club: 60 (30 first-time, 30 password changed)")
    print(f"   - Phoenix Fitness: 55 (27 first-time, 28 password changed)")
    print(f"   - Tiger Gym: 35 (18 first-time, 17 password changed)")
    print(f"   - Total first-time users: 75 (can see plain passwords)")
    print("="*80 + "\n")

def seed_subscriptions():
    """Create 87 active subscriptions + 63 expired"""
    print("\n💳 CREATING SUBSCRIPTIONS")
    print("-" * 80)
    
    customers = Customer.query.all()
    today = datetime.now()
    
    sub_id = 1
    active_count = 0
    expired_count = 0
    
    # Distribution: Branch 1: 45 active, Branch 2: 27 active, Branch 3: 15 active
    for customer in customers:
        if customer.branch_id == 1 and active_count < 45:
            create_active = True
        elif customer.branch_id == 2 and active_count < 72:  # 45+27
            create_active = True
        elif customer.branch_id == 3 and active_count < 87:  # 45+27+15
            create_active = True
        else:
            create_active = False
        
        if create_active:
            sub_type = random.choice(['monthly', 'monthly', 'coins', 'sessions'])
            
            if sub_type == 'monthly':
                start_date = today - timedelta(days=random.randint(5, 25))
                end_date = start_date + timedelta(days=30)
                amount = 1200.00
                subscription = Subscription(
                    customer_id=customer.id,
                    type='monthly',
                    status='active',
                    start_date=start_date,
                    end_date=end_date,
                    amount=amount
                )
            elif sub_type == 'coins':
                coins_purchased = random.choice([20, 30, 40, 50])
                coins_used = random.randint(0, coins_purchased // 2)
                amount = coins_purchased * 40.00
                subscription = Subscription(
                    customer_id=customer.id,
                    type='coins',
                    status='active',
                    coins_purchased=coins_purchased,
                    coins_remaining=coins_purchased - coins_used,
                    amount=amount,
                    created_at=today - timedelta(days=random.randint(1, 60))
                )
            else:  # sessions
                sessions_purchased = random.choice([12, 16, 20, 24])
                sessions_used = random.randint(0, sessions_purchased // 2)
                amount = sessions_purchased * 80.00
                subscription = Subscription(
                    customer_id=customer.id,
                    type='sessions',
                    status='active',
                    sessions_purchased=sessions_purchased,
                    sessions_remaining=sessions_purchased - sessions_used,
                    amount=amount,
                    created_at=today - timedelta(days=random.randint(1, 60))
                )
            
            db.session.add(subscription)
            active_count += 1
        
        elif expired_count < 63:
            # Create expired subscription
            start_date = today - timedelta(days=random.randint(40, 90))
            end_date = start_date + timedelta(days=30)
            subscription = Subscription(
                customer_id=customer.id,
                type='monthly',
                status='expired',
                start_date=start_date,
                end_date=end_date,
                amount=1200.00
            )
            db.session.add(subscription)
            expired_count += 1
        
        sub_id += 1
    
    db.session.commit()
    print(f"  ✓ Active subscriptions: {active_count}")
    print(f"  ✓ Expired subscriptions: {expired_count}")
    print(f"\n✅ Created {active_count + expired_count} total subscriptions")

def seed_payments():
    """Create payment records for all subscriptions"""
    print("\n💰 CREATING PAYMENT RECORDS")
    print("-" * 80)
    
    subscriptions = Subscription.query.all()
    payment_methods = ['cash', 'cash', 'cash', 'card', 'card', 'online']
    
    for subscription in subscriptions:
        payment = Payment(
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            amount=subscription.amount,
            payment_method=random.choice(payment_methods),
            payment_date=subscription.start_date or subscription.created_at,
            status='completed'
        )
        db.session.add(payment)
    
    db.session.commit()
    print(f"✅ Created {len(subscriptions)} payment records")

def seed_expenses():
    """Create 45 expense records"""
    print("\n💵 CREATING EXPENSE RECORDS")
    print("-" * 80)
    
    categories = ['salary', 'equipment', 'utilities', 'maintenance', 'other']
    statuses = ['pending'] * 10 + ['approved'] * 25 + ['rejected'] * 10
    random.shuffle(statuses)
    
    for i in range(45):
        expense = Expense(
            branch_id=random.randint(1, 3),
            category=random.choice(categories),
            amount=round(random.uniform(500, 5000), 2),
            description=f"Expense description {i+1}",
            status=statuses[i],
            requested_by=random.randint(2, 14),
            request_date=datetime.now() - timedelta(days=random.randint(1, 60)),
            urgency=random.choice(['normal', 'high', 'urgent'])
        )
        db.session.add(expense)
    
    db.session.commit()
    print(f"✅ Created 45 expenses (10 pending, 25 approved, 10 rejected)")

def seed_attendance():
    """Create 500+ attendance records"""
    print("\n📝 CREATING ATTENDANCE RECORDS")
    print("-" * 80)
    
    customers = Customer.query.all()
    today = datetime.now()
    
    count = 0
    for customer in customers[:100]:  # First 100 active customers
        visits = random.randint(3, 8)
        for _ in range(visits):
            attendance = Attendance(
                customer_id=customer.id,
                check_in_time=today - timedelta(days=random.randint(1, 30)),
                check_out_time=today - timedelta(days=random.randint(1, 30), hours=2)
            )
            db.session.add(attendance)
            count += 1
    
    db.session.commit()
    print(f"✅ Created {count} attendance records")

def seed_complaints():
    """Create 20 complaint records"""
    print("\n📢 CREATING COMPLAINT RECORDS")
    print("-" * 80)
    
    statuses = ['pending'] * 8 + ['investigating'] * 7 + ['resolved'] * 5
    priorities = ['low'] * 4 + ['medium'] * 8 + ['high'] * 5 + ['critical'] * 3
    categories = ['equipment', 'staff', 'cleanliness', 'schedule', 'other']
    
    for i in range(20):
        complaint = Complaint(
            customer_id=random.randint(1, 150),
            branch_id=random.randint(1, 3),
            category=random.choice(categories),
            title=f"Complaint {i+1}",
            description=f"Description of complaint {i+1}",
            status=statuses[i],
            priority=priorities[i],
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        db.session.add(complaint)
    
    db.session.commit()
    print(f"✅ Created 20 complaints")

if __name__ == '__main__':
    seed_all()
```

---

## 🧪 TESTING AFTER IMPLEMENTATION

### Test 1: Staff Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "owner", "password": "owner123"}'
```
**Expected:** JWT token + user details

### Test 2: Get Customers (Check Temporary Passwords)
```bash
curl -X GET http://localhost:5000/api/customers \
  -H "Authorization: Bearer {staff_token}"
```
**Expected Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "full_name": "Mohamed Salem",
        "phone": "01077827639",
        "password_changed": false,
        "temporary_password": "RX04AF"  // ← THIS MUST APPEAR
      }
    ]
  }
}
```

### Test 3: Client Login (First Time)
```bash
curl -X POST http://localhost:5000/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "01077827639", "password": "RX04AF"}'
```
**Expected:** JWT token + customer details with `password_changed: false`

### Test 4: Change Password
```bash
curl -X POST http://localhost:5000/api/client/auth/change-password \
  -H "Authorization: Bearer {client_token}" \
  -H "Content-Type: application/json" \
  -d '{"old_password": "RX04AF", "new_password": "MyNewPass123"}'
```
**Expected:** Success message, backend sets `password_changed = true` and clears `plain_temporary_password`

### Test 5: Get Customers Again (After Password Change)
```bash
curl -X GET http://localhost:5000/api/customers/{customer_id} \
  -H "Authorization: Bearer {staff_token}"
```
**Expected:** `temporary_password` field should NOT be present (because `password_changed = true`)

### Test 6: Owner Dashboard Data
```bash
curl -X GET http://localhost:5000/api/reports/revenue \
  -H "Authorization: Bearer {owner_token}"
```
**Expected:**
```json
{
  "status": "success",
  "data": {
    "total_revenue": 164521.50,
    "active_subscriptions": 87,
    "total_customers": 150
  }
}
```

---

## 📝 SUMMARY

**What You Need to Implement:**
1. ✅ 60+ API endpoints (staff + client apps)
2. ✅ Temporary password system (BOTH hashed + plain storage)
3. ✅ Complete seed script (150 customers with visible passwords)
4. ✅ JWT authentication (separate for staff and clients)
5. ✅ QR code check-in with session/coin deduction

**Key Success Criteria:**
- Reception can see temporary passwords for first-time users
- Client login works with temporary password
- Client is forced to change password on first login
- After password change, plain password is cleared
- Owner dashboard shows real data (150 customers, 87 subs, 164k revenue)
- QR scanner can deduct sessions/coins

**Time Estimate:** 8-12 hours for complete implementation

---

**All specifications are complete. Implement exactly as described and the Flutter app will work perfectly!**

