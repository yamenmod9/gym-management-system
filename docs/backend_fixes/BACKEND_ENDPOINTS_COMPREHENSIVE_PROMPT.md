# 🎯 COMPREHENSIVE BACKEND API ENDPOINTS GUIDE FOR GYM MANAGEMENT SYSTEM

**Date:** February 14, 2026  
**For:** Claude Sonnet 4.5  
**Purpose:** Complete list of ALL endpoints needed for Staff App and Client App

---

## 📱 TABLE OF CONTENTS

1. [Staff App Endpoints](#staff-app-endpoints) (38 endpoints)
2. [Client App Endpoints](#client-app-endpoints) (8 endpoints)
3. [HTTP Methods & Status Codes](#http-methods--status-codes)
4. [Authentication & Authorization](#authentication--authorization)
5. [Error Handling Standards](#error-handling-standards)

---

## 🏢 STAFF APP ENDPOINTS

**Base URL:** `https://yamenmod91.pythonanywhere.com/api`

### 1. AUTHENTICATION (3 endpoints)

#### 1.1 Staff Login
```http
POST /api/auth/login
```
**Request Body:**
```json
{
  "username": "owner",
  "password": "owner123"
}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "owner",
      "role": "owner",  // owner | branch_manager | front_desk | central_accountant | branch_accountant
      "branch_id": null  // null for owner/central_accountant, number for others
    }
  }
}
```

#### 1.2 Get Staff Profile
```http
GET /api/auth/profile
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "owner",
    "role": "owner",
    "branch_id": null,
    "full_name": "System Owner",
    "email": "owner@gym.com",
    "phone": "01234567890"
  }
}
```

#### 1.3 Staff Logout
```http
POST /api/auth/logout
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

### 2. CUSTOMERS (6 endpoints)

#### 2.1 Get All Customers (with filtering)
```http
GET /api/customers?branch_id={id}&is_active={bool}&page={num}&limit={num}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 151,
        "full_name": "Ahmed Hassan",
        "phone": "01234567890",
        "email": "ahmed@example.com",
        "qr_code": "GYM-151",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "weight": 75.0,
        "height": 1.80,
        "bmi": 23.15,
        "date_of_birth": "1994-02-18",
        "gender": "male",
        "is_active": true,
        "created_at": "2026-02-10T22:47:28.297720",
        "active_subscription": {
          "id": 45,
          "service_name": "Monthly Gym",
          "start_date": "2026-01-15",
          "end_date": "2026-02-15",
          "status": "active",
          "remaining_days": 1,
          "remaining_coins": 10
        }
      }
    ],
    "total": 150,
    "page": 1,
    "limit": 20
  }
}
```

#### 2.2 Get Customer by ID
```http
GET /api/customers/{id}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "GYM-151",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "weight": 75.0,
    "height": 1.80,
    "bmi": 23.15,
    "ideal_weight": 72.0,
    "daily_calories": 2200,
    "date_of_birth": "1994-02-18",
    "gender": "male",
    "address": "123 Main St, Cairo",
    "national_id": "29402180101234",
    "health_notes": "None",
    "is_active": true,
    "created_at": "2026-02-10T22:47:28.297720",
    "updated_at": "2026-02-10T22:47:28.331552"
  }
}
```

#### 2.3 Register New Customer
```http
POST /api/customers/register
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "full_name": "Ahmed Hassan",
  "phone": "01234567890",
  "email": "ahmed@example.com",
  "branch_id": 1,
  "weight": 75.0,
  "height": 1.80,
  "date_of_birth": "1994-02-18",
  "gender": "male",
  "address": "123 Main St, Cairo",
  "national_id": "29402180101234",
  "health_notes": "None"
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "id": 151,
    "qr_code": "GYM-151",
    "bmi": 23.15,
    "bmi_category": "Normal",
    "ideal_weight": 72.0,
    "daily_calories": 2200
  }
}
```

#### 2.4 Update Customer
```http
PUT /api/customers/{id}
Authorization: Bearer {token}
```
**Request Body:** (same as register, all fields optional)

#### 2.5 Delete Customer
```http
DELETE /api/customers/{id}
Authorization: Bearer {token}
```

#### 2.6 Search Customers
```http
GET /api/customers/search?q={query}&branch_id={id}
Authorization: Bearer {token}
```
**Search by:** name, phone, email, national_id, qr_code

---

### 3. SUBSCRIPTIONS (6 endpoints)

#### 3.1 Get All Subscriptions (with filtering)
```http
GET /api/subscriptions?customer_id={id}&branch_id={id}&status={active|frozen|expired}&page={num}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 45,
        "customer_id": 151,
        "customer_name": "Ahmed Hassan",
        "service_id": 1,
        "service_name": "Monthly Gym",
        "service_type": "gym",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "start_date": "2026-01-15",
        "end_date": "2026-02-15",
        "original_end_date": "2026-02-15",
        "status": "active",
        "remaining_days": 1,
        "remaining_coins": 10,
        "total_coins": 30,
        "freeze_days_used": 0,
        "freeze_days_allowed": 5,
        "amount": 500.0,
        "discount": 0.0,
        "notes": null,
        "created_at": "2026-01-15T10:00:00",
        "created_by": "reception_dragon_1"
      }
    ],
    "total": 83,
    "page": 1,
    "limit": 20
  }
}
```

#### 3.2 Get Subscription by ID
```http
GET /api/subscriptions/{id}
Authorization: Bearer {token}
```

#### 3.3 Activate New Subscription
```http
POST /api/subscriptions/activate
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "customer_id": 151,
  "service_id": 1,
  "start_date": "2026-02-15",
  "payment_method": "cash",
  "amount": 500.0,
  "discount": 0.0,
  "notes": "First subscription"
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 45,
    "end_date": "2026-03-15",
    "remaining_days": 30,
    "remaining_coins": 30
  }
}
```

#### 3.4 Renew Subscription
```http
POST /api/subscriptions/renew
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "subscription_id": 45,
  "payment_method": "cash",
  "amount": 500.0,
  "discount": 0.0
}
```

#### 3.5 Freeze Subscription
```http
POST /api/subscriptions/freeze
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "subscription_id": 45,
  "freeze_days": 3,
  "reason": "Travel"
}
```

#### 3.6 Stop Subscription
```http
POST /api/subscriptions/stop
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "subscription_id": 45,
  "reason": "Customer request"
}
```

---

### 4. QR CODE SCANNING & CHECK-IN (2 endpoints)

#### 4.1 Scan QR Code (Process Entry)
```http
POST /api/qr/scan
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "qr_code": "GYM-151",
  "branch_id": 1,
  "action": "check_in"  // check_in | deduct_coins
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Check-in successful",
  "data": {
    "customer_id": 151,
    "customer_name": "Ahmed Hassan",
    "subscription_status": "active",
    "remaining_days": 1,
    "remaining_coins": 9,
    "entry_id": 1234,
    "entry_time": "2026-02-14T10:30:00Z"
  }
}
```

#### 4.2 Deduct Coins from Subscription
```http
POST /api/qr/deduct-coins
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "qr_code": "GYM-151",
  "coins_to_deduct": 2,
  "service_name": "Personal Training Session",
  "notes": "1 hour PT"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "2 coins deducted successfully",
  "data": {
    "customer_name": "Ahmed Hassan",
    "coins_before": 10,
    "coins_after": 8,
    "subscription_status": "active"
  }
}
```

---

### 5. PAYMENTS (4 endpoints)

#### 5.1 Get All Payments
```http
GET /api/payments?branch_id={id}&payment_method={cash|card|online}&date_from={date}&date_to={date}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 789,
        "subscription_id": 45,
        "customer_name": "Ahmed Hassan",
        "service_name": "Monthly Gym",
        "amount": 500.0,
        "discount": 0.0,
        "payment_method": "cash",
        "payment_date": "2026-02-14T10:00:00",
        "receipt_number": "RCP-20260214-001",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "processed_by": "reception_dragon_1",
        "notes": null
      }
    ],
    "total": 245,
    "total_amount": 122500.0
  }
}
```

#### 5.2 Record Payment
```http
POST /api/payments/record
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "subscription_id": 45,
  "amount": 500.0,
  "discount": 0.0,
  "payment_method": "cash",
  "notes": "Full payment"
}
```

#### 5.3 Daily Closing
```http
POST /api/payments/daily-closing
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "branch_id": 1,
  "date": "2026-02-14",
  "expected_cash": 15000.0,
  "actual_cash": 14950.0,
  "cash_difference": -50.0,
  "notes": "50 EGP missing - customer change"
}
```

#### 5.4 Get Payment by ID
```http
GET /api/payments/{id}
Authorization: Bearer {token}
```

---

### 6. SERVICES (2 endpoints)

#### 6.1 Get All Services
```http
GET /api/services
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Monthly Gym",
      "description": "Full gym access for 1 month",
      "price": 500.0,
      "duration_days": 30,
      "service_type": "gym",
      "total_coins": 30,
      "freeze_days_allowed": 5,
      "is_active": true
    },
    {
      "id": 2,
      "name": "3-Month Gym",
      "description": "Full gym access for 3 months",
      "price": 1350.0,
      "duration_days": 90,
      "service_type": "gym",
      "total_coins": 90,
      "freeze_days_allowed": 15,
      "is_active": true
    }
  ]
}
```

#### 6.2 Get Service by ID
```http
GET /api/services/{id}
Authorization: Bearer {token}
```

---

### 7. BRANCHES (3 endpoints)

#### 7.1 Get All Branches
```http
GET /api/branches
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Dragon Club",
      "location": "Nasr City, Cairo",
      "phone": "01012345678",
      "email": "dragon@gym.com",
      "is_active": true,
      "total_customers": 60,
      "active_subscriptions": 40,
      "monthly_revenue": 65000.0,
      "staff_count": 3
    },
    {
      "id": 2,
      "name": "Phoenix Fitness",
      "location": "Maadi, Cairo",
      "phone": "01023456789",
      "email": "phoenix@gym.com",
      "is_active": true,
      "total_customers": 55,
      "active_subscriptions": 35,
      "monthly_revenue": 58000.0,
      "staff_count": 3
    }
  ]
}
```

#### 7.2 Get Branch by ID
```http
GET /api/branches/{id}
Authorization: Bearer {token}
```

#### 7.3 Get Branch Performance
```http
GET /api/branches/{id}/performance?month={YYYY-MM}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "month": "2026-02",
    "total_customers": 60,
    "new_customers": 8,
    "active_subscriptions": 40,
    "expired_subscriptions": 5,
    "frozen_subscriptions": 2,
    "total_revenue": 65000.0,
    "revenue_by_service": {
      "Monthly Gym": 30000.0,
      "3-Month Gym": 25000.0,
      "Personal Training": 10000.0
    },
    "average_subscription_value": 1625.0,
    "check_ins_count": 1250,
    "complaints_count": 12,
    "open_complaints": 1,
    "staff_performance": [
      {
        "staff_id": 2,
        "staff_name": "reception_dragon_1",
        "transactions_count": 45,
        "total_revenue": 35000.0
      }
    ]
  }
}
```

---

### 8. USERS/STAFF (3 endpoints)

#### 8.1 Get All Users (Staff)
```http
GET /api/users?branch_id={id}&role={role}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 2,
      "username": "manager_dragon",
      "role": "branch_manager",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "full_name": "Dragon Manager",
      "email": "manager.dragon@gym.com",
      "phone": "01012345678",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00"
    }
  ]
}
```

#### 8.2 Get User by ID
```http
GET /api/users/{id}
Authorization: Bearer {token}
```

#### 8.3 Get Users by Branch
```http
GET /api/users/branch/{branch_id}
Authorization: Bearer {token}
```

---

### 9. REPORTS (6 endpoints)

#### 9.1 Revenue Report
```http
GET /api/reports/revenue?branch_id={id}&date_from={date}&date_to={date}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 164521.0,
    "revenue_by_branch": [
      {"branch_id": 1, "branch_name": "Dragon Club", "revenue": 65000.0},
      {"branch_id": 2, "branch_name": "Phoenix Fitness", "revenue": 58000.0},
      {"branch_id": 3, "branch_name": "Tiger Gym", "revenue": 41521.0}
    ],
    "revenue_by_service": [
      {"service_name": "Monthly Gym", "revenue": 90000.0},
      {"service_name": "3-Month Gym", "revenue": 54000.0},
      {"service_name": "Personal Training", "revenue": 20521.0}
    ],
    "revenue_by_payment_method": {
      "cash": 120000.0,
      "card": 35521.0,
      "online": 9000.0
    }
  }
}
```

#### 9.2 Daily Sales Report
```http
GET /api/reports/daily?date={YYYY-MM-DD}&branch_id={id}
Authorization: Bearer {token}
```

#### 9.3 Weekly Sales Report
```http
GET /api/reports/weekly?week_start={date}&branch_id={id}
Authorization: Bearer {token}
```

#### 9.4 Monthly Sales Report
```http
GET /api/reports/monthly?month={YYYY-MM}&branch_id={id}
Authorization: Bearer {token}
```

#### 9.5 Branch Comparison Report
```http
GET /api/reports/branch-comparison?month={YYYY-MM}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "customers": 60,
      "active_subscriptions": 40,
      "revenue": 65000.0,
      "complaints": 12,
      "open_complaints": 1,
      "performance_score": 92
    }
  ]
}
```

#### 9.6 Employee Performance Report
```http
GET /api/reports/employee-performance?branch_id={id}&month={YYYY-MM}
Authorization: Bearer {token}
```

---

### 10. COMPLAINTS (3 endpoints)

#### 10.1 Get All Complaints
```http
GET /api/complaints?branch_id={id}&status={open|resolved}&priority={low|medium|high}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "customer_id": 151,
      "customer_name": "Ahmed Hassan",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "category": "equipment",
      "priority": "high",
      "status": "open",
      "description": "Treadmill not working",
      "submitted_at": "2026-02-14T09:00:00",
      "resolved_at": null,
      "resolution_notes": null,
      "submitted_by": "reception_dragon_1"
    }
  ],
  "total": 50,
  "open_count": 11,
  "resolved_count": 39
}
```

#### 10.2 Submit Complaint
```http
POST /api/complaints/submit
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "customer_id": 151,
  "branch_id": 1,
  "category": "equipment",
  "priority": "high",
  "description": "Treadmill not working"
}
```

#### 10.3 Update Complaint Status
```http
PUT /api/complaints/{id}
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "status": "resolved",
  "resolution_notes": "Equipment repaired"
}
```

---

### 11. ALERTS (2 endpoints)

#### 11.1 Get Alerts
```http
GET /api/alerts?branch_id={id}&alert_type={expiring|low_coins|complaints}&is_read={bool}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "alert_type": "expiring_subscription",
      "priority": "high",
      "customer_id": 151,
      "customer_name": "Ahmed Hassan",
      "branch_id": 1,
      "message": "Subscription expires in 1 day",
      "is_read": false,
      "created_at": "2026-02-14T08:00:00"
    },
    {
      "id": 2,
      "alert_type": "low_coins",
      "priority": "medium",
      "customer_id": 152,
      "customer_name": "Sara Ali",
      "branch_id": 1,
      "message": "Only 2 coins remaining",
      "is_read": false,
      "created_at": "2026-02-14T09:00:00"
    }
  ],
  "unread_count": 15
}
```

#### 11.2 Get Smart Alerts (Owner Dashboard)
```http
GET /api/alerts/smart
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "expiring_today": 2,
    "expiring_week": 11,
    "low_coins": 8,
    "open_complaints": 11,
    "pending_expenses": 10,
    "urgent_expenses": 3
  }
}
```

---

### 12. FINANCE (3 endpoints)

#### 12.1 Get Expenses
```http
GET /api/finance/expenses?branch_id={id}&status={pending|approved|rejected}&date_from={date}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "category": "maintenance",
      "amount": 5000.0,
      "description": "AC repair",
      "status": "pending",
      "priority": "urgent",
      "requested_date": "2026-02-14T10:00:00",
      "requested_by": "manager_dragon",
      "approved_date": null,
      "approved_by": null
    }
  ],
  "total_pending": 35000.0,
  "total_approved": 125000.0
}
```

#### 12.2 Get Cash Differences
```http
GET /api/finance/cash-differences?branch_id={id}&date_from={date}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "branch_id": 1,
      "date": "2026-02-14",
      "expected_cash": 15000.0,
      "actual_cash": 14950.0,
      "difference": -50.0,
      "notes": "Customer change shortage",
      "recorded_by": "reception_dragon_1"
    }
  ],
  "total_difference": -150.0
}
```

#### 12.3 Get Daily Sales Summary
```http
GET /api/finance/daily-sales?date={YYYY-MM-DD}&branch_id={id}
Authorization: Bearer {token}
```

---

### 13. ATTENDANCE (2 endpoints)

#### 13.1 Get Attendance Records
```http
GET /api/attendance?branch_id={id}&user_id={id}&date={YYYY-MM-DD}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": 2,
      "user_name": "reception_dragon_1",
      "branch_id": 1,
      "date": "2026-02-14",
      "check_in": "09:00:00",
      "check_out": "17:00:00",
      "status": "present",
      "hours_worked": 8.0
    }
  ]
}
```

#### 13.2 Get Attendance by Branch
```http
GET /api/attendance/by-branch/{branch_id}?month={YYYY-MM}
Authorization: Bearer {token}
```

---

## 📱 CLIENT APP ENDPOINTS

**Base URL:** `https://yamenmod91.pythonanywhere.com/api/client`

