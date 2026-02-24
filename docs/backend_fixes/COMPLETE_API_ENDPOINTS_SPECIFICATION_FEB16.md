# 🎯 COMPLETE API ENDPOINTS SPECIFICATION - GYM MANAGEMENT SYSTEM
**Date:** February 16, 2026  
**Status:** COMPREHENSIVE REFERENCE DOCUMENT

---

## 📋 TABLE OF CONTENTS

1. [Staff App Endpoints](#staff-app-endpoints) (50+ endpoints)
   - Authentication (2)
   - Dashboard & Overview (8)
   - Customer Management (6)
   - Subscription Management (8)
   - Attendance & Check-In (4)
   - Branch Management (5)
   - Staff Management (6)
   - Service Management (4)
   - Payment Management (4)
   - Reports & Analytics (5)
   - Settings (3)

2. [Client App Endpoints](#client-app-endpoints) (12 endpoints)
   - Authentication (3)
   - Profile Management (3)
   - Subscription (3)
   - Attendance History (2)
   - Complaints (1)

3. [Implementation Checklist](#implementation-checklist)
4. [Test Credentials](#test-credentials)

---

## 🏢 STAFF APP ENDPOINTS

### Base URL
```
https://yamenmod91.pythonanywhere.com/api
```

### Authentication Header (Required for all authenticated endpoints)
```
Authorization: Bearer <jwt_token>
```

---

## 1. AUTHENTICATION ENDPOINTS (2)

### 1.1 Staff Login
```http
POST /api/staff/auth/login
```

**Request Body:**
```json
{
  "phone": "01012345678",
  "password": "SecurePass123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "full_name": "Ahmed Hassan",
      "phone": "01012345678",
      "email": "ahmed@dragonclub.com",
      "role": "owner",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "is_active": true
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": "Invalid phone or password"
}
```

**Roles:** `owner`, `manager`, `accountant`, `receptionist`

---

### 1.2 Staff Logout
```http
POST /api/staff/auth/logout
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 2. DASHBOARD & OVERVIEW ENDPOINTS (8)

### 2.1 Owner Dashboard Overview
```http
GET /api/dashboard/owner
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 150000.00,
    "monthly_revenue": 45000.00,
    "total_customers": 450,
    "active_customers": 320,
    "total_branches": 3,
    "total_staff": 25,
    "active_subscriptions": 320,
    "expiring_soon": 45,
    "revenue_by_branch": [
      {
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "revenue": 25000.00,
        "customers": 150
      }
    ],
    "recent_subscriptions": [
      {
        "id": 456,
        "customer_name": "Mohamed Salem",
        "service_name": "Monthly Gym",
        "amount": 500.00,
        "date": "2026-02-15T10:30:00Z"
      }
    ]
  }
}
```

---

### 2.2 Manager Dashboard Overview
```http
GET /api/dashboard/manager
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "monthly_revenue": 25000.00,
    "total_customers": 150,
    "active_customers": 120,
    "active_subscriptions": 120,
    "staff_count": 8,
    "today_checkins": 45,
    "expiring_subscriptions": 12,
    "recent_customers": [...],
    "revenue_chart": {...}
  }
}
```

---

### 2.3 Accountant Dashboard Overview
```http
GET /api/dashboard/accountant
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 45000.00,
    "total_expenses": 12000.00,
    "net_profit": 33000.00,
    "pending_payments": 5,
    "cash_collected": 30000.00,
    "card_collected": 15000.00,
    "recent_payments": [...],
    "expense_breakdown": {...}
  }
}
```

---

### 2.4 Receptionist Dashboard Overview
```http
GET /api/dashboard/receptionist
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "branch_id": 1,
    "today_checkins": 45,
    "active_subscriptions": 120,
    "expiring_today": 3,
    "recent_customers": [...],
    "pending_activations": 5
  }
}
```

---

### 2.5 Get Total Customers Count
```http
GET /api/dashboard/customers/count
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional): Filter by branch
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total": 450,
    "active": 320,
    "inactive": 130
  }
}
```

---

### 2.6 Get Active Subscriptions Count
```http
GET /api/dashboard/subscriptions/active-count
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional): Filter by branch
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "active_count": 320,
    "expiring_soon": 45
  }
}
```

---

### 2.7 Get Recent Customers
```http
GET /api/dashboard/customers/recent
Authorization: Bearer {token}
Query Parameters:
  - limit (optional): Default 20
  - branch_id (optional): Filter by branch
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 153,
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "email": "mohamed@example.com",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "is_active": true,
        "has_active_subscription": true,
        "created_at": "2026-02-15T10:30:00Z"
      }
    ],
    "total": 20
  }
}
```

---

### 2.8 Get Financial Summary
```http
GET /api/dashboard/financial-summary
Authorization: Bearer {token}
Query Parameters:
  - start_date (optional)
  - end_date (optional)
  - branch_id (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 150000.00,
    "total_expenses": 35000.00,
    "net_profit": 115000.00,
    "payment_methods": {
      "cash": 90000.00,
      "card": 60000.00
    },
    "revenue_by_service": [
      {
        "service_name": "Monthly Gym",
        "revenue": 80000.00,
        "count": 160
      }
    ]
  }
}
```

---

## 3. CUSTOMER MANAGEMENT ENDPOINTS (6)

### 3.1 Get All Customers (Paginated)
```http
GET /api/customers
Authorization: Bearer {token}
Query Parameters:
  - page (optional): Page number (default: 1)
  - limit (optional): Items per page (default: 20)
  - branch_id (optional): Filter by branch
  - search (optional): Search by name or phone
  - is_active (optional): true/false
