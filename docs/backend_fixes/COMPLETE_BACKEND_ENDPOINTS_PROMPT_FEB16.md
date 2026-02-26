# 🚀 COMPLETE BACKEND API ENDPOINTS - COMPREHENSIVE PROMPT FOR CLAUDE SONNET 4.5
**Date:** February 16, 2026  
**Purpose:** Complete API implementation guide for both Staff and Client apps

---

## 📌 CRITICAL ISSUES TO FIX

### 🔴 ISSUE 1: QR Check-In Error - "qr_code is required"
**Current Problem:** When receptionist scans QR code and tries to check in, backend returns:
```json
{
  "error": "qr_code is required",
  "success": false
}
```

**Frontend sends:**
```json
{
  "customer_id": 115,
  "qr_code": "customer_id:115",
  "check_in_time": "2026-02-16T13:00:00Z",
  "action": "check_in_only"
}
```

**Required Fix:** The `POST /api/attendance` endpoint must accept EITHER `qr_code` OR `customer_id` fields and extract the customer ID from the QR code if provided.

---

### 🔴 ISSUE 2: Subscription Expiry Logic
**Current Problem:** Subscriptions don't expire automatically.

**Required Logic:**
1. **Coins Subscriptions:**
   - Coins >= 30: Unlimited validity (never expire)
   - Coins < 30: 1 year validity from purchase date
   - Expire when: `remaining_coins == 0` OR `end_date < now()` (for coins < 30)

2. **Time-based Subscriptions:**
   - Expire when: `end_date < now()`

3. **Personal Training Subscriptions:**
   - Expire when: `remaining_sessions == 0` OR `end_date < now()`

**Backend Response Must Include:**
```json
{
  "subscription": {
    "type": "coins",
    "remaining_coins": 50,
    "display_metric": "coins",
    "display_value": 50,
    "display_label": "50 Coins",
    "validity": "unlimited",
    "end_date": null
  }
}
```

OR for coins < 30:
```json
{
  "subscription": {
    "type": "coins",
    "remaining_coins": 20,
    "display_metric": "coins",
    "display_value": 20,
    "display_label": "20 Coins",
    "validity": "1 year",
    "end_date": "2027-02-16"
  }
}
```

---

## 🏢 STAFF APP ENDPOINTS (55 Total)

### Base URL
```
https://yamenmod91.pythonanywhere.com/api
```

### Authentication Header
```
Authorization: Bearer <jwt_token>
```

---

## 1. AUTHENTICATION (2 Endpoints)

### 1.1 Staff Login ✅
```http
POST /api/staff/auth/login
```

**Request:**
```json
{
  "phone": "01012345678",
  "password": "owner123"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "full_name": "Ahmed Hassan",
      "phone": "01012345678",
      "role": "owner",
      "branch_id": 1,
      "branch_name": "Dragon Club"
    },
    "token": "eyJ..."
  }
}
```

**Roles:** `owner`, `manager`, `accountant`, `receptionist`

---

### 1.2 Staff Logout ✅
```http
POST /api/staff/auth/logout
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 2. DASHBOARD & OVERVIEW (8 Endpoints)

### 2.1 Owner Dashboard 🔴 FIX REQUIRED
```http
GET /api/dashboard/owner
Authorization: Bearer {token}
```

**Current Problem:** Returns all zeros despite having data in database.

**Required Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 145000.00,
    "total_customers": 150,
    "active_subscriptions": 120,
    "total_branches": 3,
    "monthly_revenue": 45000.00,
    "revenue_by_branch": [
      {"branch_name": "Dragon Club", "revenue": 50000.00},
      {"branch_name": "Phoenix Club", "revenue": 55000.00},
      {"branch_name": "Lions Fitness", "revenue": 40000.00}
    ],
    "recent_payments": [
      {
        "id": 1,
        "customer_name": "Mohamed Salem",
        "amount": 1200.00,
        "date": "2026-02-16",
        "branch_name": "Dragon Club"
      }
    ]
  }
}
```

---

### 2.2 Manager Dashboard 🔴 FIX REQUIRED
```http
GET /api/dashboard/manager
Authorization: Bearer {token}
```

**Current Problem:** Returns all zeros for branch-specific data.