### 1. AUTHENTICATION (4 endpoints)

#### 1.1 Request Activation Code
```http
POST /api/client/request-activation
```
**Request Body:**
```json
{
  "identifier": "01234567890"  // phone or email
}
```
**Response (200):**
```json
{
  "status": "success",
  "message": "Activation code sent to your phone",
  "data": {
    "expires_in": 600  // 10 minutes
  }
}
```

#### 1.2 Verify Activation Code & Login
```http
POST /api/client/verify-activation
```
**Request Body:**
```json
{
  "identifier": "01234567890",
  "activation_code": "123456"
}
```
**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

#### 1.3 Refresh Access Token
```http
POST /api/client/refresh
```
**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

#### 1.4 Logout
```http
POST /api/client/logout
Authorization: Bearer {token}
```

---

### 2. PROFILE (1 endpoint)

#### 2.1 Get Client Profile
```http
GET /api/client/me
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "GYM-151",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "branch_location": "Nasr City, Cairo",
    "weight": 75.0,
    "height": 1.80,
    "bmi": 23.15,
    "bmi_category": "Normal",
    "ideal_weight": 72.0,
    "daily_calories": 2200,
    "date_of_birth": "1994-02-18",
    "gender": "male",
    "active_subscription": {
      "id": 45,
      "service_name": "Monthly Gym",
      "service_type": "gym",
      "start_date": "2026-01-15",
      "end_date": "2026-02-15",
      "status": "active",
      "remaining_days": 1,
      "remaining_coins": 10,
      "total_coins": 30,
      "freeze_days_remaining": 5
    }
  }
}
```