```

**Success Response (200):**
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
        "branch_name": "Tigers Gym",
        "gender": "male",
        "date_of_birth": "1993-08-25",
        "height": 172.0,
        "weight": 92.0,
        "bmi": 31.1,
        "bmi_category": "Obese",
        "bmr": 1964.65,
        "daily_calories": 3045,
        "qr_code": "CUST-115-TIGERS",
        "temp_password": "AB12CD",
        "password_changed": false,
        "is_active": true,
        "has_active_subscription": true,
        "created_at": "2026-02-14T17:07:24Z",
        "updated_at": "2026-02-14T18:09:47Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 8,
      "total_items": 150,
      "items_per_page": 20
    }
  }
}
```

---

### 3.2 Get Single Customer Details
```http
GET /api/customers/{customer_id}
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 115,
    "full_name": "Adel Saad",
    "phone": "01025867870",
    "email": "customer115@example.com",
    "national_id": "29072938235553",
    "address": "41 Street, Giza",
    "branch_id": 2,
    "branch_name": "Tigers Gym",
    "gender": "male",
    "date_of_birth": "1993-08-25",
    "height": 172.0,
    "weight": 92.0,
    "bmi": 31.1,
    "bmi_category": "Obese",
    "bmr": 1964.65,
    "daily_calories": 3045,
    "health_notes": "Asthma - no heavy cardio",
    "qr_code": "CUST-115-TIGERS",
    "temp_password": "AB12CD",
    "password_changed": false,
    "is_active": true,
    "created_at": "2026-02-14T17:07:24Z",
    "updated_at": "2026-02-14T18:09:47Z",
    "active_subscription": {
      "id": 456,
      "service_name": "Monthly Gym",
      "status": "active",
      "start_date": "2026-02-10",
      "end_date": "2026-03-10",
      "remaining_coins": 25
    },
    "attendance_stats": {
      "total_visits": 45,
      "this_month": 12,
      "last_visit": "2026-02-15T09:30:00Z"
    }
  }
}
```

---

### 3.3 Register New Customer
```http
POST /api/customers
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "full_name": "Ahmed Hassan",
  "phone": "01012345678",
  "email": "ahmed@example.com",
  "national_id": "29501012345678",
  "date_of_birth": "1995-01-01",
  "gender": "male",
  "address": "123 Street, Cairo",
  "branch_id": 1,
  "height": 175.0,
  "weight": 80.0,
  "health_notes": "None"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "customer_id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01012345678",
    "qr_code": "CUST-151-DRAGON",
    "temp_password": "XY56ZW",
    "bmi": 26.12,
    "bmi_category": "Overweight",
    "bmr": 1745.5,
    "daily_calories": 2618
  }
}
```

**Notes:**
- System automatically generates:
  - QR code: `CUST-{id}-{BRANCH_PREFIX}`
  - Temporary password: 6 random chars (e.g., "AB12CD")
  - BMI, BMR, and daily calories calculations

---

### 3.4 Update Customer
```http
PUT /api/customers/{customer_id}
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "full_name": "Ahmed Hassan Updated",
  "email": "newemail@example.com",
  "address": "New Address",
  "height": 176.0,
  "weight": 78.0,
  "health_notes": "Updated notes"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Customer updated successfully",
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan Updated",
    "bmi": 25.18,
    "updated_at": "2026-02-16T10:30:00Z"
  }
}
```

---

### 3.5 Regenerate Customer QR Code
```http
POST /api/customers/{customer_id}/regenerate-qr
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "QR code regenerated successfully",
  "data": {
    "customer_id": 151,
    "qr_code": "CUST-151-DRAGON-NEW-1234567890"
  }
}
```

---

### 3.6 Deactivate/Activate Customer
```http
PATCH /api/customers/{customer_id}/status
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "is_active": false
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Customer status updated successfully",
  "data": {
    "customer_id": 151,
    "is_active": false
  }
}
```

---

## 4. SUBSCRIPTION MANAGEMENT ENDPOINTS (8)

### 4.1 Get All Subscriptions (Paginated & Filtered)
```http
GET /api/subscriptions
Authorization: Bearer {token}
Query Parameters:
  - page (optional): Page number (default: 1)
  - limit (optional): Items per page (default: 20)
  - branch_id (optional): Filter by branch
  - customer_id (optional): Filter by customer
  - status (optional): active|expired|frozen
  - type (optional): coins|time_based|sessions|training
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 456,
        "customer_id": 115,
        "customer_name": "Adel Saad",
        "customer_phone": "01025867870",
        "service_id": 1,
        "service_name": "Monthly Gym",
        "branch_id": 2,
        "branch_name": "Tigers Gym",
        "subscription_type": "coins",
        "start_date": "2026-02-10",
        "end_date": "2027-02-10",
        "validity_months": 12,
        "status": "active",
        "remaining_coins": 25,
        "total_coins": 30,
        "remaining_sessions": null,
        "total_sessions": null,
        "amount": 500.00,
        "payment_method": "cash",
        "created_at": "2026-02-10T10:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 95
    }
  }
}
```

---

### 4.2 Get Single Subscription Details
```http
GET /api/subscriptions/{subscription_id}
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "customer": {
      "id": 115,
      "full_name": "Adel Saad",
      "phone": "01025867870",
      "qr_code": "CUST-115-TIGERS"
    },
    "service": {
      "id": 1,
      "name": "Monthly Gym",
      "type": "gym"
    },
    "branch": {
      "id": 2,
      "name": "Tigers Gym"
    },
    "subscription_type": "coins",
    "start_date": "2026-02-10",
    "end_date": "2027-02-10",
    "validity_months": 12,
    "status": "active",
    "remaining_coins": 25,
    "total_coins": 30,
    "remaining_sessions": null,
    "total_sessions": null,
    "amount": 500.00,
    "payment_method": "cash",
    "discount": 0.00,
    "created_at": "2026-02-10T10:00:00Z",
    "payment": {
      "id": 789,
      "amount": 500.00,
      "method": "cash",
      "date": "2026-02-10T10:00:00Z"
    },
    "usage_history": [
      {
        "date": "2026-02-15",
        "coins_used": 1,
        "action": "check_in"
      }
    ]
  }
}
```

