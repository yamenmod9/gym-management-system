# 🎯 COMPLETE BACKEND ENDPOINTS & SEED DATA REQUIREMENTS

## For Claude Sonnet 4.5 - Backend Implementation

---

# PART 1: STAFF APP BACKEND ENDPOINTS

## 1. OWNER ENDPOINTS

### Dashboard Overview
```
GET /api/owner/dashboard
Authorization: Bearer <token>

Response:
{
  "total_revenue": 125000.0,
  "active_subscriptions": 45,
  "total_customers": 150,
  "total_branches": 3,
  "total_staff": 9,
  "recent_alerts": [...]
}
```

### Get All Customers (No Branch Filter for Owner)
```
GET /api/customers
Authorization: Bearer <token>

Response:
{
  "data": {
    "items": [
      {
        "id": 1,
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "email": "customer1@example.com",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "temporary_password": "RX04AF",  // Only if password_changed == false AND requester is staff
        "password_changed": false,
        "qr_code": "CUST-00001-001-ABC123",
        "is_active": true,
        "has_active_subscription": true,
        "height": 175.0,
        "weight": 80.0,
        "bmi": 26.1,
        "bmr": 1850.5,
        "daily_calories": 2868,
        "created_at": "2026-02-14T10:00:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "per_page": 20
  }
}
```

### Get All Subscriptions (No Branch Filter for Owner)
```
GET /api/subscriptions
Authorization: Bearer <token>

Response:
{
  "data": {
    "items": [
      {
        "id": 1,
        "customer_id": 1,
        "customer_name": "Mohamed Salem",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "type": "Monthly",
        "amount": 1500.0,
        "status": "active",
        "start_date": "2026-02-01",
        "end_date": "2026-03-01",
        "remaining_sessions": 12,
        "remaining_coins": 0,
        "created_at": "2026-02-01T10:00:00Z"
      }
    ],
    "total": 45
  }
}
```

### Get All Branches
```
GET /api/branches
Authorization: Bearer <token>

Response:
{
  "data": [
    {
      "id": 1,
      "name": "Dragon Club",
      "location": "Nasr City, Cairo",
      "phone": "02-12345678",
      "is_active": true,
      "customer_count": 50,
      "revenue": 45000.0,
      "active_subscriptions": 15
    },
    {
      "id": 2,
      "name": "Monster Fitness",
      "location": "Maadi, Cairo",
      "phone": "02-87654321",
      "is_active": true,
      "customer_count": 60,
      "revenue": 50000.0,
      "active_subscriptions": 18
    },
    {
      "id": 3,
      "name": "Beast Gym",
      "location": "6th October City",
      "phone": "02-11223344",
      "is_active": true,
      "customer_count": 40,
      "revenue": 30000.0,
      "active_subscriptions": 12
    }
  ]
}
```

### Get All Staff Members
```
GET /api/users?role=staff
Authorization: Bearer <token>

Response:
{
  "data": [
    {
      "id": 2,
      "username": "manager_dragon_1",
      "full_name": "Ahmed Manager",
      "role": "manager",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "email": "manager1@gym.com",
      "phone": "01011111111",
      "is_active": true
    },
    {
      "id": 3,
      "username": "reception_dragon_1",
      "full_name": "Fatima Reception",
      "role": "reception",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "email": "reception1@gym.com",
      "phone": "01022222222",
      "is_active": true
    }
    // ... 7 more staff members (3 managers, 3 receptionists, 3 accountants)
  ]
}
```

---

## 2. MANAGER ENDPOINTS

### Manager Dashboard (Branch-Specific)
```
GET /api/manager/dashboard
Authorization: Bearer <token>

Response:
{
  "branch_id": 1,
  "branch_name": "Dragon Club",
  "total_customers": 50,
  "active_subscriptions": 15,
  "branch_revenue": 45000.0,
  "today_check_ins": 23,
  "staff_count": 3
}
```

### Get Customers by Branch
```
GET /api/customers?branch_id=1
Authorization: Bearer <token>

Response: Same format as owner's customer list, but filtered by branch
```

---

## 3. ACCOUNTANT ENDPOINTS

### Accountant Dashboard
```
GET /api/accountant/dashboard
Authorization: Bearer <token>

Response:
{
  "today_sales": 5000.0,
  "payment_count": 12,
  "today_expenses": 2000.0,
  "net_profit": 3000.0,
  "pending_invoices": 3
}
```