**Required Response (200):**
```json
{
  "success": true,
  "data": {
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "branch_revenue": 50000.00,
    "branch_customers": 50,
    "active_subscriptions": 40,
    "monthly_revenue": 15000.00,
    "recent_check_ins": [
      {
        "customer_name": "Mohamed Salem",
        "check_in_time": "2026-02-16T14:30:00Z"
      }
    ]
  }
}
```

---

### 2.3 Accountant Dashboard 🔴 FIX REQUIRED
```http
GET /api/dashboard/accountant
Authorization: Bearer {token}
```

**Required Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 145000.00,
    "monthly_revenue": 45000.00,
    "pending_payments": 5000.00,
    "expenses": 20000.00,
    "net_profit": 25000.00,
    "payment_breakdown": {
      "cash": 80000.00,
      "card": 50000.00,
      "bank_transfer": 15000.00
    }
  }
}
```

---

### 2.4 Receptionist Dashboard ✅
```http
GET /api/dashboard/receptionist
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "today_check_ins": 25,
    "recent_customers": [
      {
        "id": 115,
        "full_name": "Adel Saad",
        "phone": "01025867870"
      }
    ],
    "active_subscriptions": 40
  }
}
```

---

### 2.5 Customer Count 🔴 FIX REQUIRED
```http
GET /api/dashboard/customers/count
Authorization: Bearer {token}
```

**Current Problem:** Returns 0 despite having 150 customers.

**Required Response (200):**
```json
{
  "success": true,
  "data": {
    "total": 150,
    "active": 145,
    "inactive": 5
  }
}
```

---

### 2.6 Active Subscriptions Count ✅
```http
GET /api/dashboard/subscriptions/active-count
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "count": 120
  }
}
```

---

### 2.7 Today's Check-ins ✅
```http
GET /api/dashboard/checkins/today
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "list": [
      {
        "customer_name": "Mohamed Salem",
        "time": "2026-02-16T14:30:00Z"
      }
    ]
  }
}
```

---

### 2.8 Monthly Revenue ✅
```http
GET /api/dashboard/revenue/monthly
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "current_month": 45000.00,
    "previous_month": 40000.00,
    "growth_percentage": 12.5
  }
}
```

---

## 3. CUSTOMER MANAGEMENT (6 Endpoints)

### 3.1 List Customers 🔴 FIX REQUIRED
```http
GET /api/customers
Authorization: Bearer {token}
Query Parameters: ?page=1&per_page=20&branch_id=1
```

**Current Problem:** Returns customers from other branches for non-owner users.

**Required Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 115,
        "full_name": "Adel Saad",
        "phone": "01025867870",
        "email": "customer115@example.com",
        "branch_id": 2,
        "branch_name": "Phoenix Club",
        "is_active": true,
        "qr_code": "customer_id:115",
        "temp_password": "AB12CD",
        "password_changed": false
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

**Business Logic:**
- Owner: See all customers from all branches
- Manager/Receptionist: See only customers from their branch
- Must include `temp_password` field (visible to staff)
- Must include `qr_code` field

---

### 3.2 Get Customer Details ✅ (WITH FIX)
```http
GET /api/customers/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 115,
    "full_name": "Adel Saad",
    "phone": "01025867870",
    "email": "customer115@example.com",
    "branch_id": 2,
    "branch_name": "Phoenix Club",
    "qr_code": "customer_id:115",
    "temp_password": "AB12CD",
    "password_changed": false,
    "is_active": true,
    "height": 172.0,
    "weight": 92.0,
    "bmi": 31.1,
    "age": 32
  }
}
```

**IMPORTANT:** Must return `temp_password` field for staff to view.

---

### 3.3 Create Customer ✅
```http
POST /api/customers
Authorization: Bearer {token}
```

**Request:**
```json
{
  "full_name": "John Doe",
  "phone": "01234567890",
  "email": "john@example.com",
  "branch_id": 1,
  "national_id": "29012345678901",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "height": 175,
  "weight": 80
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Customer created successfully",
  "data": {
    "id": 151,
    "qr_code": "customer_id:151",
    "temp_password": "XY34ZW"
  }
}
```

**Business Logic:**
- Auto-generate `qr_code` = `customer_id:{id}`
- Auto-generate `temp_password` (6 chars: 2 letters, 2 numbers, 2 letters)
- Set `password_changed` = false
- Calculate BMI, BMR, daily calories

---

### 3.4 Update Customer ✅
```http
PUT /api/customers/{id}
Authorization: Bearer {token}
```

**Request:**
```json
{
  "full_name": "John Doe Updated",
  "phone": "01234567890",
  "height": 176,
  "weight": 78
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Customer updated successfully"
}
```

---

### 3.5 Regenerate QR Code ✅
```http
POST /api/customers/{id}/regenerate-qr
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "QR code regenerated successfully",
  "data": {
    "qr_code": "customer_id:115"
  }
}
```

---

### 3.6 Regenerate Temporary Password ✅
```http
POST /api/customers/{id}/regenerate-password
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Temporary password regenerated",
  "data": {
    "temp_password": "CD56EF"
  }
}
```

**Business Logic:**
- Generate new 6-char password
- Set `password_changed` = false
- Notify customer (optional)

---

## 4. SUBSCRIPTION MANAGEMENT (8 Endpoints)

### 4.1 List Subscriptions ✅
```http
GET /api/subscriptions
Authorization: Bearer {token}
Query Parameters: ?customer_id=115&status=active&branch_id=1
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 124,
        "customer_id": 115,
        "customer_name": "Adel Saad",
        "customer_phone": "01025867870",
        "branch_id": 2,
        "service_id": 1,
        "type": "coins",
        "status": "active",
        "remaining_coins": 50,
        "display_metric": "coins",
        "display_value": 50,
        "display_label": "50 Coins",
        "validity": "unlimited",
        "start_date": "2026-02-16",
        "end_date": null,
        "created_at": "2026-02-16T13:00:29Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total": 150
    }
  }
}
```

---

### 4.2 Get Subscription Details ✅
```http
GET /api/subscriptions/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 124,
    "customer_id": 115,
    "type": "coins",
    "remaining_coins": 50,
    "display_metric": "coins",
    "display_value": 50,
    "display_label": "50 Coins",
    "validity": "unlimited",
    "status": "active"
  }
}
```

---

### 4.3 Activate Subscription 🔴 FIX REQUIRED
```http
POST /api/subscriptions/activate
Authorization: Bearer {token}
```

**Current Problem:** Error "Cannot create subscription for another branch" even though staff and customer are in the same branch.

**Request:**
```json
{
  "customer_id": 115,
  "service_id": 1,
  "branch_id": 1,
  "subscription_type": "coins",
  "coins": 50,
  "validity_months": null,
  "amount": 2000.00,
  "payment_method": "cash"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 151,
    "remaining_coins": 50,
    "display_metric": "coins",
    "display_value": 50,
    "display_label": "50 Coins",
    "validity": "unlimited",
    "end_date": null
  }
}
```

**Business Logic for Coin Subscriptions:**
```python
if subscription_type == "coins":
    if coins >= 30:
        validity = "unlimited"
        end_date = None
    else:
        validity = "1 year"
        end_date = start_date + timedelta(days=365)
    
    display_metric = "coins"
    display_value = coins
    display_label = f"{coins} Coins"