---

### 4.3 Activate New Subscription
```http
POST /api/subscriptions/activate
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "customer_id": 115,
  "service_id": 1,
  "branch_id": 2,
  "amount": 500.00,
  "payment_method": "cash",
  "discount": 0.00,
  "subscription_type": "coins",
  "coins": 30,
  "validity_months": 12,
  "notes": "First subscription"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 456,
    "customer_name": "Adel Saad",
    "service_name": "Monthly Gym",
    "subscription_type": "coins",
    "start_date": "2026-02-16",
    "end_date": "2027-02-16",
    "total_coins": 30,
    "remaining_coins": 30,
    "amount": 500.00,
    "payment_id": 789
  }
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Cannot create subscription for another branch. Customer is in branch 2, but you are trying to create subscription for branch 1"
}
```

---

### 4.4 Deduct Coin from Subscription (Check-in)
```http
POST /api/subscriptions/{subscription_id}/deduct-coin
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "coins_to_deduct": 1
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "1 coin deducted successfully",
  "data": {
    "subscription_id": 456,
    "remaining_coins": 24,
    "total_coins": 30
  }
}
```

---

### 4.5 Deduct Session from Subscription
```http
POST /api/subscriptions/{subscription_id}/deduct-session
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "sessions_to_deduct": 1
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "1 session deducted successfully",
  "data": {
    "subscription_id": 456,
    "remaining_sessions": 9,
    "total_sessions": 10
  }
}
```

---

### 4.6 Freeze Subscription
```http
POST /api/subscriptions/{subscription_id}/freeze
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "freeze_days": 7
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Subscription frozen for 7 days",
  "data": {
    "subscription_id": 456,
    "status": "frozen",
    "freeze_until": "2026-02-23",
    "new_end_date": "2026-03-17"
  }
}
```

---

### 4.7 Cancel Subscription
```http
POST /api/subscriptions/{subscription_id}/cancel
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "reason": "Customer request"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Subscription cancelled successfully",
  "data": {
    "subscription_id": 456,
    "status": "cancelled",
    "cancelled_at": "2026-02-16T10:30:00Z"
  }
}
```

---

### 4.8 Expire Old Subscriptions (Cron Job)
```http
POST /api/subscriptions/expire-old
Authorization: Bearer {token}
```

**Purpose:** Automatically expire subscriptions based on:
- Time-based: `end_date` has passed
- Coin-based: `remaining_coins` = 0
- Session-based: `remaining_sessions` = 0

**Success Response (200):**
```json
{
  "success": true,
  "message": "Expired 15 subscriptions",
  "data": {
    "expired_count": 15,
    "expired_ids": [456, 457, 458]
  }
}
```

---

## 5. ATTENDANCE & CHECK-IN ENDPOINTS (4)

### 5.1 Record Customer Check-In (QR Scan)
```http
POST /api/attendance
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "customer_id": 115,
  "qr_code": "CUST-115-TIGERS",
  "check_in_time": "2026-02-16T10:30:00Z",
  "action": "check_in_only"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Check-in recorded successfully",
  "data": {
    "attendance_id": 789,
    "customer_id": 115,
    "customer_name": "Adel Saad",
    "check_in_time": "2026-02-16T10:30:00Z",
    "branch_id": 2,
    "branch_name": "Tigers Gym",
    "action": "check_in_only",
    "subscription_id": 456,
    "coins_deducted": 1,
    "remaining_coins": 24
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Customer not found with this QR code"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "No active subscription found for this customer"
}
```

---

### 5.2 Get Attendance History
```http
GET /api/attendance
Authorization: Bearer {token}
Query Parameters:
  - page (optional): Page number (default: 1)
  - limit (optional): Items per page (default: 50)
  - branch_id (optional): Filter by branch
  - customer_id (optional): Filter by customer
  - start_date (optional): YYYY-MM-DD
  - end_date (optional): YYYY-MM-DD
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 789,
        "customer_id": 115,
        "customer_name": "Adel Saad",
        "customer_phone": "01025867870",
        "branch_id": 2,
        "branch_name": "Tigers Gym",
        "check_in_time": "2026-02-16T10:30:00Z",
        "action": "check_in_only",
        "coins_deducted": 1
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_items": 500
    }
  }
}
```

---

### 5.3 Get Customer's Attendance History
```http
GET /api/attendance/customer/{customer_id}
Authorization: Bearer {token}
Query Parameters:
  - limit (optional): Default 30
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "customer_id": 115,
    "customer_name": "Adel Saad",
    "total_visits": 45,
    "this_month_visits": 12,
    "last_visit": "2026-02-16T10:30:00Z",
    "history": [
      {
        "id": 789,
        "check_in_time": "2026-02-16T10:30:00Z",
        "branch_name": "Tigers Gym",
        "coins_deducted": 1
      }
    ]
  }
}
```

---

### 5.4 Get Today's Check-Ins
```http
GET /api/attendance/today
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional): Filter by branch
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "date": "2026-02-16",
    "total_checkins": 45,
    "by_branch": [
      {
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "checkins": 25
      },
      {
        "branch_id": 2,
        "branch_name": "Tigers Gym",
        "checkins": 20
      }
    ],
    "recent_checkins": [...]
  }
}
```

---

## 6. BRANCH MANAGEMENT ENDPOINTS (5)

### 6.1 Get All Branches
```http
GET /api/branches
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Dragon Club",
        "prefix": "DRAGON",
        "address": "123 Main Street, Cairo",
        "phone": "0225551234",
        "email": "dragon@gym.com",
        "is_active": true,
        "customer_count": 150,
        "staff_count": 8,
        "active_subscriptions": 120,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 3
  }
}
```

---

