# 🎯 COMPLETE BACKEND API REQUIREMENTS FOR GYM MANAGEMENT SYSTEM

## 📋 Executive Summary

This document provides **complete, production-ready specifications** for all backend API endpoints required by the Flutter gym management application. The app has two interfaces:

1. **Staff App** (Reception, Manager, Accountant, Owner roles)
2. **Client App** (Gym members/customers)

**Current Status:**
- ✅ Login endpoint works
- ❌ Subscription activation fails (CRITICAL)
- ❓ All other endpoints status unknown

**Base URL:** `https://yamenmod91.pythonanywhere.com/api`

---

## 🚨 CRITICAL - Fix First (Blocking Users)

### 1. POST /api/subscriptions/activate

**Purpose:** Activate a new gym membership subscription for a customer

**Request:**
```json
POST /api/subscriptions/activate
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 123,
  "service_id": 1,
  "branch_id": 1,
  "amount": 500.00,
  "payment_method": "cash",
  "notes": "First time member" // optional
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 456,
    "customer_id": 123,
    "service_id": 1,
    "service_name": "Monthly Gym",
    "branch_id": 1,
    "start_date": "2026-02-11",
    "end_date": "2026-03-11",
    "status": "active",
    "amount": 500.0,
    "payment_method": "cash",
    "receipt_number": "RCP-20260211-001",
    "created_at": "2026-02-11T10:30:00Z"
  }
}
```

**Error Responses:**

```json
// 400 - Customer not found
{
  "success": false,
  "message": "Customer not found",
  "error_code": "CUSTOMER_NOT_FOUND"
}

// 400 - Service not found
{
  "success": false,
  "message": "Service not found",
  "error_code": "SERVICE_NOT_FOUND"
}

// 409 - Active subscription exists
{
  "success": false,
  "message": "Customer already has an active subscription",
  "error_code": "ACTIVE_SUBSCRIPTION_EXISTS",
  "data": {
    "existing_subscription_id": 123,
    "end_date": "2026-03-15"
  }
}

// 401 - Unauthorized
{
  "success": false,
  "message": "Invalid or expired token",
  "error_code": "UNAUTHORIZED"
}
```

**Backend Implementation Logic:**

1. **Validate Token:**
   - Extract user from JWT token
   - Verify token is valid and not expired
   - Check user has permission (reception, manager, owner roles)

2. **Validate Input:**
   - All required fields present
   - customer_id exists in database
   - service_id exists in database
   - branch_id exists and user has access to it
   - amount is positive number
   - payment_method is one of: "cash", "card", "transfer"

3. **Check Active Subscription:**
   - Query: `SELECT * FROM subscriptions WHERE customer_id = ? AND status = 'active'`
   - If found, return 409 error

4. **Calculate Dates:**
   - start_date = today (or specified date)
   - Get service duration from services table (e.g., 30 days for monthly)
   - end_date = start_date + service.duration_days

5. **Create Subscription Record:**
   ```sql
   INSERT INTO subscriptions (
     customer_id, service_id, branch_id, 
     start_date, end_date, status, 
     amount, payment_method, created_at
   ) VALUES (?, ?, ?, ?, ?, 'active', ?, ?, NOW())
   ```

6. **Create Payment Record:**
   ```sql
   INSERT INTO payments (
     customer_id, subscription_id, amount,
     payment_method, branch_id, payment_date,
     receipt_number, created_at
   ) VALUES (?, ?, ?, ?, ?, NOW(), ?, NOW())
   ```
   Generate receipt_number: `RCP-YYYYMMDD-XXX` (XXX = sequence number for the day)

7. **Return Success Response** with all subscription details

**Test Command:**
```bash
# 1. Login first
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"reception1","password":"reception123"}'

# 2. Copy the access_token from response

# 3. Test subscription activation
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "customer_id": 1,
    "service_id": 1,
    "branch_id": 1,
    "amount": 500.00,
    "payment_method": "cash"
  }'
```

---

## 🔐 Authentication Endpoints

### 2. POST /api/auth/login

**Status:** ✅ **WORKING** (Already implemented)

**Request:**
```json
POST /api/auth/login
Content-Type: application/json

{
  "username": "reception1",
  "password": "reception123"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "reception1",
      "full_name": "Ahmed Mohamed",
      "role": "reception",
      "branch_id": 1,
      "branch_name": "Dragon Club"
    }
  }
}
```

---

### 3. POST /api/auth/logout

**Request:**
```json
POST /api/auth/logout
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Implementation:** Optionally blacklist the token or simply return success (JWT is stateless)

---

### 4. GET /api/auth/profile

**Purpose:** Get current logged-in user profile

**Request:**
```json
GET /api/auth/profile
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "reception1",
    "full_name": "Ahmed Mohamed",
    "role": "reception",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "email": "reception1@gym.com",
    "phone": "01234567890",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

---

## 👥 Customer Management Endpoints

### 5. POST /api/customers/register

**Purpose:** Register a new customer/member

**Request:**
```json
POST /api/customers/register
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Ahmed Hassan",
  "phone": "01234567890",
  "email": "ahmed@example.com",
  "national_id": "29901012345678",
  "birthdate": "1999-01-01",
  "gender": "male",
  "address": "123 Main St, Cairo",
  "emergency_contact": "01098765432",
  "weight": 80,
  "height": 175,
  "health_notes": "No health issues",
  "branch_id": 1
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "GYM-151",
    "branch_id": 1,
    "created_at": "2026-02-11T10:30:00Z",
    "client_credentials": {
      "client_id": "GYM-151",
      "phone": "01234567890",
      "temporary_password": "AB12CD34",
      "note": "Give these credentials to the client for their mobile app login"
    }
  }
}
```

**Important:** 
- Generate unique QR code (format: `GYM-{customer_id}`)
- Generate random 8-character temporary password for client app login
- Hash the password before storing in database
- Set `password_changed = false` for new customers

**Error Responses:**

```json
// 409 - Phone already registered
{
  "success": false,
  "message": "Phone number already registered",
  "error_code": "PHONE_EXISTS"
}

// 409 - National ID already registered
{
  "success": false,
  "message": "National ID already registered",
  "error_code": "NATIONAL_ID_EXISTS"
}
```

---

### 6. GET /api/customers

**Purpose:** Get list of customers (with search, filter, pagination)

