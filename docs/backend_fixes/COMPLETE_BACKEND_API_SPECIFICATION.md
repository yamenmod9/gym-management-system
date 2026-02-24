# 🎯 COMPLETE BACKEND API SPECIFICATION FOR GYM MANAGEMENT SYSTEM

**Date:** February 14, 2026  
**For:** Claude Sonnet 4.5 Backend Implementation  
**Purpose:** Complete list of ALL API endpoints needed for both Staff and Client apps

---

## 📱 STAFF APP ENDPOINTS (Owner, Manager, Accountant, Reception)

### 1. AUTHENTICATION & PROFILE

#### 1.1 Staff Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "owner",
  "password": "owner123"
}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "owner",
      "role": "owner",
      "branch_id": null,
      "full_name": "System Owner"
    }
  }
}
```

#### 1.2 Get Staff Profile
```http
GET /api/auth/profile
Authorization: Bearer {token}
```

#### 1.3 Staff Logout
```http
POST /api/auth/logout
Authorization: Bearer {token}
```

---

### 2. OWNER DASHBOARD ENDPOINTS

#### 2.1 Revenue Report
```http
GET /api/reports/revenue
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional): Filter by branch
  - start_date: YYYY-MM-DD
  - end_date: YYYY-MM-DD
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_revenue": 164521.50,
    "active_subscriptions": 87,
    "total_customers": 150,
    "revenue_by_type": {
      "monthly": 89400.00,
      "coins": 45600.50,
      "sessions": 29521.00
    }
  }
}
```

#### 2.2 Smart Alerts
```http
GET /api/smart-alerts
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "id": 1,
        "type": "expiring_subscriptions",
        "severity": "warning",
        "title": "12 Subscriptions Expiring Soon",
        "message": "12 customer subscriptions will expire within 7 days",
        "count": 12,
        "branch_id": 1,
        "created_at": "2026-02-14T10:30:00"
      },
      {
        "id": 2,
        "type": "pending_approvals",
        "severity": "urgent",
        "title": "5 Expenses Pending Approval",
        "message": "5 expense requests awaiting your approval",
        "count": 5,
        "created_at": "2026-02-14T09:15:00"
      }
    ]
  }
}
```

#### 2.3 Branch Comparison
```http
GET /api/branches
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Dragon Club",
        "location": "Downtown Cairo",
        "status": "active",
        "capacity": 150,
        "phone": "021234567890",
        "email": "dragon@gym.com",
        "customer_count": 60,
        "active_subscriptions": 45,
        "monthly_revenue": 67800.00,
        "manager": {
          "id": 2,
          "name": "Ahmed Manager",
          "username": "manager_dragon"
        }
      },
      {
        "id": 2,
        "name": "Phoenix Fitness",
        "location": "Nasr City",
        "status": "active",
        "capacity": 120,
        "phone": "021234567891",
        "email": "phoenix@gym.com",
        "customer_count": 55,
        "active_subscriptions": 42,
        "monthly_revenue": 56221.50,
        "manager": {
          "id": 3,
          "name": "Sara Manager",
          "username": "manager_phoenix"
        }
      },
      {
        "id": 3,
        "name": "Tiger Gym",
        "location": "Heliopolis",
        "status": "active",
        "capacity": 100,
        "phone": "021234567892",
        "email": "tiger@gym.com",
        "customer_count": 35,
        "active_subscriptions": 28,
        "monthly_revenue": 40500.00,
        "manager": {
          "id": 4,
          "name": "Mohamed Manager",
          "username": "manager_tiger"
        }
      }
    ],
    "total": 3
  }
}
```

#### 2.4 Staff/Employees List
```http
GET /api/users
Authorization: Bearer {token}
Query Parameters:
  - role (optional): owner|manager|reception|accountant
  - branch_id (optional)
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 2,
        "username": "manager_dragon",
        "role": "manager",
        "full_name": "Ahmed Manager",
        "email": "manager.dragon@gym.com",
        "phone": "01234567890",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "is_active": true,
        "created_at": "2026-01-15T10:00:00"
      },
      {
        "id": 5,
        "username": "reception_dragon_1",
        "role": "reception",
        "full_name": "Fatma Reception",
        "email": "reception1@gym.com",
        "phone": "01234567893",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "is_active": true,
        "created_at": "2026-01-20T14:30:00"
      }
    ],
    "total": 14
  }
}
```

#### 2.5 Branch Details
```http
GET /api/branches/{branch_id}
Authorization: Bearer {token}
```

#### 2.6 Complaints List
```http
GET /api/complaints
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - status (optional): pending|investigating|resolved|rejected
```

---

### 3. CUSTOMER MANAGEMENT ENDPOINTS

#### 3.1 Get Customers List
```http
GET /api/customers
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional): Filter by branch
  - page (optional): Page number (default: 1)
  - limit (optional): Items per page (default: 20)
  - search (optional): Search by name, phone, email
  - status (optional): active|inactive
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "email": "customer1@example.com",
        "qr_code": "CUST-001-DRAGON",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "is_active": true,
        "password_changed": false,
        "temporary_password": "RX04AF",
        "has_active_subscription": true,
        "height": 175,
        "weight": 80,
        "bmi": 26.1,
        "gender": "male",
        "created_at": "2026-01-20T10:30:00",
        "active_subscription": {
          "id": 1,
          "type": "monthly",
          "status": "active",
          "start_date": "2026-02-01",
          "end_date": "2026-03-01",
          "remaining_days": 15,
          "amount": 1200.00
        }
      }
    ],
    "total": 150,
    "page": 1,
    "pages": 8
  }
}
```

**IMPORTANT:** The `temporary_password` field should ONLY be visible when `password_changed = false`. This is the plain text password (e.g., "RX04AF") that reception staff need to give to the customer for first-time login.

#### 3.2 Get Single Customer
```http
GET /api/customers/{customer_id}
Authorization: Bearer {token}
```

#### 3.3 Register New Customer
```http
POST /api/customers/register
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Ahmed Hassan",
  "phone": "01234567890",
  "email": "ahmed@example.com",
  "branch_id": 1,
  "gender": "male",
  "date_of_birth": "1995-05-15",
  "height": 178,
  "weight": 75,
  "health_notes": "No known allergies",
  "address": "123 Cairo Street"
}
```
**Response (201):**
```json
{
  "status": "success",
  "message": "Customer registered successfully",
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "CUST-151-DRAGON",
    "temporary_password": "AB12CD",
    "password_changed": false,
    "branch_id": 1,
    "note": "Give these credentials to the customer for their mobile app login"
  }
}
```

#### 3.4 Update Customer
```http
PUT /api/customers/{customer_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Ahmed Hassan Updated",
  "email": "newemail@example.com",
  "weight": 76,
  "height": 178,
  "is_active": true
}
```

#### 3.5 Delete Customer
```http
DELETE /api/customers/{customer_id}
Authorization: Bearer {token}
```

#### 3.6 Get Customer QR Code
```http
GET /api/customers/{customer_id}/qr-code
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "qr_code": "CUST-001-DRAGON",
    "qr_image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