```

**Business Logic for Time-based:**
```python
if subscription_type == "time_based":
    end_date = start_date + timedelta(days=30 * duration_months)
    days_remaining = (end_date - datetime.now()).days
    
    display_metric = "time"
    display_value = days_remaining
    display_label = f"{days_remaining} days"
```

**Business Logic for Personal Training:**
```python
if subscription_type == "personal_training":
    end_date = start_date + timedelta(days=90)  # 3 months default
    
    display_metric = "training"
    display_value = sessions
    display_label = f"{sessions} Sessions"
```

---

### 4.4 Deduct Session/Coin ✅
```http
POST /api/subscriptions/{id}/deduct
Authorization: Bearer {token}
```

**Request:**
```json
{
  "deduct_type": "coin",
  "amount": 1
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "1 coin deducted successfully",
  "data": {
    "remaining_coins": 49,
    "display_value": 49,
    "display_label": "49 Coins"
  }
}
```

---

### 4.5 Freeze Subscription ✅
```http
POST /api/subscriptions/{id}/freeze
Authorization: Bearer {token}
```

**Request:**
```json
{
  "reason": "Medical leave"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Subscription frozen successfully"
}
```

---

### 4.6 Unfreeze Subscription ✅
```http
POST /api/subscriptions/{id}/unfreeze
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Subscription unfrozen successfully"
}
```

---

### 4.7 Stop Subscription ✅
```http
POST /api/subscriptions/{id}/stop
Authorization: Bearer {token}
```

**Request:**
```json
{
  "reason": "Customer request"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Subscription stopped successfully"
}
```

---

### 4.8 Transfer Subscription ✅
```http
POST /api/subscriptions/{id}/transfer
Authorization: Bearer {token}
```

**Request:**
```json
{
  "new_customer_id": 120
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Subscription transferred successfully"
}
```

---

## 5. ATTENDANCE & CHECK-IN (4 Endpoints)

### 5.1 Record Check-In 🔴 CRITICAL FIX REQUIRED
```http
POST /api/attendance
Authorization: Bearer {token}
```

**Current Problem:** Returns error "qr_code is required" even when provided.

**Request Option 1 (with QR code):**
```json
{
  "qr_code": "customer_id:115",
  "check_in_time": "2026-02-16T13:00:00Z",
  "action": "check_in_only"
}
```

**Request Option 2 (with customer_id):**
```json
{
  "customer_id": 115,
  "check_in_time": "2026-02-16T13:00:00Z",
  "action": "check_in_only"
}
```

**Request Option 3 (with both):**
```json
{
  "customer_id": 115,
  "qr_code": "customer_id:115",
  "check_in_time": "2026-02-16T13:00:00Z",
  "action": "check_in_only"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Check-in recorded successfully",
  "data": {
    "attendance_id": 2001,
    "customer_id": 115,
    "customer_name": "Adel Saad",
    "check_in_time": "2026-02-16T13:00:00Z",
    "branch_id": 2
  }
}
```

**Business Logic:**
```python
# Extract customer ID from qr_code if provided
if 'qr_code' in request_data:
    qr_code = request_data['qr_code']
    if ':' in qr_code:
        customer_id = int(qr_code.split(':')[1])
    else:
        customer_id = int(qr_code)