**Request:**
```json
GET /api/customers?search=ahmed&branch_id=1&page=1&limit=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `search` (optional): Search by name, phone, or QR code
- `branch_id` (optional): Filter by branch (required for reception/manager roles)
- `has_active_subscription` (optional): true/false
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "customers": [
      {
        "id": 151,
        "full_name": "Ahmed Hassan",
        "phone": "01234567890",
        "email": "ahmed@example.com",
        "qr_code": "GYM-151",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "has_active_subscription": true,
        "active_subscription": {
          "id": 456,
          "service_name": "Monthly Gym",
          "end_date": "2026-03-11",
          "status": "active"
        },
        "created_at": "2026-02-11T10:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 98,
      "items_per_page": 20
    }
  }
}
```

---

### 7. GET /api/customers/{id}

**Purpose:** Get detailed customer information

**Request:**
```json
GET /api/customers/151
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "national_id": "29901012345678",
    "birthdate": "1999-01-01",
    "gender": "male",
    "age": 27,
    "address": "123 Main St, Cairo",
    "emergency_contact": "01098765432",
    "weight": 80,
    "height": 175,
    "bmi": 26.1,
    "bmi_category": "Overweight",
    "qr_code": "GYM-151",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "health_notes": "No health issues",
    "created_at": "2026-02-11T10:30:00Z",
    "active_subscription": {
      "id": 456,
      "service_id": 1,
      "service_name": "Monthly Gym",
      "start_date": "2026-02-11",
      "end_date": "2026-03-11",
      "status": "active",
      "amount": 500.0,
      "days_remaining": 28
    },
    "subscription_history": [
      {
        "id": 455,
        "service_name": "Monthly Gym",
        "start_date": "2026-01-11",
        "end_date": "2026-02-11",
        "status": "expired",
        "amount": 500.0
      }
    ],
    "total_payments": 1000.0,
    "total_visits": 45
  }
}
```

**Error Response:**
```json
// 404 - Customer not found
{
  "success": false,
  "message": "Customer not found",
  "error_code": "CUSTOMER_NOT_FOUND"
}
```

---

## 📝 Subscription Management Endpoints

### 8. GET /api/subscriptions

**Purpose:** Get list of subscriptions with filters

**Request:**
```json
GET /api/subscriptions?customer_id=151&status=active&branch_id=1&page=1&limit=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `customer_id` (optional): Filter by specific customer
- `status` (optional): active, expired, frozen, stopped
- `branch_id` (optional): Filter by branch
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `page` (optional): Page number
- `limit` (optional): Items per page

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "subscriptions": [
      {
        "id": 456,
        "customer_id": 151,
        "customer_name": "Ahmed Hassan",
        "customer_phone": "01234567890",
        "service_id": 1,
        "service_name": "Monthly Gym",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "start_date": "2026-02-11",
        "end_date": "2026-03-11",
        "status": "active",
        "amount": 500.0,
        "payment_method": "cash",
        "days_remaining": 28,
        "created_at": "2026-02-11T10:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_items": 195,
      "items_per_page": 20
    },
    "summary": {
      "total_active": 145,
      "total_expired": 50,
      "total_revenue": 72500.0
    }
  }
}
```

---

### 9. GET /api/subscriptions/{id}

**Purpose:** Get detailed subscription information

**Request:**
```json
GET /api/subscriptions/456
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "customer": {
      "id": 151,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "qr_code": "GYM-151"
    },
    "service": {
      "id": 1,
      "name": "Monthly Gym",
      "duration_days": 30,
      "price": 500.0
    },
    "branch": {
      "id": 1,
      "name": "Dragon Club"
    },
    "start_date": "2026-02-11",
    "end_date": "2026-03-11",
    "status": "active",
    "amount": 500.0,
    "payment_method": "cash",
    "receipt_number": "RCP-20260211-001",
    "days_remaining": 28,
    "created_at": "2026-02-11T10:30:00Z",
    "created_by": {
      "id": 1,
      "username": "reception1",
      "full_name": "Ahmed Mohamed"
    },
    "payment_details": {
      "payment_id": 789,
      "payment_date": "2026-02-11T10:30:00Z",
      "amount": 500.0,
      "method": "cash"
    }
  }
}
```

---

### 10. POST /api/subscriptions/renew

**Purpose:** Renew an expired or expiring subscription

**Request:**
```json
POST /api/subscriptions/renew
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 151,
  "service_id": 1,
  "branch_id": 1,
  "amount": 500.00,
  "payment_method": "card",
  "notes": "Renewal for February"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Subscription renewed successfully",
  "data": {
    "subscription_id": 457,
    "customer_id": 151,
    "service_id": 1,
    "start_date": "2026-03-11",
    "end_date": "2026-04-11",
    "status": "active",
    "amount": 500.0,
    "payment_method": "card",
    "receipt_number": "RCP-20260311-015",
    "previous_subscription_id": 456
  }
}
```

**Implementation:**
- If customer has active subscription, start_date = current end_date
- If expired, start_date = today
- Create new subscription record
- Create payment record
- Mark old subscription as expired if overlapping

---

### 11. POST /api/subscriptions/freeze

**Purpose:** Temporarily freeze a subscription (pause it)

**Request:**
```json
POST /api/subscriptions/freeze
Authorization: Bearer {token}
Content-Type: application/json

{
  "subscription_id": 456,
  "freeze_days": 7,
  "reason": "Medical emergency"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Subscription frozen successfully",
  "data": {
    "subscription_id": 456,
    "status": "frozen",
    "original_end_date": "2026-03-11",
    "new_end_date": "2026-03-18",
    "freeze_days": 7,
    "frozen_at": "2026-02-11T10:30:00Z"
  }
}
```

**Implementation:**
- Update subscription status to "frozen"
- Extend end_date by freeze_days
- Log freeze action with reason

---

### 12. POST /api/subscriptions/stop

**Purpose:** Permanently stop/cancel a subscription

**Request:**
```json
POST /api/subscriptions/stop
Authorization: Bearer {token}
Content-Type: application/json

{
  "subscription_id": 456,
  "reason": "Relocating to another city",
  "refund_amount": 0.0
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Subscription stopped successfully",
  "data": {
    "subscription_id": 456,
    "status": "stopped",
    "stopped_at": "2026-02-11T10:30:00Z",
    "refund_amount": 0.0
  }
}
```

---

## 💰 Payment Management Endpoints

### 13. GET /api/payments

**Purpose:** Get list of payments with filters

