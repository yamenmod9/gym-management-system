# 🚀 COMPLETE BACKEND ENDPOINTS - GYM MANAGEMENT SYSTEM

**Date:** February 14, 2026  
**For:** Claude Sonnet 4.5  
**Purpose:** Complete list of ALL required endpoints for Staff App and Client App

---

## 📋 TABLE OF CONTENTS

1. [Staff App Endpoints](#staff-app-endpoints)
2. [Client App Endpoints](#client-app-endpoints)
3. [Authentication Endpoints](#authentication-endpoints)
4. [Testing Credentials](#testing-credentials)

---

## 🏢 STAFF APP ENDPOINTS

### 1. AUTHENTICATION

#### POST `/api/auth/login`
**Purpose:** Login for all staff members (owner, managers, receptionists, accountants)

**Request:**
```json
{
  "username": "owner",
  "password": "owner123"
}
```

**Response:**
```json
{
  "status": "success",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "owner",
    "role": "owner",
    "full_name": "System Owner",
    "branch_id": null,
    "email": "owner@gym.com",
    "phone": "01000000001"
  }
}
```

**Roles:**
- `owner` - Full system access
- `branch_manager` - Branch-specific access
- `front_desk` - Reception/front desk staff
- `central_accountant` - All branches financial access
- `branch_accountant` - Branch-specific financial access

---

### 2. OWNER DASHBOARD ENDPOINTS

#### GET `/api/dashboard/overview`
**Purpose:** Get overall gym system metrics  
**Auth:** Owner only  
**Query Params:** 
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_revenue": 164521.50,
    "total_customers": 150,
    "active_subscriptions": 83,
    "total_branches": 3,
    "revenue_by_branch": [
      {
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "revenue": 65000.00,
        "customers": 60,
        "active_subscriptions": 40
      },
      {
        "branch_id": 2,
        "branch_name": "Phoenix Fitness",
        "revenue": 58000.00,
        "customers": 55,
        "active_subscriptions": 35
      },
      {
        "branch_id": 3,
        "branch_name": "Tiger Gym",
        "revenue": 41521.50,
        "customers": 35,
        "active_subscriptions": 8
      }
    ]
  }
}
```

---

#### GET `/api/customers`
**Purpose:** Get all customers across all branches  
**Auth:** Owner, Managers (filtered by branch)  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `search` (optional): Search by name, phone, email
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 50)

**Response:**
```json
{
  "status": "success",
  "data": {
    "customers": [
      {
        "id": 1,
        "full_name": "Ahmed Hassan",
        "phone": "01001234567",
        "email": "ahmed@example.com",
        "qr_code": "GYM-000001",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "gender": "male",
        "age": 25,
        "weight": 75.5,
        "height": 1.75,
        "bmi": 24.7,
        "bmi_category": "Normal",
        "has_active_subscription": true,
        "password_changed": false,
        "temporary_password": "AB12CD",
        "created_at": "2026-01-15T10:30:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "per_page": 50,
    "total_pages": 3
  }
}
```

**Note:** `temporary_password` should ONLY be returned if `password_changed` is `false`

---

#### GET `/api/customers/{id}`
**Purpose:** Get single customer details  
**Auth:** Owner, Managers (own branch only), Receptionists (own branch only)

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01001234567",
    "email": "ahmed@example.com",
    "qr_code": "GYM-000001",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "gender": "male",
    "age": 25,
    "weight": 75.5,
    "height": 1.75,
    "bmi": 24.7,
    "bmi_category": "Normal",
    "daily_calories": 2450,
    "ideal_weight": 67.4,
    "has_active_subscription": true,
    "password_changed": false,
    "temporary_password": "AB12CD",
    "created_at": "2026-01-15T10:30:00Z",
    "active_subscription": {
      "id": 1,
      "service_name": "Monthly Gym",
      "start_date": "2026-02-01",
      "end_date": "2026-03-03",
      "remaining_days": 17,
      "remaining_coins": 25,
      "total_coins": 30,
      "status": "active"
    }
  }
}
```

---

#### GET `/api/subscriptions`
**Purpose:** Get all subscriptions  
**Auth:** Owner, Managers (own branch), Accountants  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `status` (optional): active, expired, frozen
- `customer_id` (optional): Filter by customer

**Response:**
```json
{
  "status": "success",
  "data": {
    "subscriptions": [
      {
        "id": 1,
        "customer_id": 1,
        "customer_name": "Ahmed Hassan",
        "service_id": 1,
        "service_name": "Monthly Gym",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "start_date": "2026-02-01",
        "end_date": "2026-03-03",
        "status": "active",
        "remaining_days": 17,
        "remaining_coins": 25,
        "total_coins": 30,
        "amount": 500.00,
        "discount": 0.00,
        "created_at": "2026-02-01T09:00:00Z"
      }
    ],
    "total": 136
  }
}
```

---

#### GET `/api/branches`
**Purpose:** Get all gym branches  
**Auth:** Owner (all), Managers (own branch only)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Dragon Club",
      "location": "Nasr City, Cairo",
      "address": "123 Street, Nasr City, Cairo",
      "phone": "01012345678",
      "email": "dragon@gym.com",
      "is_active": true,
      "opening_hour": "06:00:00",
      "closing_hour": "23:00:00",
      "total_customers": 60,
      "active_subscriptions": 40,
      "total_revenue": 65000.00,
      "staff_count": 3,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

#### GET `/api/users/employees` or `/api/staff`
**Purpose:** Get all staff members  
**Auth:** Owner (all staff), Managers (own branch staff only)  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `role` (optional): Filter by role

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 2,
      "username": "manager_dragon",
      "role": "branch_manager",
      "full_name": "Dragon Manager",
      "email": "manager.dragon@gym.com",
      "phone": "01000000002",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 5,
      "username": "reception_dragon_1",
      "role": "front_desk",
      "full_name": "Dragon Reception 1",
      "email": "reception1.dragon@gym.com",
      "phone": "01000000005",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 3. MANAGER DASHBOARD ENDPOINTS

#### GET `/api/dashboard/branch/{branch_id}`
**Purpose:** Get branch-specific metrics  
**Auth:** Branch Manager (own branch only), Owner (all branches)

**Response:**
```json
{
  "status": "success",
  "data": {
    "branch": {
      "id": 1,
      "name": "Dragon Club",
      "location": "Nasr City, Cairo"
    },
    "total_customers": 60,
    "active_subscriptions": 40,
    "total_revenue": 65000.00,
    "staff_count": 3,
    "open_complaints": 1,
    "pending_expenses": 3
  }
}
```

---

### 4. ACCOUNTANT ENDPOINTS

#### GET `/api/payments`
**Purpose:** Get all payment transactions  
**Auth:** Accountants (all or branch-specific), Owner  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD
- `payment_method` (optional): cash, card, online

**Response:**
```json
{
  "status": "success",
  "data": {
    "payments": [
      {
        "id": 1,
        "subscription_id": 1,
        "customer_name": "Ahmed Hassan",
        "branch_name": "Dragon Club",
        "amount": 500.00,
        "discount": 0.00,
        "payment_method": "cash",
        "payment_date": "2026-02-01T10:30:00Z",
        "receipt_number": "RCP-20260201-001",
        "processed_by": "Dragon Reception 1"
      }
    ],
    "total_payments": 245,
    "total_amount": 164521.50,
    "by_method": {
      "cash": 120000.00,
      "card": 35000.00,
      "online": 9521.50
    }
  }
}
```

---

#### GET `/api/expenses`
**Purpose:** Get all expenses  
**Auth:** Accountants, Managers (own branch), Owner  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `status` (optional): pending, approved, rejected

**Response:**
```json
{
  "status": "success",
  "data": {
    "expenses": [
      {
        "id": 1,
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "category": "maintenance",
        "amount": 5000.00,
        "description": "AC repair - main hall",
        "status": "pending",
        "priority": "urgent",
        "requested_date": "2026-02-13T10:00:00Z",
        "requested_by": "Dragon Manager",
        "approved_date": null,
        "approved_by": null
      }
    ],
    "total_pending": 10,
    "pending_amount": 35000.00
  }
}
```

---

### 5. RECEPTION ENDPOINTS

#### POST `/api/customers/register`
**Purpose:** Register new customer  
**Auth:** Receptionists, Managers

**Request:**
```json
{
  "full_name": "Ahmed Hassan",
  "phone": "01001234567",
  "email": "ahmed@example.com",
  "gender": "male",
  "age": 25,
  "weight": 75.5,
  "height": 1.75,
  "branch_id": 1
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Customer registered successfully",
  "data": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01001234567",
    "email": "ahmed@example.com",
    "qr_code": "GYM-000001",
    "branch_id": 1,
    "bmi": 24.7,
    "bmi_category": "Normal",
    "daily_calories": 2450,
    "ideal_weight": 67.4,
    "temporary_password": "AB12CD",
    "password_changed": false,
    "note": "Give these credentials to the customer for their mobile app login"
  }
}
```

**IMPORTANT:** Return the PLAIN temporary password so receptionist can give it to customer!

---

#### POST `/api/subscriptions/activate`
**Purpose:** Activate subscription for customer  
**Auth:** Receptionists, Managers

**Request:**
```json
{
  "customer_id": 1,
  "service_id": 1,
  "payment_method": "cash",
  "discount": 0,
  "notes": "New member discount"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 1,
    "customer_name": "Ahmed Hassan",
    "service_name": "Monthly Gym",
    "start_date": "2026-02-14",
    "end_date": "2026-03-16",
    "total_coins": 30,
    "amount": 500.00,
    "payment_id": 1,
    "receipt_number": "RCP-20260214-001"
  }
}
```

---

#### POST `/api/entry-logs/scan`
**Purpose:** Record customer check-in via QR scan  
**Auth:** Receptionists, Managers

**Request:**
```json
{
  "qr_code": "GYM-000001",
  "branch_id": 1
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Check-in successful",
  "data": {
    "entry_log_id": 1,
    "customer_name": "Ahmed Hassan",
    "customer_id": 1,
    "entry_time": "2026-02-14T10:30:00Z",
    "coins_used": 1,
    "remaining_coins": 24,
    "subscription_end_date": "2026-03-16"
  }
}
```

**Response (No Active Subscription):**
```json
{
  "status": "error",
  "message": "No active subscription found",
  "code": "NO_SUBSCRIPTION",
  "data": {
    "customer_name": "Ahmed Hassan",
    "customer_id": 1,
    "has_expired_subscription": true,
    "last_subscription_end_date": "2026-01-15"
  }
}
```

**Response (No Coins Remaining):**
```json
{
  "status": "error",
  "message": "No coins remaining",
  "code": "NO_COINS",
  "data": {
    "customer_name": "Ahmed Hassan",
    "customer_id": 1,
    "remaining_coins": 0,
    "subscription_type": "Personal Training - 8 Sessions"
  }
}
```

**Response (Frozen Subscription):**
```json
{
  "status": "error",
  "message": "Subscription is frozen",
  "code": "FROZEN",
  "data": {
    "customer_name": "Ahmed Hassan",
    "customer_id": 1,
    "frozen_date": "2026-02-10",
    "freeze_reason": "Medical leave"
  }
}
```

---

#### GET `/api/services`
**Purpose:** Get all available services/subscriptions  
**Auth:** All staff

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Monthly Gym",
      "description": "Full gym access for 1 month with all equipment",
      "price": 500.00,
      "duration_days": 30,
      "service_type": "gym",
      "total_coins": 30,
      "freeze_days_allowed": 5,
      "is_active": true
    },
    {
      "id": 2,
      "name": "3-Month Gym",
      "description": "Full gym access for 3 months - Save 10%",
      "price": 1350.00,
      "duration_days": 90,
      "service_type": "gym",
      "total_coins": 90,
      "freeze_days_allowed": 15,
      "is_active": true
    }
  ]
}
```

---

#### GET `/api/complaints`
**Purpose:** Get all complaints  
**Auth:** All staff (filtered by branch for non-owners)  
**Query Params:**
- `branch_id` (optional)
- `status` (optional): open, resolved

**Response:**
```json
{
  "status": "success",
  "data": {
    "complaints": [
      {
        "id": 1,
        "customer_id": 1,
        "customer_name": "Ahmed Hassan",
        "branch_id": 1,
        "branch_name": "Dragon Club",
        "category": "equipment",
        "priority": "high",
        "status": "open",
        "description": "Treadmill #3 not working properly",
        "submitted_at": "2026-02-12T14:30:00Z",
        "resolved_at": null,
        "resolution_notes": null
      }
    ],
    "total_open": 11,
    "total_resolved": 39
  }
}
```

---

---

## 📱 CLIENT APP ENDPOINTS

### 1. CLIENT AUTHENTICATION

#### POST `/api/clients/request-activation`
**Purpose:** Request activation code for client login (legacy - may not be used)  
**Auth:** None

**Request:**
```json
{
  "identifier": "01001234567"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Activation code sent",
  "note": "Code expires in 10 minutes"
}
```

**Backend Logic:**
- Find customer by phone OR email
- Generate 6-digit code (e.g., 523941)
- Save with 10-minute expiry
- Send via SMS/Email (can be mocked for testing)
- Print code to console for testing

---

#### POST `/api/clients/verify-activation`
**Purpose:** Verify activation code and login (legacy - may not be used)  
**Auth:** None

**Request:**
```json
{
  "identifier": "01001234567",
  "code": "523941"
}
```

**Response:**
```json
{
  "status": "success",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "customer": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01001234567",
    "email": "ahmed@example.com",
    "qr_code": "GYM-000001",
    "branch_name": "Dragon Club",
    "password_changed": false
  }
}
```

**JWT Claims:**
```json
{
  "sub": 1,
  "type": "client",
  "exp": 1739587200
}
```

---

#### POST `/api/clients/login`
**Purpose:** Client login with phone/email + password  
**Auth:** None

**Request:**
```json
{
  "identifier": "01001234567",
  "password": "AB12CD"
}
```

**Response:**
```json
{
  "status": "success",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "customer": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01001234567",
    "email": "ahmed@example.com",
    "qr_code": "GYM-000001",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "password_changed": false,
    "has_active_subscription": true
  }
}
```

---

#### POST `/api/clients/change-password`
**Purpose:** Change client password  
**Auth:** Client JWT required

**Request:**
```json
{
  "current_password": "AB12CD",
  "new_password": "mynewpass123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

**Backend Logic:**
- Verify current password
- Hash new password
- Update `temporary_password` field
- Set `password_changed = true`

---

### 2. CLIENT PROFILE

#### GET `/api/clients/profile`
**Purpose:** Get client profile data  
**Auth:** Client JWT required

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01001234567",
    "email": "ahmed@example.com",
    "qr_code": "GYM-000001",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "gender": "male",
    "age": 25,
    "weight": 75.5,
    "height": 1.75,
    "bmi": 24.7,
    "bmi_category": "Normal",
    "daily_calories": 2450,
    "ideal_weight": 67.4,
    "password_changed": true,
    "has_active_subscription": true
  }
}
```

---

### 3. CLIENT SUBSCRIPTION

#### GET `/api/clients/subscription`
**Purpose:** Get client's active subscription  
**Auth:** Client JWT required

**Response (Has Active):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "service_id": 1,
    "service_name": "Monthly Gym",
    "service_type": "gym",
    "start_date": "2026-02-01",
    "end_date": "2026-03-03",
    "remaining_days": 17,
    "remaining_coins": 25,
    "total_coins": 30,
    "status": "active",
    "freeze_days_used": 0,
    "freeze_days_allowed": 5,
    "branch_name": "Dragon Club"
  }
}
```