### 6.2 Get Single Branch Details
```http
GET /api/branches/{branch_id}
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Dragon Club",
    "prefix": "DRAGON",
    "address": "123 Main Street, Cairo",
    "phone": "0225551234",
    "email": "dragon@gym.com",
    "is_active": true,
    "customer_count": 150,
    "staff_count": 8,
    "active_subscriptions": 120,
    "monthly_revenue": 45000.00,
    "today_checkins": 25,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

### 6.3 Create New Branch
```http
POST /api/branches
Authorization: Bearer {token}
Role: owner only
```

**Request Body:**
```json
{
  "name": "Lions Gym",
  "prefix": "LIONS",
  "address": "456 New Street, Giza",
  "phone": "0225559876",
  "email": "lions@gym.com"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Branch created successfully",
  "data": {
    "branch_id": 4,
    "name": "Lions Gym",
    "prefix": "LIONS",
    "is_active": true
  }
}
```

---

### 6.4 Update Branch
```http
PUT /api/branches/{branch_id}
Authorization: Bearer {token}
Role: owner only
```

**Request Body:**
```json
{
  "name": "Lions Gym Updated",
  "address": "New Address",
  "phone": "0225559999"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Branch updated successfully",
  "data": {
    "branch_id": 4,
    "name": "Lions Gym Updated",
    "updated_at": "2026-02-16T10:30:00Z"
  }
}
```

---

### 6.5 Deactivate/Activate Branch
```http
PATCH /api/branches/{branch_id}/status
Authorization: Bearer {token}
Role: owner only
```

**Request Body:**
```json
{
  "is_active": false
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Branch status updated successfully",
  "data": {
    "branch_id": 4,
    "is_active": false
  }
}
```

---

## 7. STAFF MANAGEMENT ENDPOINTS (6)

### 7.1 Get All Staff
```http
GET /api/staff
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional): Filter by branch
  - role (optional): owner|manager|accountant|receptionist
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "full_name": "Ahmed Hassan",
        "phone": "01012345678",
        "email": "ahmed@gym.com",
        "role": "owner",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "is_active": true,
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "total": 25
  }
}
```

---

### 7.2 Get Single Staff Details
```http
GET /api/staff/{staff_id}
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01012345678",
    "email": "ahmed@gym.com",
    "role": "manager",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "permissions": ["view_customers", "manage_subscriptions"]
  }
}
```

---

### 7.3 Create New Staff
```http
POST /api/staff
Authorization: Bearer {token}
Role: owner or manager
```

**Request Body:**
```json
{
  "full_name": "Mohamed Ali",
  "phone": "01087654321",
  "email": "mohamed@gym.com",
  "password": "TempPass123",
  "role": "receptionist",
  "branch_id": 1
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Staff member created successfully",
  "data": {
    "staff_id": 26,
    "full_name": "Mohamed Ali",
    "role": "receptionist",
    "branch_name": "Dragon Club"
  }
}
```

---

### 7.4 Update Staff
```http
PUT /api/staff/{staff_id}
Authorization: Bearer {token}
Role: owner or manager
```

**Request Body:**
```json
{
  "full_name": "Mohamed Ali Updated",
  "email": "newemail@gym.com",
  "branch_id": 2
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Staff member updated successfully",
  "data": {
    "staff_id": 26,
    "full_name": "Mohamed Ali Updated",
    "updated_at": "2026-02-16T10:30:00Z"
  }
}
```

---

### 7.5 Change Staff Password
```http
POST /api/staff/{staff_id}/change-password
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "old_password": "OldPass123",
  "new_password": "NewSecurePass456"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

### 7.6 Deactivate/Activate Staff
```http
PATCH /api/staff/{staff_id}/status
Authorization: Bearer {token}
Role: owner or manager
```

**Request Body:**
```json
{
  "is_active": false
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Staff status updated successfully",
  "data": {
    "staff_id": 26,
    "is_active": false
  }
}
```

---

## 8. SERVICE MANAGEMENT ENDPOINTS (4)

### 8.1 Get All Services
```http
GET /api/services
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Monthly Gym",
        "type": "gym",
        "description": "Full access to gym facilities",
        "duration_days": 30,
        "price": 500.00,
        "is_active": true
      },
      {
        "id": 2,
        "name": "Personal Training - 10 Sessions",
        "type": "training",
        "description": "10 personal training sessions",
        "sessions": 10,
        "price": 1500.00,
        "is_active": true
      }
    ],
    "total": 5
  }
}
```

---

### 8.2 Get Single Service Details
```http
GET /api/services/{service_id}
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Monthly Gym",
    "type": "gym",
    "description": "Full access to gym facilities",
    "duration_days": 30,
    "price": 500.00,
    "is_active": true,
    "active_subscriptions": 120
  }
}
```

---

### 8.3 Create New Service
```http
POST /api/services
Authorization: Bearer {token}
Role: owner or manager
```

**Request Body:**
```json
{
  "name": "3-Month Gym",
  "type": "gym",
  "description": "3 months gym access",
  "duration_days": 90,
  "price": 1200.00
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Service created successfully",
  "data": {
    "service_id": 6,
    "name": "3-Month Gym",
    "price": 1200.00
  }
}
```

---

### 8.4 Update Service
```http
PUT /api/services/{service_id}
Authorization: Bearer {token}
Role: owner or manager
```

**Request Body:**
```json
{
  "name": "3-Month Gym Updated",
  "price": 1100.00,
  "description": "Updated description"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Service updated successfully",
  "data": {
    "service_id": 6,
    "name": "3-Month Gym Updated",
    "price": 1100.00
  }
}
```

---

## 9. PAYMENT MANAGEMENT ENDPOINTS (4)