### Get All Payments
```
GET /api/payments
Authorization: Bearer <token>
Query params: ?start_date=2026-02-01&end_date=2026-02-14

Response:
{
  "data": {
    "items": [
      {
        "id": 1,
        "customer_id": 1,
        "customer_name": "Mohamed Salem",
        "subscription_id": 1,
        "amount": 1500.0,
        "payment_method": "cash",
        "payment_date": "2026-02-01T10:00:00Z",
        "receipt_number": "REC-001-2026"
      }
    ],
    "total_amount": 54000.0,
    "total_count": 36
  }
}
```

### Get All Expenses
```
GET /api/expenses
Authorization: Bearer <token>
Query params: ?start_date=2026-02-01&end_date=2026-02-14

Response:
{
  "data": {
    "items": [
      {
        "id": 1,
        "category": "Equipment",
        "description": "Dumbbells set",
        "amount": 3000.0,
        "expense_date": "2026-02-05",
        "approved_by": "owner1",
        "branch_id": 1
      }
    ],
    "total_amount": 18000.0,
    "total_count": 12
  }
}
```

---

## 4. RECEPTION ENDPOINTS

### Get Customers by Branch (Reception's Branch Only)
```
GET /api/staff/{branch_id}/customers
Authorization: Bearer <token>

Response: Same as customer list, filtered by reception's branch

IMPORTANT: Must include "temporary_password" field when:
- Customer's password_changed == false
- Requester is a staff member
```

### Register New Customer
```
POST /api/customers
Authorization: Bearer <token>

Request:
{
  "full_name": "New Customer",
  "phone": "01099999999",
  "email": "newcustomer@example.com",
  "date_of_birth": "1995-05-15",
  "gender": "male",
  "height": 180.0,
  "weight": 75.0,
  "address": "Cairo, Egypt",
  "national_id": "29505151234567",
  "health_notes": "None",
  "branch_id": 1
}

Response:
{
  "data": {
    "id": 151,
    "full_name": "New Customer",
    "phone": "01099999999",
    "email": "newcustomer@example.com",
    "temporary_password": "AB12CD",  // ← MUST RETURN THIS!
    "password_changed": false,
    "qr_code": "CUST-00151-001-XYZ789",
    "branch_id": 1,
    ...other fields
  },
  "message": "Customer registered successfully"
}
```

### QR Code Check-In
```
GET /api/customers/{customer_id}
Authorization: Bearer <token>

Response: Customer details with subscription

POST /api/customers/{customer_id}/check-in
Authorization: Bearer <token>

Request:
{
  "subscription_id": 1,
  "timestamp": "2026-02-14T14:30:00Z"
}

Response:
{
  "message": "Check-in successful",
  "remaining_sessions": 11,  // Decremented if session-based
  "remaining_coins": 95      // Decremented if coin-based (1 entry = 5 coins)
}
```

### Get Customer Subscription
```
GET /api/customers/{customer_id}/subscription
Authorization: Bearer <token>

Response:
{
  "data": {
    "id": 1,
    "type": "Monthly",
    "status": "active",
    "start_date": "2026-02-01",
    "end_date": "2026-03-01",
    "remaining_sessions": 12,
    "remaining_coins": 0,
    "amount": 1500.0
  }
}
```

---

# PART 2: CLIENT APP BACKEND ENDPOINTS

## 1. CLIENT AUTHENTICATION

### Login
```
POST /api/client/auth/login

Request:
{
  "phone": "01077827638",
  "password": "RX04AF"  // Temporary password on first login
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "customer": {
    "id": 1,
    "full_name": "Mohamed Salem",
    "phone": "01077827638",
    "email": "customer1@example.com",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "qr_code": "CUST-00001-001-ABC123",
    "password_changed": false,  // ← CRITICAL: Forces password change screen
    "is_active": true,
    "height": 175.0,
    "weight": 80.0,
    "bmi": 26.1,
    "bmr": 1850.5,
    "daily_calories": 2868
  },
  "subscription": {
    "status": "active",
    "type": "Monthly",
    "remaining_sessions": 12,
    "expires_at": "2026-03-01"
  }
}
```

### Change Password (First Time or Regular)
```
POST /api/client/auth/change-password
Authorization: Bearer <token>

Request:
{
  "old_password": "RX04AF",
  "new_password": "MySecurePassword123"
}

Response:
{
  "message": "Password changed successfully",
  "password_changed": true  // ← Set to true in database
}
```

---

## 2. CLIENT DASHBOARD

### Get My Profile
```
GET /api/client/profile
Authorization: Bearer <token>

Response: Same as customer object from login
```