---

### 4. SUBSCRIPTION MANAGEMENT ENDPOINTS

#### 4.1 Get Subscriptions List
```http
GET /api/subscriptions
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - customer_id (optional)
  - status (optional): active|expired|cancelled
  - type (optional): monthly|sessions|coins
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "customer_id": 1,
        "customer_name": "Mohamed Salem",
        "customer_phone": "01077827638",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "type": "monthly",
        "status": "active",
        "start_date": "2026-02-01",
        "end_date": "2026-03-01",
        "amount": 1200.00,
        "created_at": "2026-02-01T10:00:00"
      },
      {
        "id": 2,
        "customer_id": 2,
        "customer_name": "Layla Rashad",
        "customer_phone": "01022981052",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "type": "coins",
        "status": "active",
        "coins_purchased": 20,
        "coins_remaining": 15,
        "amount": 800.00,
        "created_at": "2026-01-25T14:30:00"
      },
      {
        "id": 3,
        "customer_id": 3,
        "customer_name": "Ibrahim Hassan",
        "customer_phone": "01041244663",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "type": "sessions",
        "status": "active",
        "sessions_purchased": 12,
        "sessions_remaining": 8,
        "amount": 960.00,
        "created_at": "2026-02-05T16:45:00"
      }
    ],
    "total": 87
  }
}
```

#### 4.2 Create New Subscription
```http
POST /api/subscriptions
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 151,
  "type": "monthly",
  "start_date": "2026-02-15",
  "amount": 1200.00,
  "payment_method": "cash",
  "notes": "First subscription"
}
```
**Response (201):**
```json
{
  "status": "success",
  "message": "Subscription created successfully",
  "data": {
    "id": 88,
    "customer_id": 151,
    "type": "monthly",
    "status": "active",
    "start_date": "2026-02-15",
    "end_date": "2026-03-15",
    "amount": 1200.00
  }
}
```