**Response (No Active):**
```json
{
  "status": "success",
  "data": null,
  "message": "No active subscription"
}
```

---

### 4. CLIENT QR CODE

#### GET `/api/clients/qr`
**Purpose:** Get client QR code for scanning  
**Auth:** Client JWT required

**Response:**
```json
{
  "status": "success",
  "data": {
    "qr_code": "GYM-000001",
    "customer_name": "Ahmed Hassan",
    "has_active_subscription": true,
    "expires_at": "2026-02-14T23:59:59Z"
  }
}
```

**Note:** QR code can be simple string (e.g., "GYM-000001") - client app will render it visually

---

### 5. CLIENT ENTRY HISTORY

#### GET `/api/clients/entry-history`
**Purpose:** Get client's gym entry history  
**Auth:** Client JWT required  
**Query Params:**
- `limit` (optional): Number of records (default: 50)
- `page` (optional): Page number (default: 1)

**Response:**
```json
{
  "status": "success",
  "data": {
    "entries": [
      {
        "id": 1,
        "entry_time": "2026-02-14T10:30:00Z",
        "branch_name": "Dragon Club",
        "coins_used": 1,
        "remaining_coins": 24,
        "entry_type": "qr_scan"
      },
      {
        "id": 2,
        "entry_time": "2026-02-13T11:00:00Z",
        "branch_name": "Dragon Club",
        "coins_used": 1,
        "remaining_coins": 25,
        "entry_type": "qr_scan"
      }
    ],
    "total": 45,
    "page": 1,
    "per_page": 50
  }
}
```