### Get My Subscription
```
GET /api/client/subscription
Authorization: Bearer <token>

Response:
{
  "data": {
    "id": 1,
    "type": "Monthly",
    "status": "active",
    "start_date": "2026-02-01",
    "end_date": "2026-03-01",
    "remaining_sessions": 12,
    "remaining_coins": 0,
    "amount": 1500.0
  }
}
```

### Get My QR Code
```
GET /api/client/qr-code
Authorization: Bearer <token>

Response:
{
  "qr_code": "CUST-00001-001-ABC123",
  "format": "string"  // For QR code generation
}
```

### Get My Workout History
```
GET /api/client/check-ins
Authorization: Bearer <token>

Response:
{
  "data": {
    "items": [
      {
        "id": 1,
        "check_in_time": "2026-02-14T14:30:00Z",
        "branch_name": "Dragon Club",
        "session_deducted": true
      }
    ]
  }
}
```

### Submit Complaint
```
POST /api/client/complaints
Authorization: Bearer <token>

Request:
{
  "title": "Equipment Issue",
  "description": "Treadmill 3 is not working",
  "category": "equipment"
}

Response:
{
  "message": "Complaint submitted successfully",
  "complaint_id": 123
}
```

---

# PART 3: SEED DATA REQUIREMENTS

## seed.py Comprehensive Requirements

### 1. Create 3 Branches
```python
branches = [
    {
        "name": "Dragon Club",
        "location": "Nasr City, Cairo",
        "phone": "02-12345678",
        "email": "dragon@gym.com",
        "is_active": True
    },
    {
        "name": "Monster Fitness",
        "location": "Maadi, Cairo",
        "phone": "02-87654321",
        "email": "monster@gym.com",
        "is_active": True
    },
    {
        "name": "Beast Gym",
        "location": "6th October City",
        "phone": "02-11223344",
        "email": "beast@gym.com",
        "is_active": True
    }
]
```

### 2. Create Owner Account
```python
owner = User(
    username="owner1",
    email="owner@gym.com",
    role="owner",
    branch_id=None,  # Owner has access to ALL branches
    is_active=True
)
owner.set_password("owner123")
```

### 3. Create 3 Managers (1 per branch)
```python
managers = [
    {"username": "manager_dragon_1", "branch_id": 1, "password": "manager123"},
    {"username": "manager_monster_1", "branch_id": 2, "password": "manager123"},
    {"username": "manager_beast_1", "branch_id": 3, "password": "manager123"}
]
```

### 4. Create 3 Receptionists (1 per branch)
```python
receptionists = [
    {"username": "reception_dragon_1", "branch_id": 1, "password": "reception123"},
    {"username": "reception_monster_1", "branch_id": 2, "password": "reception123"},
    {"username": "reception_beast_1", "branch_id": 3, "password": "reception123"}
]
```

### 5. Create 3 Accountants (1 per branch)
```python
accountants = [
    {"username": "accountant_dragon_1", "branch_id": 1, "password": "accountant123"},
    {"username": "accountant_monster_1", "branch_id": 2, "password": "accountant123"},
    {"username": "accountant_beast_1", "branch_id": 3, "password": "accountant123"}
]
```

### 6. Create 150 Customers (50 per branch)

**CRITICAL: Each customer MUST have:**

```python
def generate_temp_password():
    """Generate 6-character password: AB12CD format"""
    import random, string
    letters1 = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{letters1}{numbers}{letters2}"

for i in range(1, 151):
    branch_id = ((i - 1) // 50) + 1  # Distribute: 1-50 → branch 1, 51-100 → branch 2, 101-150 → branch 3
    
    customer = Customer(
        full_name=f"Customer {i}",
        phone=f"010{str(i).zfill(8)}",
        email=f"customer{i}@example.com",
        date_of_birth="1990-01-01",
        gender="male" if i % 2 == 0 else "female",
        height=random.uniform(160, 190),
        weight=random.uniform(60, 100),
        address=f"{i} Street, Cairo",
        national_id=f"2900101{str(i).zfill(7)}",
        branch_id=branch_id,
        qr_code=f"CUST-{str(i).zfill(5)}-{str(branch_id).zfill(3)}-{generate_hash()}",
        temporary_password=generate_temp_password(),  # ← CRITICAL
        password_changed=False,  # ← CRITICAL: Initially false
        is_active=True
    )
    # Set hashed password to temporary_password initially
    customer.set_password(customer.temporary_password)
```