#### 4.3 Deduct Session/Coin (QR Scan Check-in)
```http
POST /api/subscriptions/{subscription_id}/deduct
Authorization: Bearer {token}
Content-Type: application/json

{
  "type": "checkin",
  "notes": "Gym entry via QR scan"
}
```
**Response (200):**
```json
{
  "status": "success",
  "message": "Session deducted successfully",
  "data": {
    "subscription_id": 2,
    "previous_remaining": 15,
    "new_remaining": 14,
    "type": "coins"
  }
}
```

#### 4.4 Update Subscription Status
```http
PATCH /api/subscriptions/{subscription_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "cancelled",
  "reason": "Customer request"
}
```

---

### 5. ATTENDANCE & CHECK-IN ENDPOINTS

#### 5.1 Record Attendance (QR Scan)
```http
POST /api/attendance
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 1,
  "qr_code": "CUST-001-DRAGON",
  "check_in_time": "2026-02-14T08:30:00",
  "subscription_id": 1,
  "deduct_session": true
}
```

#### 5.2 Get Attendance History
```http
GET /api/attendance
Authorization: Bearer {token}
Query Parameters:
  - customer_id (optional)
  - branch_id (optional)
  - date (optional): YYYY-MM-DD
  - start_date, end_date (optional)
```

---

### 6. PAYMENT ENDPOINTS

#### 6.1 Record Payment
```http
POST /api/payments
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 151,
  "subscription_id": 88,
  "amount": 1200.00,
  "payment_method": "cash",
  "payment_date": "2026-02-15",
  "notes": "First payment"
}
```

#### 6.2 Get Payments List
```http
GET /api/payments
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - customer_id (optional)
  - start_date, end_date (optional)
  - payment_method (optional): cash|card|online
```

---

### 7. EXPENSE MANAGEMENT ENDPOINTS

#### 7.1 Get Expenses List
```http
GET /api/expenses
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - status (optional): pending|approved|rejected
  - category (optional): salary|equipment|utilities|maintenance|other
  - start_date, end_date (optional)
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "category": "equipment",
        "amount": 5000.00,
        "description": "New treadmill purchase",
        "status": "pending",
        "requested_by": "reception_dragon_1",
        "request_date": "2026-02-10",
        "urgency": "urgent",
        "receipt_url": "/uploads/receipts/receipt_001.pdf"
      },
      {
        "id": 2,
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "category": "utilities",
        "amount": 2500.00,
        "description": "Electricity bill - January",
        "status": "approved",
        "requested_by": "manager_dragon",
        "request_date": "2026-02-05",
        "approved_by": "owner",
        "approval_date": "2026-02-06",
        "urgency": "high"
      }
    ],
    "total": 45,
    "pending_count": 10,
    "urgent_count": 3
  }
}
```

#### 7.2 Create Expense
```http
POST /api/expenses
Authorization: Bearer {token}
Content-Type: application/json

{
  "branch_id": 1,
  "category": "equipment",
  "amount": 5000.00,
  "description": "New weights set",
  "urgency": "normal",
  "receipt_file": "base64_encoded_file_data"
}
```

#### 7.3 Approve/Reject Expense
```http
PATCH /api/expenses/{expense_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "approved",
  "notes": "Approved for equipment upgrade"
}
```

---

### 8. COMPLAINT MANAGEMENT ENDPOINTS

#### 8.1 Get Complaints List
```http
GET /api/complaints
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - status (optional): pending|investigating|resolved|rejected
  - priority (optional): low|medium|high|critical
```

#### 8.2 Update Complaint Status
```http
PATCH /api/complaints/{complaint_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "resolved",
  "resolution_notes": "Issue fixed, new equipment installed"
}
```

---

### 9. REPORTS ENDPOINTS

#### 9.1 Revenue Report
```http
GET /api/reports/revenue
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - start_date: YYYY-MM-DD
  - end_date: YYYY-MM-DD
  - group_by (optional): day|week|month
```

#### 9.2 Customer Analytics
```http
GET /api/reports/customers
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - metric: total|active|inactive|new|retention
```