**Request:**
```json
GET /api/payments?branch_id=1&payment_method=cash&date_from=2026-02-01&date_to=2026-02-11&page=1&limit=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `branch_id` (optional): Filter by branch
- `customer_id` (optional): Filter by customer
- `payment_method` (optional): cash, card, transfer
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `page`, `limit`: Pagination

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "id": 789,
        "customer_id": 151,
        "customer_name": "Ahmed Hassan",
        "subscription_id": 456,
        "service_name": "Monthly Gym",
        "amount": 500.0,
        "payment_method": "cash",
        "receipt_number": "RCP-20260211-001",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "payment_date": "2026-02-11T10:30:00Z",
        "created_by": "reception1"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 25,
      "total_items": 487,
      "items_per_page": 20
    },
    "summary": {
      "total_amount": 243500.0,
      "cash_total": 150000.0,
      "card_total": 80000.0,
      "transfer_total": 13500.0,
      "total_count": 487
    }
  }
}
```

---

### 14. POST /api/payments/record

**Purpose:** Record a standalone payment (not linked to subscription)

**Request:**
```json
POST /api/payments/record
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 151,
  "amount": 100.0,
  "payment_method": "cash",
  "description": "Personal training session",
  "branch_id": 1
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Payment recorded successfully",
  "data": {
    "payment_id": 790,
    "customer_id": 151,
    "amount": 100.0,
    "payment_method": "cash",
    "receipt_number": "RCP-20260211-002",
    "branch_id": 1,
    "payment_date": "2026-02-11T11:00:00Z"
  }
}
```

---

### 15. POST /api/payments/daily-closing

**Purpose:** Close daily cash register and record cash counts

**Request:**
```json
POST /api/payments/daily-closing
Authorization: Bearer {token}
Content-Type: application/json

{
  "branch_id": 1,
  "cash_counted": 15250.0,
  "card_total": 8500.0,
  "transfer_total": 2000.0,
  "notes": "All transactions verified"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Daily closing completed successfully",
  "data": {
    "closing_id": 123,
    "branch_id": 1,
    "date": "2026-02-11",
    "expected_cash": 15000.0,
    "actual_cash": 15250.0,
    "cash_difference": 250.0,
    "card_total": 8500.0,
    "transfer_total": 2000.0,
    "total_revenue": 25750.0,
    "transaction_count": 52,
    "closed_by": "reception1",
    "closed_at": "2026-02-11T20:00:00Z"
  }
}
```

**Implementation:**
- Calculate expected cash from all cash payments today
- Compare with actual counted cash
- Record any difference (shortage/surplus)
- Generate daily report

---

## 🏋️ Services & Offerings Endpoints

### 16. GET /api/services

**Purpose:** Get list of available gym services/plans

**Request:**
```json
GET /api/services?branch_id=1&active=true
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "services": [
      {
        "id": 1,
        "name": "Monthly Gym",
        "description": "1 month gym access",
        "duration_days": 30,
        "price": 500.0,
        "service_type": "gym",
        "is_active": true,
        "features": [
          "Full gym access",
          "Cardio equipment",
          "Weight training",
          "Locker room"
        ]
      },
      {
        "id": 2,
        "name": "3 Months Gym",
        "description": "3 months gym access",
        "duration_days": 90,
        "price": 1350.0,
        "service_type": "gym",
        "is_active": true,
        "discount_percentage": 10
      },
      {
        "id": 3,
        "name": "Personal Training - 8 Sessions",
        "description": "8 one-on-one training sessions",
        "duration_days": 30,
        "price": 800.0,
        "service_type": "personal_training",
        "is_active": true
      }
    ]
  }
}
```

---

### 17. GET /api/services/{id}

**Purpose:** Get detailed service information

**Request:**
```json
GET /api/services/1
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Monthly Gym",
    "description": "1 month full gym access with all equipment",
    "duration_days": 30,
    "price": 500.0,
    "service_type": "gym",
    "is_active": true,
    "features": [
      "Full gym access",
      "Cardio equipment",
      "Weight training",
      "Locker room",
      "Shower facilities"
    ],
    "statistics": {
      "active_subscriptions": 145,
      "total_subscriptions": 523,
      "monthly_revenue": 72500.0
    }
  }
}
```

---

## 🏢 Branch Management Endpoints

### 18. GET /api/branches

**Purpose:** Get list of gym branches

**Request:**
```json
GET /api/branches
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "branches": [
      {
        "id": 1,
        "name": "Dragon Club",
        "address": "123 Main St, Cairo",
        "phone": "02-12345678",
        "email": "dragon@gym.com",
        "is_active": true,
        "active_members": 145,
        "total_members": 312,
        "monthly_revenue": 72500.0
      },
      {
        "id": 2,
        "name": "Lion Fitness",
        "address": "456 Second St, Giza",
        "phone": "02-87654321",
        "email": "lion@gym.com",
        "is_active": true,
        "active_members": 89,
        "total_members": 198,
        "monthly_revenue": 44500.0
      }
    ]
  }
}
```

---

### 19. GET /api/branches/{id}

**Purpose:** Get detailed branch information

**Request:**
```json
GET /api/branches/1
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Dragon Club",
    "address": "123 Main St, Cairo",
    "phone": "02-12345678",
    "email": "dragon@gym.com",
    "manager": {
      "id": 2,
      "name": "Manager 1",
      "phone": "01234567890"
    },
    "is_active": true,
    "opening_hours": "6:00 AM - 11:00 PM",
    "facilities": [
      "Cardio Zone",
      "Weight Training Area",
      "Group Classes Studio",
      "Locker Rooms",
      "Sauna"
    ],
    "statistics": {
      "active_members": 145,
      "total_members": 312,
      "staff_count": 5,
      "monthly_revenue": 72500.0,
      "daily_visits_avg": 89
    }
  }
}
```

---

### 20. GET /api/branches/{id}/performance

**Purpose:** Get branch performance metrics

**Request:**
```json
GET /api/branches/1/performance?period=month
Authorization: Bearer {token}
```