---

### 6. CLIENT COMPLAINTS

#### POST `/api/clients/complaints`
**Purpose:** Submit a complaint  
**Auth:** Client JWT required

**Request:**
```json
{
  "category": "equipment",
  "priority": "medium",
  "description": "Treadmill #5 is making noise"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Complaint submitted successfully",
  "data": {
    "complaint_id": 51,
    "submitted_at": "2026-02-14T15:30:00Z",
    "status": "open"
  }
}
```

---

#### GET `/api/clients/complaints`
**Purpose:** Get client's complaints history  
**Auth:** Client JWT required

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 51,
      "category": "equipment",
      "priority": "medium",
      "status": "open",
      "description": "Treadmill #5 is making noise",
      "submitted_at": "2026-02-14T15:30:00Z",
      "resolved_at": null,
      "resolution_notes": null
    }
  ]
}
```

---

---

## 🔐 TESTING CREDENTIALS

### Staff App

| Role | Username | Password | Branch | Access |
|------|----------|----------|--------|--------|
| Owner | `owner` | `owner123` | All | Full system |
| Manager | `manager_dragon` | `manager123` | Dragon Club | Branch 1 |
| Manager | `manager_phoenix` | `manager123` | Phoenix Fitness | Branch 2 |
| Manager | `manager_tiger` | `manager123` | Tiger Gym | Branch 3 |
| Reception | `reception_dragon_1` | `reception123` | Dragon Club | Branch 1 |
| Reception | `reception_phoenix_1` | `reception123` | Phoenix Fitness | Branch 2 |
| Accountant | `accountant_central_1` | `accountant123` | All | All branches |
| Accountant | `accountant_dragon` | `accountant123` | Dragon Club | Branch 1 |

### Client App

| Phone | Temporary Password | Status |
|-------|-------------------|--------|
| `01001234567` | `AB12CD` | First time (not changed) |
| `01001234568` | `XY34ZF` | First time (not changed) |
| `01001234569` | `PQ78MN` | Changed password |

**Note:** Clients login with phone/email + temporary password (first time) or new password (after change)

---

## ✅ IMPLEMENTATION CHECKLIST

### Authentication
- [ ] Staff login endpoint
- [ ] Client login endpoint
- [ ] Client password change endpoint
- [ ] JWT token generation with proper claims
- [ ] Token expiry handling

### Owner Dashboard
- [ ] Overview metrics endpoint
- [ ] Customers list endpoint (all branches)
- [ ] Subscriptions list endpoint (all branches)
- [ ] Branches list endpoint
- [ ] Staff list endpoint (all roles)

### Manager Dashboard
- [ ] Branch metrics endpoint
- [ ] Customers list endpoint (branch-filtered)
- [ ] Subscriptions list endpoint (branch-filtered)
- [ ] Staff list endpoint (branch-filtered)

### Accountant
- [ ] Payments list endpoint
- [ ] Expenses list endpoint
- [ ] Financial reports endpoint

### Reception
- [ ] Customer registration endpoint
- [ ] Subscription activation endpoint
- [ ] QR code scanning/check-in endpoint
- [ ] Services list endpoint

### Client App
- [ ] Profile endpoint
- [ ] Active subscription endpoint
- [ ] QR code endpoint
- [ ] Entry history endpoint
- [ ] Complaints submission endpoint
- [ ] Complaints history endpoint

---

## 🚨 CRITICAL NOTES

### 1. Temporary Password Return
When registering a customer, **ALWAYS** return the plain temporary password in the response:
```json
{
  "temporary_password": "AB12CD",
  "password_changed": false,
  "note": "Give these credentials to the customer for their mobile app login"
}
```

### 2. QR Code Scanning
When scanning QR code for check-in:
- Verify customer exists
- Check for active subscription
- Check remaining coins > 0
- Check subscription not frozen
- Deduct 1 coin
- Record entry log

### 3. Role-Based Access
- **Owner:** Access to all branches
- **Manager:** Only their assigned branch
- **Receptionist:** Only their assigned branch
- **Central Accountant:** All branches
- **Branch Accountant:** Only their assigned branch

### 4. JWT Token Claims
All JWT tokens must include:
- `sub`: User/Customer ID
- `type`: "staff" or "client"
- `role`: (for staff only) "owner", "branch_manager", etc.
- `exp`: Expiration timestamp

---

**END OF ENDPOINTS PROMPT**

**Date:** February 14, 2026  
**Version:** 1.0  
**Status:** Complete ✅