#### 9.3 Subscription Analytics
```http
GET /api/reports/subscriptions
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
  - type (optional): monthly|sessions|coins
  - status (optional): active|expired|expiring_soon
```

---

## 📱 CLIENT APP ENDPOINTS (Customer Mobile App)

### 10. CLIENT AUTHENTICATION

#### 10.1 Client Login
```http
POST /api/client/auth/login
Content-Type: application/json

{
  "phone": "01077827638",
  "password": "RX04AF"
}
```
**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "customer": {
      "id": 1,
      "full_name": "Mohamed Salem",
      "phone": "01077827638",
      "email": "customer1@example.com",
      "qr_code": "CUST-001-DRAGON",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "password_changed": false,
      "is_active": true,
      "height": 175,
      "weight": 80,
      "bmi": 26.1,
      "bmi_category": "Overweight",
      "bmr": 1850.5,
      "daily_calories": 2868
    },
    "subscription": {
      "id": 1,
      "type": "monthly",
      "status": "active",
      "start_date": "2026-02-01",
      "end_date": "2026-03-01",
      "remaining_days": 15,
      "amount": 1200.00
    }
  }
}
```

**Error Responses:**
```json
// 401 - Invalid credentials
{
  "status": "error",
  "message": "Invalid phone or password",
  "code": "INVALID_CREDENTIALS"
}

// 403 - Account inactive
{
  "status": "error",
  "message": "Your account is not active. Please contact reception.",
  "code": "ACCOUNT_INACTIVE"
}
```

#### 10.2 Change Password (First Time / Anytime)
```http
POST /api/client/auth/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "RX04AF",
  "new_password": "MyNewPassword123"
}
```
**Response (200):**
```json
{
  "status": "success",
  "message": "Password changed successfully",
  "data": {
    "password_changed": true
  }
}
```

**IMPORTANT BACKEND LOGIC:**
```python
# In change password endpoint:
# 1. Verify old_password matches customer.temporary_password (hashed)
# 2. Update customer.temporary_password with new hashed password
# 3. Set customer.password_changed = True
# 4. Clear customer.plain_temporary_password to NULL
```

#### 10.3 Get Client Profile
```http
GET /api/client/profile
Authorization: Bearer {token}
```

#### 10.4 Update Client Profile
```http
PUT /api/client/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "weight": 78,
  "height": 175
}
```

---

### 11. CLIENT SUBSCRIPTION ENDPOINTS

#### 11.1 Get My Active Subscription
```http
GET /api/client/subscription
Authorization: Bearer {token}
```

#### 11.2 Get Subscription History
```http
GET /api/client/subscriptions/history
Authorization: Bearer {token}
```

---

### 12. CLIENT ATTENDANCE ENDPOINTS

#### 12.1 Get My Attendance History
```http
GET /api/client/attendance
Authorization: Bearer {token}
Query Parameters:
  - limit (optional): Number of records (default: 30)
  - start_date, end_date (optional)
```

---

### 13. CLIENT COMPLAINT ENDPOINTS

#### 13.1 Submit Complaint
```http
POST /api/client/complaints
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Broken equipment",
  "description": "Treadmill #3 is not working",
  "category": "equipment",
  "priority": "high"
}
```

#### 13.2 Get My Complaints
```http
GET /api/client/complaints
Authorization: Bearer {token}
```

---

### 14. CLIENT QR CODE ENDPOINT

#### 14.1 Get My QR Code
```http
GET /api/client/qr-code
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "qr_code": "CUST-001-DRAGON",
    "qr_image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "customer_id": 1,
    "valid_until": "2026-03-01"
  }
}
```

---

## 🌱 SEED DATA REQUIREMENTS

### Database Seeding Script (`seed.py`) Must Create:

#### 1. Staff Users (14 total)
```python
# 1 Owner
{
  "username": "owner",
  "password": "owner123",  # hashed
  "role": "owner",
  "full_name": "System Owner",
  "email": "owner@gym.com",
  "phone": "01000000000"
}

# 3 Branch Managers (1 per branch)
{
  "username": "manager_dragon",
  "password": "manager123",  # hashed
  "role": "manager",
  "branch_id": 1,
  "full_name": "Ahmed Manager",
  "email": "manager.dragon@gym.com",
  "phone": "01234567890"
}
# ... manager_phoenix (branch 2), manager_tiger (branch 3)