**Query Parameters:**
- `period`: day, week, month, year

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "period": "month",
    "date_from": "2026-01-11",
    "date_to": "2026-02-11",
    "metrics": {
      "revenue": {
        "total": 72500.0,
        "cash": 45000.0,
        "card": 22500.0,
        "transfer": 5000.0,
        "growth_percentage": 15.5
      },
      "memberships": {
        "new_subscriptions": 23,
        "renewals": 98,
        "cancellations": 5,
        "active_count": 145,
        "growth_percentage": 12.3
      },
      "attendance": {
        "total_visits": 2678,
        "daily_average": 89,
        "peak_hours": ["6:00-8:00", "18:00-21:00"]
      },
      "customer_satisfaction": {
        "rating": 4.5,
        "complaints": 3,
        "resolved_complaints": 2
      }
    }
  }
}
```

---

## 📞 Complaints Management Endpoints

### 21. GET /api/complaints

**Purpose:** Get list of customer complaints

**Request:**
```json
GET /api/complaints?branch_id=1&status=pending&page=1&limit=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `branch_id` (optional): Filter by branch
- `status` (optional): pending, resolved
- `date_from`, `date_to`: Date range
- `page`, `limit`: Pagination

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "complaints": [
      {
        "id": 45,
        "customer_id": 151,
        "customer_name": "Ahmed Hassan",
        "customer_phone": "01234567890",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "complaint_type": "equipment",
        "description": "Treadmill not working properly",
        "status": "pending",
        "priority": "medium",
        "submitted_at": "2026-02-11T09:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 12,
      "items_per_page": 20
    },
    "summary": {
      "pending": 8,
      "resolved": 4,
      "average_resolution_time_hours": 24
    }
  }
}
```

---

### 22. POST /api/complaints/submit

**Purpose:** Submit a new complaint

**Request:**
```json
POST /api/complaints/submit
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 151,
  "branch_id": 1,
  "complaint_type": "equipment",
  "description": "Treadmill #3 is making strange noises",
  "priority": "medium"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Complaint submitted successfully",
  "data": {
    "complaint_id": 46,
    "ticket_number": "CMP-20260211-046",
    "status": "pending",
    "submitted_at": "2026-02-11T10:30:00Z",
    "estimated_resolution": "2026-02-12T10:30:00Z"
  }
}
```

---

## 📊 Reports & Analytics Endpoints

### 23. GET /api/reports/revenue

**Purpose:** Get revenue report with various breakdowns

**Request:**
```json
GET /api/reports/revenue?branch_id=1&date_from=2026-01-01&date_to=2026-02-11&group_by=day
Authorization: Bearer {token}
```

**Query Parameters:**
- `branch_id` (optional): Specific branch or all branches
- `date_from`, `date_to`: Date range
- `group_by`: day, week, month, payment_method, service_type

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2026-01-01",
      "to": "2026-02-11"
    },
    "total_revenue": 145000.0,
    "breakdown": [
      {
        "date": "2026-02-11",
        "revenue": 3500.0,
        "transaction_count": 7,
        "cash": 2000.0,
        "card": 1200.0,
        "transfer": 300.0
      },
      {
        "date": "2026-02-10",
        "revenue": 4200.0,
        "transaction_count": 9,
        "cash": 2500.0,
        "card": 1500.0,
        "transfer": 200.0
      }
    ],
    "payment_methods": {
      "cash": 87000.0,
      "card": 48000.0,
      "transfer": 10000.0
    },
    "service_types": {
      "gym_memberships": 120000.0,
      "personal_training": 20000.0,
      "other": 5000.0
    }
  }
}
```

---

### 24. GET /api/reports/daily

**Purpose:** Get daily operations summary

**Request:**
```json
GET /api/reports/daily?branch_id=1&date=2026-02-11
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "date": "2026-02-11",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "revenue": {
      "total": 3500.0,
      "cash": 2000.0,
      "card": 1200.0,
      "transfer": 300.0
    },
    "subscriptions": {
      "new": 3,
      "renewals": 4,
      "cancellations": 0,
      "freezes": 1
    },
    "attendance": {
      "total_visits": 89,
      "unique_members": 78,
      "peak_hour": "18:00-19:00"
    },
    "new_customers": 3,
    "complaints": {
      "new": 1,
      "resolved": 2,
      "pending": 8
    }
  }
}
```

---

### 25. GET /api/reports/weekly

**Purpose:** Get weekly summary report

**Request:**
```json
GET /api/reports/weekly?branch_id=1&week_start=2026-02-05
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "week_start": "2026-02-05",
    "week_end": "2026-02-11",
    "branch_id": 1,
    "revenue": {
      "total": 24500.0,
      "daily_average": 3500.0,
      "growth_vs_last_week": 8.5
    },
    "subscriptions": {
      "new": 21,
      "renewals": 28,
      "active_end_of_week": 145
    },
    "attendance": {
      "total_visits": 623,
      "daily_average": 89,
      "busiest_day": "Monday"
    },
    "new_customers": 21,
    "top_services": [
      {
        "service_name": "Monthly Gym",
        "count": 35,
        "revenue": 17500.0
      },
      {
        "service_name": "3 Months Gym",
        "count": 8,
        "revenue": 10800.0
      }
    ]
  }
}
```

---

### 26. GET /api/reports/monthly

**Purpose:** Get monthly summary report

**Request:**
```json
GET /api/reports/monthly?branch_id=1&year=2026&month=2
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "year": 2026,
    "month": 2,
    "month_name": "February",
    "branch_id": 1,
    "revenue": {
      "total": 72500.0,
      "daily_average": 2500.0,
      "growth_vs_last_month": 15.5,
      "cash": 45000.0,
      "card": 22500.0,
      "transfer": 5000.0
    },
    "subscriptions": {
      "new": 23,
      "renewals": 98,
      "cancellations": 5,
      "active_end_of_month": 145,
      "growth_percentage": 12.3
    },
    "attendance": {
      "total_visits": 2678,
      "daily_average": 89,
      "unique_members": 145
    },
    "new_customers": 23,
    "customer_retention_rate": 95.8,
    "top_performing_days": [
      "Monday",
      "Wednesday",
      "Saturday"
    ]
  }
}
```

---

### 27. GET /api/reports/branch-comparison

**Purpose:** Compare performance across branches

**Request:**
```json
GET /api/reports/branch-comparison?date_from=2026-01-01&date_to=2026-02-11
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2026-01-01",
      "to": "2026-02-11"
    },
    "branches": [
      {
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "revenue": 145000.0,
        "active_members": 145,
        "new_members": 23,
        "retention_rate": 95.8,
        "daily_visits_avg": 89,
        "ranking": 1
      },
      {
        "branch_id": 2,
        "branch_name": "Lion Fitness",
        "revenue": 89000.0,
        "active_members": 89,
        "new_members": 15,
        "retention_rate": 92.5,
        "daily_visits_avg": 56,
        "ranking": 2
      }
    ],
    "totals": {
      "total_revenue": 234000.0,
      "total_active_members": 234,
      "total_new_members": 38,
      "average_retention_rate": 94.2
    }
  }
}
```

---

### 28. GET /api/reports/employee-performance

**Purpose:** Get employee performance metrics