---

### 3. SUBSCRIPTION (1 endpoint)

#### 3.1 Get Subscription Details
```http
GET /api/client/subscription
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "current_subscription": {
      "id": 45,
      "service_name": "Monthly Gym",
      "service_type": "gym",
      "start_date": "2026-01-15",
      "end_date": "2026-02-15",
      "status": "active",
      "remaining_days": 1,
      "remaining_coins": 10,
      "total_coins": 30,
      "freeze_days_remaining": 5,
      "can_freeze": true,
      "amount_paid": 500.0
    },
    "subscription_history": [
      {
        "id": 44,
        "service_name": "Monthly Gym",
        "start_date": "2025-12-15",
        "end_date": "2026-01-15",
        "status": "expired",
        "amount_paid": 500.0
      }
    ]
  }
}
```

---

### 4. ENTRY HISTORY (1 endpoint)

#### 4.1 Get Entry History (Check-ins)
```http
GET /api/client/entry-history?limit={num}&offset={num}
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "status": "success",
  "data": {
    "entries": [
      {
        "id": 1234,
        "entry_time": "2026-02-14T09:30:00Z",
        "branch_name": "Dragon Club",
        "entry_type": "qr_scan",
        "coins_used": 1
      },
      {
        "id": 1233,
        "entry_time": "2026-02-13T18:15:00Z",
        "branch_name": "Dragon Club",
        "entry_type": "qr_scan",
        "coins_used": 1
      }
    ],
    "total": 125,
    "limit": 50,
    "offset": 0
  }
}
```