elif 'customer_id' in request_data:
    customer_id = request_data['customer_id']
else:
    return error("customer_id or qr_code is required")

# Verify customer exists and is active
customer = Customer.query.get(customer_id)
if not customer:
    return error("Customer not found", 404)

if not customer.is_active:
    return error("Customer account is inactive", 400)

# Get staff's branch from JWT token
staff_branch_id = current_user.branch_id

# Create attendance record
attendance = Attendance(
    customer_id=customer_id,
    branch_id=staff_branch_id,
    check_in_time=request_data.get('check_in_time', datetime.now()),
    action=request_data.get('action', 'check_in_only')
)
db.session.add(attendance)
db.session.commit()

return success(attendance)
```

---

### 5.2 Record Check-In with Deduction ✅
```http
POST /api/attendance/with-deduction
Authorization: Bearer {token}
```

**Request:**
```json
{
  "customer_id": 115,
  "subscription_id": 124,
  "check_in_time": "2026-02-16T13:00:00Z",
  "deduct_type": "coin",
  "amount": 1
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Check-in recorded and 1 coin deducted",
  "data": {
    "attendance_id": 2002,
    "remaining_coins": 49
  }
}
```

---

### 5.3 Get Attendance History ✅
```http
GET /api/attendance
Authorization: Bearer {token}
Query Parameters: ?customer_id=115&from_date=2026-02-01&to_date=2026-02-16
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 2001,
        "customer_id": 115,
        "customer_name": "Adel Saad",
        "check_in_time": "2026-02-16T13:00:00Z",
        "branch_name": "Phoenix Club"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total": 50
    }
  }
}
```

---

### 5.4 Get Today's Attendance ✅
```http
GET /api/attendance/today
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "list": [
      {
        "customer_name": "Adel Saad",
        "check_in_time": "2026-02-16T13:00:00Z"
      }
    ]
  }
}
```

---

## 6. BRANCH MANAGEMENT (5 Endpoints)

### 6.1 List Branches 🔴 FIX REQUIRED
```http
GET /api/branches
Authorization: Bearer {token}
```

**Current Problem:** Returns empty array despite having 3 branches.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Dragon Club",
        "address": "123 Main St, Cairo",
        "phone": "0201234567890",
        "email": "dragon@gym.com",
        "is_active": true
      },
      {
        "id": 2,
        "name": "Phoenix Club",
        "address": "456 Second St, Giza",
        "phone": "0209876543210",
        "email": "phoenix@gym.com",
        "is_active": true
      },
      {
        "id": 3,
        "name": "Lions Fitness",
        "address": "789 Third Ave, Alexandria",
        "phone": "0205555555555",
        "email": "lions@gym.com",
        "is_active": true
      }
    ]
  }
}
```