# 6 Receptionists (2 per branch)
{
  "username": "reception_dragon_1",
  "password": "reception123",  # hashed
  "role": "reception",
  "branch_id": 1,
  "full_name": "Fatma Reception",
  "email": "reception1.dragon@gym.com",
  "phone": "01234567893"
}
# ... reception_dragon_2, reception_phoenix_1, reception_phoenix_2, reception_tiger_1, reception_tiger_2

# 4 Accountants (1 central + 3 branch)
{
  "username": "accountant_central",
  "password": "accountant123",  # hashed
  "role": "accountant",
  "branch_id": null,
  "full_name": "Heba Accountant",
  "email": "accountant.central@gym.com",
  "phone": "01234567897"
}
# ... accountant_dragon, accountant_phoenix, accountant_tiger
```

#### 2. Branches (3 total)
```python
[
  {
    "id": 1,
    "name": "Dragon Club",
    "location": "Downtown Cairo",
    "address": "123 Main Street, Cairo",
    "phone": "021234567890",
    "email": "dragon@gym.com",
    "capacity": 150,
    "status": "active"
  },
  {
    "id": 2,
    "name": "Phoenix Fitness",
    "location": "Nasr City",
    "address": "456 Nasr Street, Cairo",
    "phone": "021234567891",
    "email": "phoenix@gym.com",
    "capacity": 120,
    "status": "active"
  },
  {
    "id": 3,
    "name": "Tiger Gym",
    "location": "Heliopolis",
    "address": "789 Heliopolis Ave, Cairo",
    "phone": "021234567892",
    "email": "tiger@gym.com",
    "capacity": 100,
    "status": "active"
  }
]
```

#### 3. Customers (150 total: 60 for branch 1, 55 for branch 2, 35 for branch 3)

**CRITICAL:** For EACH customer, generate:
- 6-character temporary password (uppercase letters + digits only)
- Example: "AB12CD", "RX04AF", "SI19IC", "PS02HC", "PE71JZ", etc.
- Store BOTH:
  - `temporary_password`: Hashed version (for authentication)
  - `plain_temporary_password`: Plain text (for staff to view)
- Set `password_changed = False` for HALF of customers (75 total)
- Set `password_changed = True` and `plain_temporary_password = NULL` for other half

**Example Customer Record:**
```python
import random
import string
from werkzeug.security import generate_password_hash