### 7. Create Sample Test Customers (For Easy Testing)
```python
test_customers = [
    {
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "email": "mohamed@example.com",
        "temporary_password": "RX04AF",
        "password_changed": False,
        "branch_id": 1
    },
    {
        "full_name": "Layla Rashad",
        "phone": "01022981052",
        "email": "layla@example.com",
        "temporary_password": "SI19IC",
        "password_changed": False,
        "branch_id": 1
    },
    {
        "full_name": "Ibrahim Hassan",
        "phone": "01041244663",
        "email": "ibrahim@example.com",
        "temporary_password": "PS02HC",
        "password_changed": False,
        "branch_id": 2
    }
]
```

### 8. Create Subscriptions (45 Active)
```python
# 15 subscriptions per branch, various types
subscription_types = ["Monthly", "3-Month", "6-Month", "Session-12", "Session-24", "Coins-100"]

for i in range(1, 46):
    subscription = Subscription(
        customer_id=i,  # First 45 customers have active subscriptions
        type=random.choice(subscription_types),
        status="active",
        amount=random.uniform(1000, 3000),
        start_date=date.today() - timedelta(days=random.randint(1, 30)),
        end_date=date.today() + timedelta(days=random.randint(15, 90)),
        remaining_sessions=random.randint(5, 24) if "Session" in type else 0,
        remaining_coins=random.randint(50, 100) if "Coins" in type else 0
    )
```

### 9. Create Payments
```python
for i in range(1, 37):
    payment = Payment(
        customer_id=random.randint(1, 150),
        subscription_id=random.randint(1, 45),
        amount=random.uniform(1000, 3000),
        payment_method=random.choice(["cash", "card", "bank_transfer"]),
        payment_date=date.today() - timedelta(days=random.randint(0, 14)),
        receipt_number=f"REC-{str(i).zfill(3)}-2026"
    )
```

### 10. Create Expenses
```python
expense_categories = ["Equipment", "Maintenance", "Utilities", "Salaries", "Marketing"]

for i in range(1, 13):
    expense = Expense(
        category=random.choice(expense_categories),
        description=f"Expense item {i}",
        amount=random.uniform(500, 5000),
        expense_date=date.today() - timedelta(days=random.randint(0, 14)),
        branch_id=random.randint(1, 3),
        approved_by=1  # Owner ID
    )
```

---

# PART 4: TESTING CHECKLIST

## Test Owner Dashboard
```
1. Login: owner1 / owner123
2. Expected Dashboard Data:
   - Total Revenue: ~125,000 EGP (sum of 45 active subscriptions)
   - Active Subscriptions: 45
   - Total Customers: 150
   - Branches Tab: Shows 3 branches (Dragon, Monster, Beast)
   - Staff Tab: Shows 9 staff members (3 managers + 3 receptionists + 3 accountants)
```

## Test Manager Dashboard
```
1. Login: manager_dragon_1 / manager123
2. Expected Dashboard Data:
   - Branch: Dragon Club
   - Total Customers: 50 (only Dragon Club customers)
   - Active Subscriptions: 15 (only Dragon Club subscriptions)
   - Branch Revenue: ~45,000 EGP
```

## Test Reception Features
```
1. Login: reception_dragon_1 / reception123
2. Navigate to "All Customers"
3. Expand customer "Mohamed Salem"
4. Expected to see:
   - Login: 01077827638
   - Password: RX04AF [Copy button]
   - Status: ⚠️ First-time login - password not changed yet
```

## Test Client App Login
```
1. Open client app
2. Login with: 01077827638 / RX04AF
3. Expected: Forced password change screen
4. Change password to: MyPassword123
5. Expected: Login successful, shows dashboard
6. Logout and login again with: 01077827638 / MyPassword123
7. Expected: Direct login, no password change prompt
```

## Test QR Scanner
```
1. Login as reception_dragon_1
2. Tap "Scan QR" button
3. Scan customer QR code: CUST-00001-001-ABC123
4. Expected: Show customer details, subscription status, check-in button
5. Tap "Confirm Check-In"
6. Expected: Success message, session/coins deducted
```

---

# SUMMARY OF CRITICAL FIXES NEEDED

## ✅ Already Fixed in Frontend:
1. StatCard pixel overflow
2. Settings screen logout button padding
3. Owner dashboard provider to fetch all data (no branch filtering)
4. QR scanner screen implementation
5. Customer list screen ready to display temp passwords

## ❌ Needs Backend Implementation:
1. **temporary_password field** in customer API responses (CRITICAL)
2. **password_changed field** in customer API responses
3. All branches endpoint (no filtering for owner)
4. All staff members endpoint
5. QR code check-in endpoint
6. Client app authentication endpoints
7. Seed data with 150 customers including temp passwords

---

*Document Created: February 14, 2026*
*For: Claude Sonnet 4.5 Backend Implementation*