### 9.1 Get All Payments
```http
GET /api/payments
Authorization: Bearer {token}
Query Parameters:
  - page (optional)
  - limit (optional)
  - branch_id (optional)
  - payment_method (optional): cash|card|bank_transfer
  - start_date (optional)
  - end_date (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 789,
        "customer_id": 115,
        "customer_name": "Adel Saad",
        "subscription_id": 456,
        "service_name": "Monthly Gym",
        "amount": 500.00,
        "payment_method": "cash",
        "branch_id": 2,
        "branch_name": "Tigers Gym",
        "collected_by": "Ahmed Hassan",
        "payment_date": "2026-02-10T10:00:00Z"
      }
    ],
    "pagination": {...},
    "summary": {
      "total_amount": 45000.00,
      "cash": 30000.00,
      "card": 15000.00
    }
  }
}
```

---

### 9.2 Get Single Payment Details
```http
GET /api/payments/{payment_id}
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 789,
    "customer": {...},
    "subscription": {...},
    "amount": 500.00,
    "payment_method": "cash",
    "discount": 0.00,
    "branch": {...},
    "collected_by": "Ahmed Hassan",
    "payment_date": "2026-02-10T10:00:00Z",
    "notes": "First payment"
  }
}
```

---

### 9.3 Record Manual Payment
```http
POST /api/payments
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "customer_id": 115,
  "subscription_id": 456,
  "amount": 500.00,
  "payment_method": "cash",
  "discount": 0.00,
  "notes": "Payment for monthly subscription"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Payment recorded successfully",
  "data": {
    "payment_id": 790,
    "amount": 500.00,
    "payment_date": "2026-02-16T10:30:00Z"
  }
}
```

---

### 9.4 Get Payment Statistics
```http
GET /api/payments/statistics
Authorization: Bearer {token}
Query Parameters:
  - start_date (optional)
  - end_date (optional)
  - branch_id (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 45000.00,
    "total_payments": 90,
    "average_payment": 500.00,
    "by_method": {
      "cash": 30000.00,
      "card": 15000.00
    },
    "by_branch": [...]
  }
}
```

---

## 10. REPORTS & ANALYTICS ENDPOINTS (5)

### 10.1 Get Revenue Report
```http
GET /api/reports/revenue
Authorization: Bearer {token}
Query Parameters:
  - start_date (required): YYYY-MM-DD
  - end_date (required): YYYY-MM-DD
  - branch_id (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2026-02-01",
      "end_date": "2026-02-16"
    },
    "total_revenue": 45000.00,
    "by_service": [...],
    "by_branch": [...],
    "by_payment_method": {...},
    "daily_breakdown": [...]
  }
}
```

---

### 10.2 Get Customer Analytics
```http
GET /api/reports/customers
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_customers": 450,
    "active_customers": 320,
    "new_this_month": 25,
    "churned_this_month": 5,
    "by_branch": [...],
    "growth_rate": 5.5
  }
}
```

---

### 10.3 Get Subscription Analytics
```http
GET /api/reports/subscriptions
Authorization: Bearer {token}
Query Parameters:
  - branch_id (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_active": 320,
    "expiring_this_week": 15,
    "expiring_this_month": 45,
    "by_type": {
      "coins": 200,
      "time_based": 100,
      "sessions": 20
    },
    "by_service": [...]
  }
}
```

---

### 10.4 Get Attendance Analytics
```http
GET /api/reports/attendance
Authorization: Bearer {token}
Query Parameters:
  - start_date (optional)
  - end_date (optional)
  - branch_id (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_checkins": 1250,
    "unique_customers": 280,
    "average_per_day": 45,
    "peak_hours": [...],
    "by_day_of_week": {...}
  }
}
```

---

### 10.5 Get Financial Summary Report
```http
GET /api/reports/financial-summary
Authorization: Bearer {token}
Query Parameters:
  - start_date (optional)
  - end_date (optional)
  - branch_id (optional)
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_revenue": 150000.00,
    "total_expenses": 35000.00,
    "net_profit": 115000.00,
    "profit_margin": 76.67,
    "revenue_by_month": [...],
    "expense_breakdown": {...}
  }
}
```

---

## 11. SETTINGS ENDPOINTS (3)

### 11.1 Get System Settings
```http
GET /api/settings
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "gym_name": "Dragon Fitness Group",
    "currency": "EGP",
    "timezone": "Africa/Cairo",
    "business_hours": {
      "open": "06:00",
      "close": "23:00"
    },
    "features": {
      "qr_checkin": true,
      "online_payments": false,
      "freeze_subscriptions": true
    }
  }
}
```

---

### 11.2 Update System Settings
```http
PUT /api/settings
Authorization: Bearer {token}
Role: owner only
```