**Request:**
```json
GET /api/reports/employee-performance?branch_id=1&role=reception&date_from=2026-01-01&date_to=2026-02-11
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "employees": [
      {
        "employee_id": 1,
        "name": "Ahmed Mohamed",
        "role": "reception",
        "branch_name": "Dragon Club",
        "metrics": {
          "subscriptions_processed": 45,
          "renewals_processed": 67,
          "payments_collected": 56250.0,
          "new_customers_registered": 15,
          "average_processing_time_minutes": 4.5,
          "customer_satisfaction_rating": 4.7
        }
      }
    ]
  }
}
```

---

## 💼 Finance Management Endpoints

### 29. GET /api/finance/daily-sales

**Purpose:** Get daily sales summary for accounting

**Request:**
```json
GET /api/finance/daily-sales?branch_id=1&date=2026-02-11
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "date": "2026-02-11",
    "branch_id": 1,
    "sales_summary": {
      "total_revenue": 3500.0,
      "cash_revenue": 2000.0,
      "card_revenue": 1200.0,
      "transfer_revenue": 300.0,
      "transaction_count": 7
    },
    "cash_reconciliation": {
      "opening_balance": 1000.0,
      "cash_collected": 2000.0,
      "expected_closing": 3000.0,
      "actual_closing": 3050.0,
      "difference": 50.0,
      "status": "surplus"
    },
    "transactions": [
      {
        "receipt_number": "RCP-20260211-001",
        "time": "10:30:00",
        "customer_name": "Ahmed Hassan",
        "description": "Monthly Gym Subscription",
        "amount": 500.0,
        "payment_method": "cash",
        "processed_by": "reception1"
      }
    ]
  }
}
```

---

### 30. GET /api/finance/expenses

**Purpose:** Get expenses report

**Request:**
```json
GET /api/finance/expenses?branch_id=1&date_from=2026-01-01&date_to=2026-02-11&category=all
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2026-01-01",
      "to": "2026-02-11"
    },
    "total_expenses": 45000.0,
    "categories": [
      {
        "category": "salaries",
        "amount": 30000.0,
        "percentage": 66.7
      },
      {
        "category": "utilities",
        "amount": 5000.0,
        "percentage": 11.1
      },
      {
        "category": "equipment_maintenance",
        "amount": 3000.0,
        "percentage": 6.7
      },
      {
        "category": "rent",
        "amount": 7000.0,
        "percentage": 15.6
      }
    ],
    "expenses": [
      {
        "id": 123,
        "date": "2026-02-11",
        "category": "equipment_maintenance",
        "description": "Treadmill belt replacement",
        "amount": 500.0,
        "approved_by": "manager1"
      }
    ]
  }
}
```

---

### 31. GET /api/finance/cash-differences

**Purpose:** Get cash shortage/surplus history

**Request:**
```json
GET /api/finance/cash-differences?branch_id=1&date_from=2026-01-01&date_to=2026-02-11
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2026-01-01",
      "to": "2026-02-11"
    },
    "summary": {
      "total_shortages": 150.0,
      "total_surpluses": 200.0,
      "net_difference": 50.0,
      "days_with_differences": 8
    },
    "differences": [
      {
        "date": "2026-02-11",
        "branch_name": "Dragon Club",
        "expected_cash": 3000.0,
        "actual_cash": 3050.0,
        "difference": 50.0,
        "type": "surplus",
        "closed_by": "reception1",
        "notes": "Extra 50 EGP found, source unclear"
      },
      {
        "date": "2026-02-10",
        "branch_name": "Dragon Club",
        "expected_cash": 2500.0,
        "actual_cash": 2450.0,
        "difference": -50.0,
        "type": "shortage",
        "closed_by": "reception1",
        "notes": "Counted twice, shortage confirmed"
      }
    ]
  }
}
```

---

## 🕒 Attendance Management Endpoints

### 32. GET /api/attendance

**Purpose:** Get gym entry/attendance records

**Request:**
```json
GET /api/attendance?branch_id=1&date=2026-02-11&customer_id=151
Authorization: Bearer {token}
```

**Query Parameters:**
- `branch_id` (optional): Filter by branch
- `customer_id` (optional): Filter by specific customer
- `date` (optional): Specific date (YYYY-MM-DD)
- `date_from`, `date_to`: Date range
- `page`, `limit`: Pagination

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "attendance_records": [
      {
        "id": 1234,
        "customer_id": 151,
        "customer_name": "Ahmed Hassan",
        "qr_code": "GYM-151",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "entry_time": "2026-02-11T07:30:00Z",
        "exit_time": "2026-02-11T09:00:00Z",
        "duration_minutes": 90,
        "subscription_status": "active"
      }
    ],
    "summary": {
      "total_visits": 89,
      "unique_visitors": 78,
      "peak_hour": "18:00-19:00"
    }
  }
}
```

---

### 33. GET /api/attendance/by-branch

**Purpose:** Get attendance statistics by branch

**Request:**
```json
GET /api/attendance/by-branch?date=2026-02-11
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "date": "2026-02-11",
    "branches": [
      {
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "total_visits": 89,
        "unique_visitors": 78,
        "peak_hour": "18:00-19:00",
        "capacity_percentage": 65,
        "hourly_breakdown": [
          {
            "hour": "06:00",
            "count": 12
          },
          {
            "hour": "07:00",
            "count": 23
          }
        ]
      }
    ]
  }
}
```

---

## 🔔 Alerts & Notifications Endpoints

### 34. GET /api/alerts

**Purpose:** Get system alerts and notifications

**Request:**
```json
GET /api/alerts?branch_id=1&type=all&status=unread
Authorization: Bearer {token}
```

**Query Parameters:**
- `branch_id` (optional): Filter by branch
- `type` (optional): expiring_subscriptions, cash_difference, low_attendance, equipment_issue
- `status` (optional): read, unread, all
- `priority` (optional): high, medium, low

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": 567,
        "type": "expiring_subscriptions",
        "priority": "medium",
        "title": "15 subscriptions expiring this week",
        "message": "15 customer subscriptions will expire in the next 7 days",
        "branch_id": 1,
        "data": {
          "expiring_count": 15,
          "customers": [
            {
              "customer_id": 151,
              "customer_name": "Ahmed Hassan",
              "phone": "01234567890",
              "expiry_date": "2026-02-15"
            }
          ]
        },
        "status": "unread",
        "created_at": "2026-02-11T08:00:00Z"
      },
      {
        "id": 568,
        "type": "cash_difference",
        "priority": "high",
        "title": "Cash shortage detected",
        "message": "Cash shortage of 50 EGP on 2026-02-10",
        "branch_id": 1,
        "data": {
          "date": "2026-02-10",
          "difference": -50.0,
          "expected": 2500.0,
          "actual": 2450.0
        },
        "status": "unread",
        "created_at": "2026-02-10T20:00:00Z"
      }
    ],
    "summary": {
      "total": 12,
      "unread": 8,
      "high_priority": 2,
      "medium_priority": 6,
      "low_priority": 4
    }
  }
}
```