---

### 5. QR CODE (1 endpoint)

#### 5.1 Refresh QR Code
```http
POST /api/client/refresh-qr
Authorization: Bearer {token}
```
**Response (200):**
```json
{
  "status": "success",
  "message": "QR code refreshed successfully",
  "data": {
    "qr_code": "GYM-151",
    "qr_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2026-02-15T12:00:00Z"
  }
}
```

---

## 🔐 HTTP METHODS & STATUS CODES

### HTTP Methods Usage

| Method | Usage |
|--------|-------|
| GET | Retrieve data (read-only) |
| POST | Create new resources, trigger actions |
| PUT | Update existing resources (full update) |
| PATCH | Partial update of resources |
| DELETE | Remove resources |

### Standard Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE (no response body) |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Valid token but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., phone exists) |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Backend error |

---

## 🔒 AUTHENTICATION & AUTHORIZATION

### Staff App Authentication

**Header Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Role-Based Access:**

| Role | Branch Access | Permissions |
|------|---------------|-------------|
| **owner** | All branches | Full access to all features |
| **branch_manager** | Own branch only | All features for their branch |
| **front_desk** (reception) | Own branch only | Customers, subscriptions, payments, complaints |
| **central_accountant** | All branches | Read-only financial reports |
| **branch_accountant** | Own branch only | Read-only financial reports |