---

### 6.2 Get Branch Details ✅
```http
GET /api/branches/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Dragon Club",
    "address": "123 Main St, Cairo",
    "customer_count": 50,
    "staff_count": 5,
    "revenue": 50000.00
  }
}
```

---

### 6.3 Create Branch ✅
```http
POST /api/branches
Authorization: Bearer {token}
Role: owner only
```

**Request:**
```json
{
  "name": "Tigers Gym",
  "address": "999 Fourth St, Mansoura",
  "phone": "0203333333333",
  "email": "tigers@gym.com"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Branch created successfully",
  "data": {
    "id": 4
  }
}
```

---

### 6.4 Update Branch ✅
```http
PUT /api/branches/{id}
Authorization: Bearer {token}
Role: owner only
```

**Request:**
```json
{
  "name": "Dragon Club Updated",
  "address": "123 New Address, Cairo"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Branch updated successfully"
}
```

---

### 6.5 Delete Branch ✅
```http
DELETE /api/branches/{id}
Authorization: Bearer {token}
Role: owner only
```

**Response (200):**
```json
{
  "success": true,
  "message": "Branch deleted successfully"
}
```

---

## 7. STAFF MANAGEMENT (6 Endpoints)

### 7.1 List Staff 🔴 FIX REQUIRED
```http
GET /api/staff
Authorization: Bearer {token}
```