---

### 35. GET /api/alerts/smart

**Purpose:** Get smart recommendations and insights

**Request:**
```json
GET /api/alerts/smart?branch_id=1
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "type": "revenue_opportunity",
        "title": "15 customers due for renewal",
        "description": "Contact these customers to renew their subscriptions",
        "action": "Send renewal reminders",
        "potential_revenue": 7500.0,
        "customers": [
          {
            "id": 151,
            "name": "Ahmed Hassan",
            "phone": "01234567890",
            "expiry_date": "2026-02-15"
          }
        ]
      },
      {
        "type": "attendance_pattern",
        "title": "Low attendance on Sundays",
        "description": "Sunday attendance is 40% lower than other days",
        "action": "Consider special promotions for Sundays",
        "data": {
          "sunday_avg": 45,
          "weekday_avg": 75,
          "difference_percentage": -40
        }
      },
      {
        "type": "service_popularity",
        "title": "Monthly Gym most popular",
        "description": "70% of members prefer Monthly Gym subscription",
        "action": "Consider promoting 3-month packages with discount",
        "data": {
          "monthly_count": 102,
          "quarterly_count": 35,
          "yearly_count": 8
        }
      }
    ]
  }
}
```

---

## 📱 CLIENT APP ENDPOINTS (Separate Mobile App for Gym Members)

### 36. POST /api/client/auth/login

**Purpose:** Login for gym members/customers using phone + password

**Request:**
```json
POST /api/client/auth/login
Content-Type: application/json

{
  "phone": "01234567890",
  "password": "AB12CD34"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 604800,
    "password_changed": false,
    "customer": {
      "id": 151,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "qr_code": "GYM-151",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "has_active_subscription": true
    }
  }
}
```

**Important:**
- `password_changed = false` → Force user to change password (first login)
- Token expires in 7 days for client app (vs 1 day for staff app)

**Error Responses:**

```json
// 401 - Invalid credentials
{
  "success": false,
  "message": "Invalid phone number or password",
  "error_code": "INVALID_CREDENTIALS"
}

// 403 - Account inactive
{
  "success": false,
  "message": "Your account is inactive. Please contact reception.",
  "error_code": "ACCOUNT_INACTIVE"
}
```

---

### 37. POST /api/client/change-password

**Purpose:** Change password for client app user

**Request:**
```json
POST /api/client/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "current_password": "AB12CD34",
  "new_password": "mynewpass123"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": {
    "password_changed": true
  }
}
```

**Validation:**
- New password minimum 6 characters
- New password must be different from current
- Current password must be correct

---

### 38. GET /api/client/me

**Purpose:** Get client profile with subscription details

**Request:**
```json
GET /api/client/me
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "birthdate": "1999-01-01",
    "age": 27,
    "gender": "male",
    "qr_code": "GYM-151",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "weight": 80,
    "height": 175,
    "bmi": 26.1,
    "bmi_category": "Overweight",
    "active_subscription": {
      "id": 456,
      "service_id": 1,
      "service_name": "Monthly Gym",
      "start_date": "2026-02-11",
      "end_date": "2026-03-11",
      "status": "active",
      "days_remaining": 28
    },
    "password_changed": true,
    "total_visits": 45,
    "member_since": "2025-06-15"
  }
}
```

---

### 39. GET /api/client/qr

**Purpose:** Get time-limited QR token for gym entry

**Request:**
```json
GET /api/client/qr
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "qr_token": "GYM-151-1707648600-a3f2c1d",
    "qr_code": "GYM-151",
    "valid_for_seconds": 300,
    "expires_at": "2026-02-11T10:35:00Z",
    "customer_name": "Ahmed Hassan",
    "subscription_status": "active",
    "branch_name": "Dragon Club"
  }
}
```

**Implementation:**
- Generate time-limited token: `{qr_code}-{timestamp}-{random}`
- Token expires in 5 minutes
- Client app should auto-refresh QR code
- Reception scans this QR code for entry

---

### 40. POST /api/client/qr/refresh

**Purpose:** Refresh QR code token

**Request:**
```json
POST /api/client/qr/refresh
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "qr_token": "GYM-151-1707648900-b4g3e2f",
    "valid_for_seconds": 300,
    "expires_at": "2026-02-11T10:40:00Z"
  }
}
```

---

### 41. GET /api/client/entry-history

**Purpose:** Get client's gym entry history

**Request:**
```json
GET /api/client/entry-history?limit=30
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "entries": [
      {
        "id": 1234,
        "branch_name": "Dragon Club",
        "entry_time": "2026-02-11T07:30:00Z",
        "exit_time": "2026-02-11T09:00:00Z",
        "duration_minutes": 90
      },
      {
        "id": 1233,
        "branch_name": "Dragon Club",
        "entry_time": "2026-02-10T18:00:00Z",
        "exit_time": "2026-02-10T20:15:00Z",
        "duration_minutes": 135
      }
    ],
    "statistics": {
      "total_visits": 45,
      "this_month": 12,
      "average_duration_minutes": 95,
      "most_frequent_time": "18:00-20:00"
    }
  }
}
```

---

### 42. GET /api/client/subscription

**Purpose:** Get detailed subscription information

**Request:**
```json
GET /api/client/subscription
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "current_subscription": {
      "id": 456,
      "service_name": "Monthly Gym",
      "start_date": "2026-02-11",
      "end_date": "2026-03-11",
      "status": "active",
      "days_remaining": 28,
      "days_elapsed": 2,
      "amount_paid": 500.0,
      "payment_method": "cash"
    },
    "history": [
      {
        "id": 455,
        "service_name": "Monthly Gym",
        "start_date": "2026-01-11",
        "end_date": "2026-02-11",
        "status": "expired",
        "amount_paid": 500.0
      }
    ],
    "total_amount_paid": 1000.0,
    "subscription_count": 2
  }
}
```

---

### 43. GET /api/client/subscriptions/history

**Purpose:** Get full subscription payment history

**Request:**
```json
GET /api/client/subscriptions/history?page=1&limit=20
Authorization: Bearer {token}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "subscriptions": [
      {
        "id": 456,
        "service_name": "Monthly Gym",
        "start_date": "2026-02-11",
        "end_date": "2026-03-11",
        "status": "active",
        "amount": 500.0,
        "payment_method": "cash",
        "receipt_number": "RCP-20260211-001",
        "payment_date": "2026-02-11T10:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 1,
      "total_items": 2
    }
  }
}
```