**Token Expiry:**
- Access Token: 1 hour
- Refresh Token: 7 days

### Client App Authentication

**Header Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Access Control:**
- Clients can only access their own data
- No cross-customer data access
- Branch filtering automatic by customer's branch

**Activation Code:**
- 6-digit numeric code
- Valid for 10 minutes
- One-time use only
- Sent via SMS or Email

---

## ⚠️ ERROR HANDLING STANDARDS

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Incorrect username or password",
    "details": {
      "field": "password",
      "reason": "Password does not match"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| INVALID_CREDENTIALS | 401 | Wrong username/password |
| TOKEN_EXPIRED | 401 | JWT token expired |
| INVALID_TOKEN | 401 | Malformed or invalid JWT |
| FORBIDDEN | 403 | No permission for resource |
| NOT_FOUND | 404 | Resource doesn't exist |
| DUPLICATE_ENTRY | 409 | Phone/email already exists |
| VALIDATION_ERROR | 422 | Invalid input data |
| INSUFFICIENT_COINS | 403 | Not enough coins in subscription |
| SUBSCRIPTION_EXPIRED | 403 | Customer subscription expired |
| BRANCH_MISMATCH | 403 | Resource not in user's branch |
| SERVER_ERROR | 500 | Internal server error |

### Validation Errors

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "phone": ["Phone number already exists"],
      "email": ["Invalid email format"],
      "weight": ["Weight must be between 30 and 300"]
    }
  }
}
```

---

## 📊 ENDPOINT SUMMARY

### Staff App
- Authentication: 3 endpoints
- Customers: 6 endpoints
- Subscriptions: 6 endpoints
- QR Scanner: 2 endpoints
- Payments: 4 endpoints
- Services: 2 endpoints
- Branches: 3 endpoints
- Users/Staff: 3 endpoints
- Reports: 6 endpoints
- Complaints: 3 endpoints
- Alerts: 2 endpoints
- Finance: 3 endpoints
- Attendance: 2 endpoints

**Total Staff App: 45 endpoints**

### Client App
- Authentication: 4 endpoints
- Profile: 1 endpoint
- Subscription: 1 endpoint
- Entry History: 1 endpoint
- QR Code: 1 endpoint

**Total Client App: 8 endpoints**

**GRAND TOTAL: 53 endpoints**

---

## ✅ IMPLEMENTATION CHECKLIST

### Priority 1 (Critical - Must Have)
- [ ] Staff Login `/api/auth/login`
- [ ] Get Customers `/api/customers`
- [ ] Register Customer `/api/customers/register`
- [ ] Activate Subscription `/api/subscriptions/activate`
- [ ] Get Services `/api/services`
- [ ] Scan QR Code `/api/qr/scan`
- [ ] Record Payment `/api/payments/record`
- [ ] Client Request Activation `/api/client/request-activation`
- [ ] Client Verify Activation `/api/client/verify-activation`
- [ ] Client Get Profile `/api/client/me`

### Priority 2 (Important)
- [ ] Get All Subscriptions `/api/subscriptions`
- [ ] Renew Subscription `/api/subscriptions/renew`
- [ ] Freeze Subscription `/api/subscriptions/freeze`
- [ ] Get Branches `/api/branches`
- [ ] Get Payments `/api/payments`
- [ ] Daily Closing `/api/payments/daily-closing`
- [ ] Submit Complaint `/api/complaints/submit`
- [ ] Client Get Subscription `/api/client/subscription`
- [ ] Client Entry History `/api/client/entry-history`

### Priority 3 (Nice to Have)
- [ ] All Reports endpoints
- [ ] Finance endpoints
- [ ] Attendance endpoints
- [ ] Branch Performance
- [ ] Smart Alerts

---

**END OF STAFF & CLIENT APP ENDPOINTS GUIDE**

**Date:** February 14, 2026  
**Version:** 1.0  
**Status:** Complete ✅