**Current Problem:** Returns empty array despite having 15 staff members.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "full_name": "Ahmed Hassan",
        "phone": "01012345678",
        "email": "ahmed@dragonclub.com",
        "role": "owner",
        "branch_id": null,
        "branch_name": "All Branches",
        "is_active": true
      },
      {
        "id": 2,
        "full_name": "Sara Ali",
        "phone": "01087654321",
        "email": "sara@dragonclub.com",
        "role": "manager",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "is_active": true
      }
    ]
  }
}
```

---

### 7.2 Get Staff Details ✅
```http
GET /api/staff/{id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "full_name": "Sara Ali",
    "role": "manager",
    "branch_name": "Dragon Club"
  }
}
```

---

### 7.3 Create Staff ✅
```http
POST /api/staff
Authorization: Bearer {token}
Role: owner only
```

**Request:**
```json
{
  "full_name": "New Manager",
  "phone": "01011111111",
  "email": "new@gym.com",
  "password": "SecurePass123",
  "role": "manager",
  "branch_id": 1
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Staff created successfully",
  "data": {
    "id": 16
  }
}
```

---

### 7.4 Update Staff ✅
```http
PUT /api/staff/{id}
Authorization: Bearer {token}
Role: owner only
```

---

### 7.5 Delete Staff ✅
```http
DELETE /api/staff/{id}
Authorization: Bearer {token}
Role: owner only
```

---

### 7.6 Change Staff Password ✅
```http
POST /api/staff/{id}/change-password
Authorization: Bearer {token}
```

---

## 8. SERVICE MANAGEMENT (4 Endpoints)

### 8.1 List Services ✅
```http
GET /api/services
Authorization: Bearer {token}
```

### 8.2 Get Service Details ✅
```http
GET /api/services/{id}
Authorization: Bearer {token}
```

### 8.3 Create Service ✅
```http
POST /api/services
Authorization: Bearer {token}
Role: owner only
```

### 8.4 Update Service ✅
```http
PUT /api/services/{id}
Authorization: Bearer {token}
Role: owner only
```

---

## 9. PAYMENT MANAGEMENT (4 Endpoints)

### 9.1 List Payments ✅
```http
GET /api/payments
Authorization: Bearer {token}
```

### 9.2 Create Payment ✅
```http
POST /api/payments
Authorization: Bearer {token}
```

### 9.3 Update Payment ✅
```http
PUT /api/payments/{id}
Authorization: Bearer {token}
```

### 9.4 Delete Payment ✅
```http
DELETE /api/payments/{id}
Authorization: Bearer {token}
```

---

## 10. REPORTS & ANALYTICS (5 Endpoints)

### 10.1 Revenue Report ✅
```http
GET /api/reports/revenue
Authorization: Bearer {token}
Query: ?from_date=2026-02-01&to_date=2026-02-16&branch_id=1
```

### 10.2 Customer Growth Report ✅
```http
GET /api/reports/customers/growth
Authorization: Bearer {token}
```

### 10.3 Attendance Report ✅
```http
GET /api/reports/attendance
Authorization: Bearer {token}
```

### 10.4 Subscription Report ✅
```http
GET /api/reports/subscriptions
Authorization: Bearer {token}
```

### 10.5 Financial Report ✅
```http
GET /api/reports/financial
Authorization: Bearer {token}
```

---

## 11. SETTINGS (3 Endpoints)

### 11.1 Get Settings ✅
```http
GET /api/settings
Authorization: Bearer {token}
```

### 11.2 Update Settings ✅
```http
PUT /api/settings
Authorization: Bearer {token}
Role: owner only
```

### 11.3 Change Password ✅
```http
POST /api/staff/change-password
Authorization: Bearer {token}
```

---

---

## 📱 CLIENT APP ENDPOINTS (12 Total)

### Base URL
```
https://yamenmod91.pythonanywhere.com/api/client
```

---

## 1. CLIENT AUTHENTICATION (3 Endpoints)

### 1.1 Client Login ✅
```http
POST /api/client/auth/login
```

**Request:**
```json
{
  "phone": "01077827638",
  "password": "RX04AF"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "customer": {
      "id": 1,
      "full_name": "Mohamed Salem",
      "phone": "01077827638",
      "email": "customer1@example.com",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "qr_code": "customer_id:1",
      "password_changed": false,
      "is_active": true
    },
    "token": "eyJ...",
    "password_changed": false
  }
}
```

**Error (401):**
```json
{
  "success": false,
  "error": "Invalid phone or password"
}
```

---

### 1.2 Change Password (First-time) ✅
```http
POST /api/client/auth/change-password
Authorization: Bearer {token}
```

**Request:**
```json
{
  "old_password": "RX04AF",
  "new_password": "MyNewPass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Business Logic:**
- Validate old password
- Hash and store new password
- Set `password_changed` = true
- Return success

---

### 1.3 Client Logout ✅
```http
POST /api/client/auth/logout
Authorization: Bearer {token}
```

---

## 2. CLIENT PROFILE (3 Endpoints)

### 2.1 Get Profile with Subscription ✅
```http
GET /api/client/me
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "full_name": "Mohamed Salem",
    "phone": "01077827638",
    "email": "customer1@example.com",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "qr_code": "customer_id:1",
    "height": 175,
    "weight": 80,
    "bmi": 26.1,
    "active_subscription": {
      "id": 1,
      "type": "coins",
      "status": "active",
      "start_date": "2026-02-16",
      "end_date": null,
      "expiry_date": null,
      "remaining_coins": 50,
      "display_metric": "coins",
      "display_value": 50,
      "display_label": "50 Coins",
      "validity": "unlimited",
      "can_access": true,
      "is_expired": false
    }
  }
}
```

---

### 2.2 Update Profile ✅
```http
PUT /api/client/me
Authorization: Bearer {token}
```

**Request:**
```json
{
  "height": 176,
  "weight": 78
}
```

---

### 2.3 Get QR Code ✅
```http
GET /api/client/qr-code
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "qr_code": "customer_id:1",
    "expires_at": "2026-02-16T14:00:00Z"
  }
}
```

---

## 3. CLIENT SUBSCRIPTION (3 Endpoints)

### 3.1 Get Active Subscription ✅
```http
GET /api/client/subscription
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "subscription_type": "coins",
    "status": "active",
    "remaining_coins": 50,
    "display_metric": "coins",
    "display_value": 50,
    "display_label": "50 Coins",
    "validity": "unlimited",
    "start_date": "2026-02-16",
    "end_date": null,
    "allowed_services": ["Gym", "Pool"],
    "freeze_history": []
  }
}
```

---

### 3.2 Get Subscription History ✅
```http
GET /api/client/subscriptions/history
Authorization: Bearer {token}
```

---

### 3.3 Request Freeze ✅
```http
POST /api/client/subscription/freeze-request
Authorization: Bearer {token}
```

---

## 4. CLIENT ATTENDANCE (2 Endpoints)

### 4.1 Get Entry History ✅
```http
GET /api/client/attendance
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "check_in_time": "2026-02-16T14:30:00Z",
        "branch_name": "Dragon Club"
      }
    ]
  }
}
```

---

### 4.2 Get Attendance Statistics ✅
```http
GET /api/client/attendance/stats
Authorization: Bearer {token}
```

---

## 5. CLIENT COMPLAINTS (1 Endpoint)

### 5.1 Submit Complaint ✅
```http
POST /api/client/complaints
Authorization: Bearer {token}
```

**Request:**
```json
{
  "subject": "Equipment issue",
  "description": "Treadmill #5 is not working",
  "priority": "medium"
}
```

---

---

## 🌱 SEED DATA REQUIREMENTS

### Create seed.py with:

#### 1. Branches (3)
```python
branches = [
    {
        "name": "Dragon Club",
        "address": "123 Main St, Cairo",
        "phone": "0201234567890",
        "email": "dragon@gym.com"
    },
    {
        "name": "Phoenix Club",
        "address": "456 Second St, Giza",
        "phone": "0209876543210",
        "email": "phoenix@gym.com"
    },
    {
        "name": "Lions Fitness",
        "address": "789 Third Ave, Alexandria",
        "phone": "0205555555555",
        "email": "lions@gym.com"
    }
]
```

---

#### 2. Services (10)
```python
services = [
    {"name": "Monthly Gym", "type": "gym", "price": 1200.00},
    {"name": "3-Month Gym", "type": "gym", "price": 3200.00},
    {"name": "20 Coins", "type": "coins", "coins": 20, "price": 800.00},
    {"name": "30 Coins", "type": "coins", "coins": 30, "price": 1100.00},
    {"name": "50 Coins", "type": "coins", "coins": 50, "price": 1800.00},
    {"name": "10 PT Sessions", "type": "training", "sessions": 10, "price": 2000.00},
    # ... more services
]
```

---

#### 3. Staff (15)
```python
staff = [
    # 1 Owner (no branch)
    {
        "full_name": "Ahmed Hassan",
        "phone": "01012345678",
        "email": "ahmed@gym.com",
        "password": "owner123",
        "role": "owner",
        "branch_id": None
    },
    # 3 Managers (one per branch)
    {
        "full_name": "Sara Ali",
        "phone": "01087654321",
        "email": "sara@dragonclub.com",
        "password": "manager123",
        "role": "manager",
        "branch_id": 1
    },
    # ... more staff
]
```

---

#### 4. Customers (150)
```python
# Distribution:
# - Branch 1 (Dragon Club): 50 customers
# - Branch 2 (Phoenix Club): 50 customers
# - Branch 3 (Lions Fitness): 50 customers

# Each customer must have:
customers = [
    {
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "email": "customer1@example.com",
        "branch_id": 1,
        "national_id": "29012345678901",
        "date_of_birth": "1990-05-15",
        "gender": "male",
        "height": 175,
        "weight": 80,
        "qr_code": "customer_id:1",
        "temp_password": "RX04AF",  # 6 chars: 2 letters, 2 numbers, 2 letters
        "password_changed": False,
        "is_active": True
    },
    # ... 149 more
]

# Temp password format: AB12CD
# Examples: RX04AF, SI19IC, PS02HC, PE71JZ, RK94GG
```

---

#### 5. Subscriptions (150)
```python
# Distribution:
# - 120 active subscriptions
# - 30 expired subscriptions

# Subscription types distribution:
# - 50 coins subscriptions (30 with >= 30 coins, 20 with < 30 coins)
# - 60 time-based subscriptions
# - 40 personal training subscriptions

# Example coins >= 30 (unlimited validity):
{
    "customer_id": 1,
    "service_id": 5,  # 50 Coins service
    "branch_id": 1,
    "type": "coins",
    "status": "active",
    "remaining_coins": 50,
    "display_metric": "coins",
    "display_value": 50,
    "display_label": "50 Coins",
    "validity": "unlimited",
    "start_date": "2026-02-16",
    "end_date": None,
    "amount": 1800.00,
    "payment_method": "cash"
}

# Example coins < 30 (1 year validity):
{
    "customer_id": 2,
    "service_id": 3,  # 20 Coins service
    "branch_id": 1,
    "type": "coins",
    "status": "active",
    "remaining_coins": 20,
    "display_metric": "coins",
    "display_value": 20,
    "display_label": "20 Coins",
    "validity": "1 year",
    "start_date": "2026-02-16",
    "end_date": "2027-02-16",
    "amount": 800.00,
    "payment_method": "card"
}

# Example time-based:
{
    "customer_id": 3,
    "service_id": 1,  # Monthly Gym service
    "branch_id": 1,
    "type": "time_based",
    "status": "active",
    "display_metric": "time",
    "display_value": 28,  # days remaining
    "display_label": "28 days",
    "start_date": "2026-02-16",
    "end_date": "2026-03-16",
    "amount": 1200.00,
    "payment_method": "cash"
}

# Example personal training:
{
    "customer_id": 4,
    "service_id": 6,  # 10 PT Sessions service
    "branch_id": 1,
    "type": "personal_training",
    "status": "active",
    "remaining_sessions": 10,
    "display_metric": "training",
    "display_value": 10,
    "display_label": "10 Sessions",
    "start_date": "2026-02-16",
    "end_date": "2026-05-16",  # 3 months
    "amount": 2000.00,
    "payment_method": "bank_transfer"
}
```

---

#### 6. Attendance (2000 records)
```python
# Create 2000 attendance records for the last 30 days
# Distributed across all active customers
# Average 13 check-ins per customer (2000 / 150)

for customer in active_customers:
    num_visits = random.randint(5, 25)
    for _ in range(num_visits):
        date = random_date_last_30_days()
        attendance = {
            "customer_id": customer.id,
            "branch_id": customer.branch_id,
            "check_in_time": date,
            "action": "check_in_only"
        }
```

---

#### 7. Payments (150)
```python
# One payment for each subscription
for subscription in subscriptions:
    payment = {
        "customer_id": subscription.customer_id,
        "subscription_id": subscription.id,
        "amount": subscription.amount,
        "payment_method": subscription.payment_method,
        "payment_status": "paid",
        "payment_date": subscription.start_date,
        "branch_id": subscription.branch_id
    }
```

---

---

## ✅ IMPLEMENTATION CHECKLIST

### Critical Fixes (Must be done first)
- [ ] Fix `POST /api/attendance` to accept `qr_code` OR `customer_id`
- [ ] Fix subscription activation branch validation error
- [ ] Fix dashboard endpoints returning zeros
- [ ] Fix branches list returning empty array
- [ ] Fix staff list returning empty array
- [ ] Fix customers list to include `temp_password` field
- [ ] Implement coin subscription validity logic (unlimited for >= 30 coins)
- [ ] Add `display_metric`, `display_value`, `display_label` fields to all subscription responses

### Complete All Endpoints
- [ ] Implement all 55 staff app endpoints
- [ ] Implement all 12 client app endpoints
- [ ] Test all endpoints with Postman/Thunder Client

### Seed Data
- [ ] Create seed.py with 150 customers
- [ ] Create 150 subscriptions (50 coins, 60 time-based, 40 training)
- [ ] Create 2000 attendance records
- [ ] Verify all temp_password fields are populated

### Testing
- [ ] Test staff login with all roles
- [ ] Test client login with temp password
- [ ] Test QR code check-in flow
- [ ] Test subscription activation for all types
- [ ] Test dashboard data displays correctly
- [ ] Test branches and staff lists populate

---

## 🔑 TEST CREDENTIALS

### Staff Accounts
```
Owner:
Phone: 01012345678
Password: owner123

Manager (Dragon Club):
Phone: 01087654321
Password: manager123

Receptionist (Dragon Club):
Phone: 01045678901
Password: receptionist123
```

### Customer Accounts
```
Customer 1:
Phone: 01077827638
Temp Password: RX04AF
Name: Mohamed Salem

Customer 2:
Phone: 01025867870
Temp Password: AB12CD
Name: Adel Saad
```

---

## 📞 SUPPORT

**Backend URL:** https://yamenmod91.pythonanywhere.com/api  
**Date:** February 16, 2026  
**Status:** Ready for Implementation

---

**END OF DOCUMENT**