---

## 🔒 Authentication & Security Requirements

### JWT Token Structure

**Staff Token (1 day expiry):**
```json
{
  "user_id": 1,
  "username": "reception1",
  "role": "reception",
  "branch_id": 1,
  "exp": 1707734400,
  "iat": 1707648000
}
```

**Client Token (7 days expiry):**
```json
{
  "customer_id": 151,
  "phone": "01234567890",
  "type": "client",
  "exp": 1708252800,
  "iat": 1707648000
}
```

### Role-Based Access Control

| Endpoint | Reception | Manager | Accountant | Owner |
|----------|-----------|---------|------------|-------|
| Customer Management | ✅ Own Branch | ✅ Own Branch | ❌ | ✅ All |
| Subscription Activation | ✅ Own Branch | ✅ Own Branch | ❌ | ✅ All |
| Payments | ✅ Own Branch | ✅ Own Branch | ✅ Read All | ✅ All |
| Reports | ❌ | ✅ Own Branch | ✅ All Branches | ✅ All |
| Branch Management | ❌ | ❌ | ❌ | ✅ All |
| Employee Performance | ❌ | ✅ Own Branch | ❌ | ✅ All |

### Security Headers

All responses should include:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

---

## 📊 Database Schema Quick Reference

### customers
- id (PK, INT, AUTO_INCREMENT)
- full_name (VARCHAR)
- phone (VARCHAR, UNIQUE)
- email (VARCHAR)
- national_id (VARCHAR, UNIQUE)
- birthdate (DATE)
- gender (ENUM: male, female)
- address (TEXT)
- emergency_contact (VARCHAR)
- weight (DECIMAL)
- height (INT)
- qr_code (VARCHAR, UNIQUE, INDEX)
- branch_id (FK)
- health_notes (TEXT)
- password_hash (VARCHAR) -- For client app login
- password_changed (BOOLEAN, DEFAULT FALSE)
- is_active (BOOLEAN, DEFAULT TRUE)
- created_at (TIMESTAMP)

### subscriptions
- id (PK)
- customer_id (FK, INDEX)
- service_id (FK)
- branch_id (FK)
- start_date (DATE, INDEX)
- end_date (DATE, INDEX)
- status (ENUM: active, expired, frozen, stopped, INDEX)
- amount (DECIMAL)
- payment_method (ENUM: cash, card, transfer)
- notes (TEXT)
- created_by (FK to users)
- created_at (TIMESTAMP)

### payments
- id (PK)
- customer_id (FK, INDEX)
- subscription_id (FK, NULLABLE)
- amount (DECIMAL)
- payment_method (ENUM: cash, card, transfer)
- branch_id (FK)
- payment_date (TIMESTAMP, INDEX)
- receipt_number (VARCHAR, UNIQUE, INDEX)
- description (TEXT)
- created_by (FK to users)
- created_at (TIMESTAMP)

### services
- id (PK)
- name (VARCHAR)
- description (TEXT)
- duration_days (INT)
- price (DECIMAL)
- service_type (ENUM: gym, personal_training, group_class, other)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

### branches
- id (PK)
- name (VARCHAR)
- address (TEXT)
- phone (VARCHAR)
- email (VARCHAR)
- manager_id (FK to users, NULLABLE)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

### users (Staff)
- id (PK)
- username (VARCHAR, UNIQUE)
- password_hash (VARCHAR)
- full_name (VARCHAR)
- role (ENUM: reception, manager, accountant, owner)
- branch_id (FK, NULLABLE for owner/accountant)
- email (VARCHAR)
- phone (VARCHAR)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

### attendance
- id (PK)
- customer_id (FK, INDEX)
- branch_id (FK)
- entry_time (TIMESTAMP, INDEX)
- exit_time (TIMESTAMP, NULLABLE)
- subscription_id (FK)
- qr_token (VARCHAR)
- created_at (TIMESTAMP)

### complaints
- id (PK)
- customer_id (FK, INDEX)
- branch_id (FK)
- complaint_type (ENUM: equipment, cleanliness, staff, other)
- description (TEXT)
- status (ENUM: pending, resolved, INDEX)
- priority (ENUM: low, medium, high)
- submitted_at (TIMESTAMP, INDEX)
- resolved_at (TIMESTAMP, NULLABLE)
- resolved_by (FK to users, NULLABLE)

### daily_closings
- id (PK)
- branch_id (FK, INDEX)
- closing_date (DATE, UNIQUE INDEX with branch_id)
- expected_cash (DECIMAL)
- actual_cash (DECIMAL)
- cash_difference (DECIMAL)
- card_total (DECIMAL)
- transfer_total (DECIMAL)
- total_revenue (DECIMAL)
- transaction_count (INT)
- notes (TEXT)
- closed_by (FK to users)
- closed_at (TIMESTAMP)

---

## 🧪 Testing Commands

### 1. Test Login (Staff)
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"reception1","password":"reception123"}'
```

### 2. Test Customer Registration
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01111111111",
    "email": "test@test.com",
    "branch_id": 1,
    "weight": 75,
    "height": 170
  }'
```

### 3. Test Subscription Activation ⚠️ CRITICAL
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "customer_id": 1,
    "service_id": 1,
    "branch_id": 1,
    "amount": 500.00,
    "payment_method": "cash"
  }'
```

### 4. Test Client Login
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "01234567890",
    "password": "AB12CD34"
  }'
```

### 5. Test Get Services
```bash
curl -X GET https://yamenmod91.pythonanywhere.com/api/services \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Implementation Priority

### Phase 1: Critical (Must have for basic operations)
1. ✅ POST /api/auth/login (WORKING)
2. ⚠️ POST /api/subscriptions/activate (FAILING - FIX FIRST)
3. POST /api/customers/register
4. GET /api/customers
5. GET /api/services
6. POST /api/payments/record
7. POST /api/payments/daily-closing

### Phase 2: Core Features (Needed for full reception workflow)
8. GET /api/subscriptions
9. POST /api/subscriptions/renew
10. GET /api/customers/{id}
11. GET /api/subscriptions/{id}
12. GET /api/payments
13. POST /api/subscriptions/freeze
14. POST /api/subscriptions/stop

### Phase 3: Management & Reports (For managers and accountants)
15. GET /api/reports/daily
16. GET /api/reports/weekly
17. GET /api/reports/monthly
18. GET /api/reports/revenue
19. GET /api/branches
20. GET /api/complaints
21. POST /api/complaints/submit

### Phase 4: Client Mobile App (Separate app for gym members)
22. POST /api/client/auth/login
23. POST /api/client/change-password
24. GET /api/client/me
25. GET /api/client/qr
26. POST /api/client/qr/refresh
27. GET /api/client/entry-history
28. GET /api/client/subscription

### Phase 5: Advanced Features (Analytics and insights)
29. GET /api/reports/branch-comparison
30. GET /api/reports/employee-performance
31. GET /api/attendance
32. GET /api/alerts
33. GET /api/alerts/smart
34. GET /api/finance/daily-sales
35. GET /api/finance/expenses
36. GET /api/finance/cash-differences

---

## 🚀 Quick Start Guide for Backend Developer

### Step 1: Fix Critical Issue (30 minutes)

Implement `POST /api/subscriptions/activate`:

**Flask Example:**
```python
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import secrets