def generate_temp_password(length=6):
    """Generate 6-character temporary password"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# For branch 1: Dragon Club (60 customers)
for i in range(1, 61):
    plain_password = generate_temp_password()  # e.g., "RX04AF"
    password_changed = i > 30  # First 30: not changed, last 30: changed
    
    customer = {
        "id": i,
        "full_name": f"Customer {i} Dragon",
        "phone": f"010{77827638 + i}",  # 01077827639, 01077827640, etc.
        "email": f"customer{i}@example.com",
        "qr_code": f"CUST-{i:03d}-DRAGON",
        "branch_id": 1,
        "gender": random.choice(["male", "female"]),
        "date_of_birth": f"{random.randint(1985, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "height": round(random.uniform(160, 190), 2),
        "weight": round(random.uniform(60, 100), 1),
        "temporary_password": generate_password_hash(plain_password),  # Hashed
        "plain_temporary_password": plain_password if not password_changed else None,  # Plain
        "password_changed": password_changed,
        "is_active": True,
        "created_at": "2026-01-20T10:00:00"
    }
    
    # Print credentials for first-time users
    if not password_changed:
        print(f"Phone: {customer['phone']} | Password: {plain_password} | QR: {customer['qr_code']}")
```

**Expected Seed Output:**
```
======================================================================
👤 CREATING 150 CUSTOMERS WITH TEMPORARY PASSWORDS
======================================================================

📋 FIRST-TIME LOGIN CREDENTIALS (password_changed=False):
----------------------------------------------------------------------
Phone: 01077827639 | Password: RX04AF | QR: CUST-001-DRAGON
Phone: 01077827640 | Password: SI19IC | QR: CUST-002-DRAGON
Phone: 01077827641 | Password: PS02HC | QR: CUST-003-DRAGON
... (75 total with visible passwords)
----------------------------------------------------------------------

✅ Created 150 customers
   - Dragon Club: 60 (30 first-time, 30 changed password)
   - Phoenix Fitness: 55 (27 first-time, 28 changed password)
   - Tiger Gym: 35 (18 first-time, 17 changed password)
======================================================================
```

#### 4. Subscriptions (87 active, 63 inactive)
- **Monthly subscriptions** (60 total, 45 active): 1200 EGP each
- **Coins subscriptions** (50 total, 25 active): 40 EGP per coin, 20-50 coins
- **Sessions subscriptions** (40 total, 17 active): 80 EGP per session, 12-24 sessions

**Distribution by branch:**
- Branch 1 (Dragon Club): 45 active, 35 expired
- Branch 2 (Phoenix Fitness): 27 active, 18 expired
- Branch 3 (Tiger Gym): 15 active, 10 expired

#### 5. Payments (150+ records)
- Match each active subscription with payment record
- Payment methods: 60% cash, 30% card, 10% online
- Dates: Spread across last 60 days

#### 6. Expenses (45 total)
```python
# Status breakdown:
# - 10 pending (3 urgent, 7 high/normal)
# - 25 approved
# - 10 rejected

# Categories:
# - Salary: 15 records
# - Equipment: 12 records
# - Utilities: 10 records
# - Maintenance: 8 records
```

#### 7. Attendance Records (500+ records)
- Link to active customers
- Spread across last 30 days
- Match with session/coin subscriptions

#### 8. Complaints (20 total)
```python
# Status: 8 pending, 7 investigating, 5 resolved
# Priority: 3 critical, 5 high, 8 medium, 4 low
# Categories: equipment, staff, cleanliness, schedule, other
```

---

## ✅ TESTING REQUIREMENTS

### After implementing all endpoints, test with:

#### Staff App Testing:
1. Login as owner → See 3 branches, 150 customers, 164,521 EGP revenue
2. Login as manager (branch 1) → See 60 customers, 45 active subs, branch metrics
3. Login as reception → Register new customer → Get temporary password → Give to customer
4. Login as accountant → See 10 pending expenses, daily sales, payment records
5. Reception QR scan → Find customer by QR → Deduct session → Verify remaining count

#### Client App Testing:
1. Get first-time customer phone + temp password from reception
2. Login with phone: 01077827639, password: RX04AF (from seed data)
3. App detects `password_changed = false` → Force password change screen
4. Enter old password: RX04AF, new password: MyNewPass123
5. Backend sets `password_changed = true`, clears `plain_temporary_password`
6. Logout and login again with new password → Success
7. View active subscription details, remaining sessions/coins
8. View QR code for gym entry
9. View attendance history
10. Submit complaint

---

## 🎯 CRITICAL IMPLEMENTATION NOTES

### 1. Authentication Flow
- Staff tokens: 1 day expiry, type: 'staff'
- Client tokens: 7 days expiry, type: 'client'
- Always verify token type in protected endpoints

### 2. Password Management
- Staff passwords: Hashed with bcrypt/werkzeug
- Customer temporary passwords: 
  - 6 characters (uppercase + digits)
  - Store BOTH hashed (for auth) AND plain (for staff viewing)
  - Clear plain password when customer changes it

### 3. QR Code Format
- Format: `CUST-{id:03d}-{BRANCH_NAME}`
- Examples: "CUST-001-DRAGON", "CUST-152-PHOENIX"
- Must be unique per customer

### 4. Subscription Logic
- Monthly: Fixed dates, no deductions
- Sessions: Track remaining sessions, deduct on check-in
- Coins: Track remaining coins, deduct on check-in
- Auto-expire subscriptions past end_date

### 5. Data Calculations
- BMI: weight / (height * height)
- BMR: Mifflin-St Jeor equation
- Revenue: Sum of active subscription amounts
- Active subs: Count where status='active' AND end_date > today

---

## 📖 SUMMARY

**Total Endpoints Required:** ~60  
**Staff App Endpoints:** ~45  
**Client App Endpoints:** ~15  

**Seed Data Records:**
- 14 staff users
- 3 branches
- 150 customers (with plain passwords for first-time users)
- 87 active subscriptions
- 150+ payments
- 45 expenses
- 500+ attendance records
- 20 complaints

**Priority Order:**
1. ✅ Authentication endpoints (staff + client)
2. ✅ Customer management (CRUD + temporary password display)
3. ✅ Subscription management + QR check-in
4. ✅ Dashboard data endpoints (revenue, branches, staff)
5. ✅ Payments, expenses, complaints
6. ✅ Attendance tracking
7. ✅ Reports

---

**This specification is complete and ready for implementation. All endpoints are required for full app functionality.**