**Request Body:**
```json
{
  "gym_name": "New Gym Name",
  "business_hours": {
    "open": "05:00",
    "close": "24:00"
  }
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

---

### 11.3 Get Staff Profile
```http
GET /api/staff/profile
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01012345678",
    "email": "ahmed@gym.com",
    "role": "manager",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "permissions": [...]
  }
}
```

---

# 📱 CLIENT APP ENDPOINTS

### Base URL
```
https://yamenmod91.pythonanywhere.com/api
```

### Authentication Header (Required for authenticated endpoints)
```
Authorization: Bearer <jwt_token>
```

---

## 1. CLIENT AUTHENTICATION ENDPOINTS (3)

### 1.1 Client Login
```http
POST /api/client/auth/login
```

**Request Body:**
```json
{
  "phone": "01077827638",
  "password": "RX04AF"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "customer": {
      "id": 1,
      "full_name": "Mohamed Salem",
      "phone": "01077827638",
      "email": "customer1@example.com",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "qr_code": "CUST-001-DRAGON",
      "password_changed": false,
      "is_active": true,
      "height": 175,
      "weight": 80,
      "bmi": 26.1,
      "bmi_category": "Overweight",
      "bmr": 1850.5,
      "daily_calories": 2868
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "subscription": {
      "id": 124,
      "status": "active",
      "subscription_type": "coins",
      "remaining_coins": 25,
      "start_date": "2026-02-01",
      "end_date": "2026-03-01",
      "display_metric": "coins",
      "display_value": 25,
      "display_label": "25 Coins"
    }
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": "Invalid phone or password"
}
```

**Error Response (403):**
```json
{
  "success": false,
  "error": "Your account is not active. Please contact reception."
}
```

---

### 1.2 Client Change Password
```http
POST /api/client/auth/change-password
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "old_password": "RX04AF",
  "new_password": "MyNewSecurePass123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": {
    "password_changed": true
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Old password is incorrect"
}
```

---

### 1.3 Client Logout
```http
POST /api/client/auth/logout
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 2. CLIENT PROFILE ENDPOINTS (3)

### 2.1 Get Client Profile
```http
GET /api/client/profile
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "full_name": "Mohamed Salem",
    "phone": "01077827638",
    "email": "customer1@example.com",
    "national_id": "29501011234567",
    "address": "123 Street, Cairo",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "gender": "male",
    "date_of_birth": "1995-01-01",
    "age": 31,
    "height": 175,
    "weight": 80,
    "bmi": 26.1,
    "bmi_category": "Overweight",
    "bmr": 1850.5,
    "daily_calories": 2868,
    "ideal_weight": 68.5,
    "health_notes": "None",
    "qr_code": "CUST-001-DRAGON",
    "is_active": true,
    "created_at": "2026-01-15T10:00:00Z"
  }
}
```

---

### 2.2 Update Client Profile
```http
PUT /api/client/profile
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "address": "New Address",
  "weight": 78.0,
  "height": 176.0
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "weight": 78.0,
    "height": 176.0,
    "bmi": 25.18,
    "updated_at": "2026-02-16T10:30:00Z"
  }
}
```

---

### 2.3 Get Client QR Code
```http
GET /api/client/qr-code
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "customer_id": 1,
    "qr_code": "CUST-001-DRAGON",
    "qr_image_url": "https://api.example.com/qr/CUST-001-DRAGON.png"
  }
}
```

---

## 3. CLIENT SUBSCRIPTION ENDPOINTS (3)

### 3.1 Get Active Subscription
```http
GET /api/client/subscription
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 124,
    "service_name": "Monthly Gym",
    "service_type": "gym",
    "subscription_type": "coins",
    "start_date": "2026-02-01",
    "end_date": "2026-03-01",
    "status": "active",
    "remaining_coins": 25,
    "total_coins": 30,
    "remaining_sessions": null,
    "total_sessions": null,
    "months_remaining": null,
    "days_remaining": null,
    "display_metric": "coins",
    "display_value": 25,
    "display_label": "25 Coins",
    "amount_paid": 500.00,
    "payment_method": "cash",
    "can_freeze": true,
    "freeze_days_remaining": 7,
    "created_at": "2026-02-01T10:00:00Z"
  }
}
```

**Response when subscription is time-based:**
```json
{
  "success": true,
  "data": {
    "id": 125,
    "subscription_type": "time_based",
    "start_date": "2026-02-01",
    "end_date": "2026-04-01",
    "status": "active",
    "display_metric": "time",
    "display_value": 44,
    "display_label": "1 month, 14 days",
    "months_remaining": 1,
    "days_remaining": 44
  }
}
```

**Response when subscription is sessions:**
```json
{
  "success": true,
  "data": {
    "id": 126,
    "subscription_type": "sessions",
    "status": "active",
    "display_metric": "sessions",
    "display_value": 8,
    "display_label": "8 Sessions",
    "remaining_sessions": 8,
    "total_sessions": 10
  }
}
```

**Response when no subscription:**
```json
{
  "success": true,
  "data": null,
  "message": "No active subscription"
}
```

---

### 3.2 Get Subscription History
```http
GET /api/client/subscriptions/history
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 124,
        "service_name": "Monthly Gym",
        "subscription_type": "coins",
        "start_date": "2026-02-01",
        "end_date": "2026-03-01",
        "status": "active",
        "amount": 500.00,
        "created_at": "2026-02-01T10:00:00Z"
      },
      {
        "id": 123,
        "service_name": "Monthly Gym",
        "subscription_type": "time_based",
        "start_date": "2026-01-01",
        "end_date": "2026-02-01",
        "status": "expired",
        "amount": 500.00,
        "created_at": "2026-01-01T10:00:00Z"
      }
    ],
    "total": 2
  }
}
```

---

### 3.3 Get Subscription Details
```http
GET /api/client/subscriptions/{subscription_id}
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 124,
    "service": {
      "id": 1,
      "name": "Monthly Gym",
      "type": "gym"
    },
    "branch": {
      "id": 1,
      "name": "Dragon Club"
    },
    "subscription_type": "coins",
    "start_date": "2026-02-01",
    "end_date": "2026-03-01",
    "status": "active",
    "remaining_coins": 25,
    "total_coins": 30,
    "display_label": "25 Coins",
    "amount_paid": 500.00,
    "usage_history": [
      {
        "date": "2026-02-15",
        "coins_used": 1,
        "action": "check_in"
      }
    ]
  }
}
```

---

## 4. CLIENT ATTENDANCE ENDPOINTS (2)

### 4.1 Get My Attendance History
```http
GET /api/client/attendance
Authorization: Bearer {token}
Query Parameters:
  - limit (optional): Default 30
  - start_date (optional): YYYY-MM-DD
  - end_date (optional): YYYY-MM-DD
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_visits": 45,
    "this_month_visits": 12,
    "last_visit": "2026-02-16T10:30:00Z",
    "history": [
      {
        "id": 789,
        "check_in_time": "2026-02-16T10:30:00Z",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "coins_deducted": 1,
        "action": "check_in"
      },
      {
        "id": 788,
        "check_in_time": "2026-02-15T09:00:00Z",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "coins_deducted": 1,
        "action": "check_in"
      }
    ]
  }
}
```

---

### 4.2 Get Attendance Statistics
```http
GET /api/client/attendance/statistics
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_visits": 45,
    "this_week": 5,
    "this_month": 12,
    "average_per_week": 4,
    "most_visited_branch": "Dragon Club",
    "preferred_time": "Morning (6AM-12PM)",
    "streak_days": 7
  }
}
```

---

## 5. CLIENT COMPLAINTS ENDPOINT (1)

### 5.1 Submit Complaint
```http
POST /api/client/complaints
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "title": "Equipment Issue",
  "description": "Treadmill #5 is not working properly",
  "category": "equipment"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Complaint submitted successfully",
  "data": {
    "complaint_id": 45,
    "status": "pending",
    "submitted_at": "2026-02-16T10:30:00Z"
  }
}
```

---

# ✅ IMPLEMENTATION CHECKLIST

## Staff App Backend Endpoints

### Authentication (2/2)
- [ ] `POST /api/staff/auth/login` - Staff login
- [ ] `POST /api/staff/auth/logout` - Staff logout

### Dashboard & Overview (8/8)
- [ ] `GET /api/dashboard/owner` - Owner dashboard
- [ ] `GET /api/dashboard/manager` - Manager dashboard
- [ ] `GET /api/dashboard/accountant` - Accountant dashboard
- [ ] `GET /api/dashboard/receptionist` - Receptionist dashboard
- [ ] `GET /api/dashboard/customers/count` - Total customers count
- [ ] `GET /api/dashboard/subscriptions/active-count` - Active subscriptions count
- [ ] `GET /api/dashboard/customers/recent` - Recent customers
- [ ] `GET /api/dashboard/financial-summary` - Financial summary

### Customer Management (6/6)
- [ ] `GET /api/customers` - List all customers (paginated)
- [ ] `GET /api/customers/{id}` - Get customer details
- [ ] `POST /api/customers` - Register new customer
- [ ] `PUT /api/customers/{id}` - Update customer
- [ ] `POST /api/customers/{id}/regenerate-qr` - Regenerate QR code
- [ ] `PATCH /api/customers/{id}/status` - Activate/deactivate customer

### Subscription Management (8/8)
- [ ] `GET /api/subscriptions` - List subscriptions (paginated & filtered)
- [ ] `GET /api/subscriptions/{id}` - Get subscription details
- [ ] `POST /api/subscriptions/activate` - Activate new subscription
- [ ] `POST /api/subscriptions/{id}/deduct-coin` - Deduct coin
- [ ] `POST /api/subscriptions/{id}/deduct-session` - Deduct session
- [ ] `POST /api/subscriptions/{id}/freeze` - Freeze subscription
- [ ] `POST /api/subscriptions/{id}/cancel` - Cancel subscription
- [ ] `POST /api/subscriptions/expire-old` - Expire old subscriptions (cron)

### Attendance & Check-In (4/4)
- [ ] `POST /api/attendance` - Record check-in (QR scan)
- [ ] `GET /api/attendance` - Get attendance history
- [ ] `GET /api/attendance/customer/{id}` - Customer attendance history
- [ ] `GET /api/attendance/today` - Today's check-ins

### Branch Management (5/5)
- [ ] `GET /api/branches` - List all branches
- [ ] `GET /api/branches/{id}` - Get branch details
- [ ] `POST /api/branches` - Create new branch
- [ ] `PUT /api/branches/{id}` - Update branch
- [ ] `PATCH /api/branches/{id}/status` - Activate/deactivate branch

### Staff Management (6/6)
- [ ] `GET /api/staff` - List all staff
- [ ] `GET /api/staff/{id}` - Get staff details
- [ ] `POST /api/staff` - Create new staff member
- [ ] `PUT /api/staff/{id}` - Update staff
- [ ] `POST /api/staff/{id}/change-password` - Change password
- [ ] `PATCH /api/staff/{id}/status` - Activate/deactivate staff

### Service Management (4/4)
- [ ] `GET /api/services` - List all services
- [ ] `GET /api/services/{id}` - Get service details
- [ ] `POST /api/services` - Create new service
- [ ] `PUT /api/services/{id}` - Update service

### Payment Management (4/4)
- [ ] `GET /api/payments` - List payments
- [ ] `GET /api/payments/{id}` - Get payment details
- [ ] `POST /api/payments` - Record manual payment
- [ ] `GET /api/payments/statistics` - Payment statistics

### Reports & Analytics (5/5)
- [ ] `GET /api/reports/revenue` - Revenue report
- [ ] `GET /api/reports/customers` - Customer analytics
- [ ] `GET /api/reports/subscriptions` - Subscription analytics
- [ ] `GET /api/reports/attendance` - Attendance analytics
- [ ] `GET /api/reports/financial-summary` - Financial summary

### Settings (3/3)
- [ ] `GET /api/settings` - Get system settings
- [ ] `PUT /api/settings` - Update system settings
- [ ] `GET /api/staff/profile` - Get staff profile

---

## Client App Backend Endpoints

### Authentication (3/3)
- [ ] `POST /api/client/auth/login` - Client login
- [ ] `POST /api/client/auth/change-password` - Change password
- [ ] `POST /api/client/auth/logout` - Client logout

### Profile Management (3/3)
- [ ] `GET /api/client/profile` - Get client profile
- [ ] `PUT /api/client/profile` - Update client profile
- [ ] `GET /api/client/qr-code` - Get QR code

### Subscription (3/3)
- [ ] `GET /api/client/subscription` - Get active subscription
- [ ] `GET /api/client/subscriptions/history` - Get subscription history
- [ ] `GET /api/client/subscriptions/{id}` - Get subscription details

### Attendance (2/2)
- [ ] `GET /api/client/attendance` - Get attendance history
- [ ] `GET /api/client/attendance/statistics` - Get attendance statistics

### Complaints (1/1)
- [ ] `POST /api/client/complaints` - Submit complaint

---

# 🔑 TEST CREDENTIALS

## Staff App Test Accounts

### Owner Account
```
Phone: 01012345678
Password: owner123
Role: owner
Access: All branches, all features
```

### Manager Account
```
Phone: 01087654321
Password: manager123
Role: manager
Branch: Dragon Club (ID: 1)
Access: Branch management, customers, subscriptions
```

### Accountant Account
```
Phone: 01098765432
Password: accountant123
Role: accountant
Branch: Dragon Club (ID: 1)
Access: Payments, reports, financial data
```

### Receptionist Account
```
Phone: 01045678901
Password: receptionist123
Role: receptionist
Branch: Dragon Club (ID: 1)
Access: Customer registration, subscription activation, check-in
```

---

## Client App Test Accounts

### Sample Customer 1
```
Phone: 01077827638
Temp Password: RX04AF
Name: Mohamed Salem
Branch: Dragon Club
Subscription: Active (Coins)
```

### Sample Customer 2
```
Phone: 01022981052
Temp Password: SI19IC
Name: Layla Rashad
Branch: Dragon Club
Subscription: Active (Time-based)
```

### Sample Customer 3
```
Phone: 01041244663
Temp Password: PS02HC
Name: Ibrahim Hassan
Branch: Dragon Club
Subscription: Active (Sessions)
```

### Sample Customer 4 (No Password Changed)
```
Phone: 01025867870
Temp Password: AB12CD
Name: Adel Saad
Branch: Tigers Gym
Password Changed: false
Must change password on first login
```

---

# 📊 ENDPOINT SUMMARY

| App | Category | Endpoints | Status |
|-----|----------|-----------|--------|
| **Staff App** | Authentication | 2 | 🔴 Required |
| **Staff App** | Dashboard & Overview | 8 | 🔴 Required |
| **Staff App** | Customer Management | 6 | 🔴 Required |
| **Staff App** | Subscription Management | 8 | 🔴 Required |
| **Staff App** | Attendance & Check-In | 4 | 🔴 Required |
| **Staff App** | Branch Management | 5 | 🔴 Required |
| **Staff App** | Staff Management | 6 | 🔴 Required |
| **Staff App** | Service Management | 4 | 🟡 Optional |
| **Staff App** | Payment Management | 4 | 🔴 Required |
| **Staff App** | Reports & Analytics | 5 | 🟡 Optional |
| **Staff App** | Settings | 3 | 🟡 Optional |
| **STAFF TOTAL** | | **55** | |
| | | | |
| **Client App** | Authentication | 3 | 🔴 Required |
| **Client App** | Profile Management | 3 | 🔴 Required |
| **Client App** | Subscription | 3 | 🔴 Required |
| **Client App** | Attendance | 2 | 🔴 Required |
| **Client App** | Complaints | 1 | 🟡 Optional |
| **CLIENT TOTAL** | | **12** | |
| | | | |
| **GRAND TOTAL** | | **67** | |

---

# 🎯 CRITICAL ENDPOINTS (MUST IMPLEMENT FIRST)

## Priority 1 - Core Functionality (20 endpoints)

### Staff App (15)
1. `POST /api/staff/auth/login` - Staff login
2. `GET /api/dashboard/owner` - Owner dashboard
3. `GET /api/dashboard/manager` - Manager dashboard
4. `GET /api/dashboard/customers/count` - Customers count
5. `GET /api/dashboard/subscriptions/active-count` - Active subscriptions
6. `GET /api/customers` - List customers
7. `GET /api/customers/{id}` - Customer details
8. `POST /api/customers` - Register customer
9. `GET /api/subscriptions` - List subscriptions
10. `POST /api/subscriptions/activate` - Activate subscription
11. `POST /api/attendance` - Record check-in (QR scan)
12. `GET /api/attendance` - Attendance history
13. `GET /api/branches` - List branches
14. `GET /api/staff` - List staff
15. `GET /api/services` - List services

### Client App (5)
1. `POST /api/client/auth/login` - Client login
2. `POST /api/client/auth/change-password` - Change password
3. `GET /api/client/profile` - Get profile
4. `GET /api/client/subscription` - Get subscription
5. `GET /api/client/attendance` - Get attendance history

---

## Priority 2 - Important Features (15 endpoints)

### Staff App
- Dashboard recent customers
- Customer QR regeneration
- Subscription deduct coin/session
- Subscription expire-old (cron)
- Branch details
- Staff details
- Payment list
- Payment statistics

### Client App
- Profile update
- QR code
- Subscription history
- Attendance statistics

---

## Priority 3 - Optional Features (32 endpoints)

- Reports & analytics
- Settings management
- Branch/staff CRUD operations
- Service management
- Complaints
- Advanced filtering

---

# 📝 NOTES

1. **Branch Validation:**
   - Staff can only interact with customers/subscriptions in their assigned branch
   - Exception: Owners can access all branches

2. **Subscription Display Logic:**
   - Backend must calculate and return `display_metric`, `display_value`, and `display_label`
   - See `BACKEND_CHECKIN_AND_SUBSCRIPTION_FIX_FEB16.md` for implementation details

3. **QR Code Format:**
   - Format: `CUST-{customer_id}-{BRANCH_PREFIX}`
   - Example: `CUST-115-TIGERS`

4. **Temporary Password:**
   - Generated on customer registration
   - Format: 6 random alphanumeric characters (e.g., "AB12CD")
   - Customer must change on first login

5. **Subscription Expiration:**
   - Time-based: When `end_date` passes
   - Coin-based: When `remaining_coins` reaches 0
   - Session-based: When `remaining_sessions` reaches 0

6. **JWT Token:**
   - Include customer/staff ID, role, and branch_id in token
   - Token expiry: 30 days (recommended)

---

**Document Version:** 1.0  
**Last Updated:** February 16, 2026  
**Status:** Complete Reference Document  
**Total Endpoints:** 67 (55 Staff + 12 Client)