@app.route('/api/subscriptions/activate', methods=['POST'])
@jwt_required()
def activate_subscription():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    required_fields = ['customer_id', 'service_id', 'branch_id', 'amount', 'payment_method']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    customer_id = data['customer_id']
    service_id = data['service_id']
    branch_id = data['branch_id']
    amount = data['amount']
    payment_method = data['payment_method']
    
    # Check if customer exists
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found', 'error_code': 'CUSTOMER_NOT_FOUND'}), 404
    
    # Check if service exists
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'success': False, 'message': 'Service not found', 'error_code': 'SERVICE_NOT_FOUND'}), 404
    
    # Check for active subscription
    active_sub = Subscription.query.filter_by(
        customer_id=customer_id,
        status='active'
    ).first()
    
    if active_sub:
        return jsonify({
            'success': False,
            'message': 'Customer already has an active subscription',
            'error_code': 'ACTIVE_SUBSCRIPTION_EXISTS',
            'data': {
                'existing_subscription_id': active_sub.id,
                'end_date': active_sub.end_date.isoformat()
            }
        }), 409
    
    # Calculate dates
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=service.duration_days)
    
    # Generate receipt number
    today_str = datetime.now().strftime('%Y%m%d')
    daily_count = Payment.query.filter(
        Payment.receipt_number.like(f'RCP-{today_str}%')
    ).count()
    receipt_number = f'RCP-{today_str}-{str(daily_count + 1).zfill(3)}'
    
    # Create subscription
    subscription = Subscription(
        customer_id=customer_id,
        service_id=service_id,
        branch_id=branch_id,
        start_date=start_date,
        end_date=end_date,
        status='active',
        amount=amount,
        payment_method=payment_method,
        created_by=current_user['user_id']
    )
    
    db.session.add(subscription)
    db.session.flush()  # Get subscription.id
    
    # Create payment record
    payment = Payment(
        customer_id=customer_id,
        subscription_id=subscription.id,
        amount=amount,
        payment_method=payment_method,
        branch_id=branch_id,
        payment_date=datetime.now(),
        receipt_number=receipt_number,
        created_by=current_user['user_id']
    )
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Subscription activated successfully',
        'data': {
            'subscription_id': subscription.id,
            'customer_id': customer_id,
            'service_id': service_id,
            'service_name': service.name,
            'branch_id': branch_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'status': 'active',
            'amount': float(amount),
            'payment_method': payment_method,
            'receipt_number': receipt_number,
            'created_at': subscription.created_at.isoformat()
        }
    }), 201
```

### Step 2: Test Immediately
```bash
# Login
TOKEN=$(curl -s -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"reception1","password":"reception123"}' \
  | jq -r '.data.access_token')

# Test subscription activation
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "customer_id": 1,
    "service_id": 1,
    "branch_id": 1,
    "amount": 500.00,
    "payment_method": "cash"
  }' | jq
```

### Step 3: Deploy to Production
```bash
# For PythonAnywhere
git pull origin main
# Reload web app in PythonAnywhere dashboard
```

### Step 4: Verify in Flutter App
- Open Flutter app
- Try to activate a subscription
- Should work now! ✅

---

## 📝 Response Format Standards

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { /* response data */ }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "data": { /* optional additional error context */ }
}
```

### Pagination Format
```json
{
  "success": true,
  "data": {
    "items": [ /* array of items */ ],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_items": 195,
      "items_per_page": 20,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

---

## 🎯 Success Criteria

### Minimum Viable Product (MVP)
✅ When these 10 endpoints work:
1. POST /api/auth/login
2. POST /api/customers/register
3. GET /api/customers
4. GET /api/services
5. POST /api/subscriptions/activate
6. GET /api/subscriptions
7. POST /api/subscriptions/renew
8. POST /api/payments/record
9. POST /api/payments/daily-closing
10. GET /api/branches

**Result:** Reception staff can work normally, manage customers, and process subscriptions.

### Full Staff App
✅ When Phase 1-3 endpoints work (21 endpoints)

**Result:** Reception, managers, and accountants can use all features.

### Complete System
✅ When all 43 endpoints work

**Result:** Full gym management system with staff app + client mobile app.

---

## 📞 Support & Questions

### Testing Credentials

**Base URL:** `https://yamenmod91.pythonanywhere.com/api`

**Staff Accounts:**
- reception1 / reception123 (Branch 1)
- manager1 / manager123 (Branch 1)
- accountant1 / accountant123 (All branches)
- owner / owner123 (All branches)

**Test Customer (for client app):**
- Phone: 01234567890
- Password: [Will be generated on registration]

### Common Issues

**CORS Errors:**
- Add proper CORS headers to all responses
- Allow methods: GET, POST, PUT, DELETE, OPTIONS
- Allow headers: Content-Type, Authorization

**401 Unauthorized:**
- Check token in Authorization header: `Bearer {token}`
- Verify token is valid and not expired
- Check JWT secret key matches

**404 Not Found:**
- Check endpoint URL spelling
- Verify endpoint is registered in routes
- Check HTTP method (GET vs POST)

**500 Internal Server Error:**
- Check server logs for Python errors
- Verify database connection
- Check all required fields in database operations

---

## 🎉 Next Steps

1. **Read this document completely**
2. **Implement critical endpoint first:** `POST /api/subscriptions/activate`
3. **Test with curl commands** provided above
4. **Deploy to production**
5. **Verify in Flutter app**
6. **Continue with remaining endpoints** following the priority order
7. **Use response format standards** consistently
8. **Implement proper error handling**
9. **Add role-based access control**
10. **Document any deviations** from this spec

---

**This document provides everything needed to implement a production-ready backend API for the gym management system. Follow the specifications exactly for seamless integration with the Flutter frontend.**

Good luck! 🚀

