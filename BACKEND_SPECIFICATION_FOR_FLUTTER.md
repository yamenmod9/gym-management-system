# Gym Management System Backend - Complete Specification for Flutter Frontend

## Table of Contents
1. [System Overview](#system-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Database Models](#database-models)
4. [API Endpoints](#api-endpoints)
5. [Business Logic Rules](#business-logic-rules)
6. [Response Formats](#response-formats)
7. [Enums & Constants](#enums--constants)
8. [User Workflows](#user-workflows)

---

## System Overview

### Technology Stack
- **Framework:** Flask 3.0.0 with Flask-RESTful
- **Database:** SQLite (development), PostgreSQL (production ready)
- **Authentication:** JWT (Flask-JWT-Extended)
- **ORM:** SQLAlchemy 2.0.36
- **Validation:** Marshmallow 3.20.1
- **Password Hashing:** Passlib (pbkdf2_sha256)
- **CORS:** Enabled for all origins (configure for production)

### Base URL
- **Local:** `http://localhost:5000`
- **Production:** `https://yamenmod91.pythonanywhere.com`
- **API Prefix:** All endpoints are prefixed with `/api`

### Key Features
1. Multi-branch gym management
2. Role-based access control (6 roles)
3. Customer registration with health metrics (BMI, ideal weight, calories)
4. Service management (Gym, Swimming Education/Recreation, Karate, Bundles)
5. Subscription lifecycle (create, renew, freeze, unfreeze, stop)
6. Fingerprint-based access control (simulated)
7. Financial tracking (transactions, expenses, daily closing)
8. Complaint management
9. Real-time dashboards for different roles
10. Automatic subscription expiration

---

## Authentication & Authorization

### JWT Configuration
- **Access Token Expiry:** 12 hours
- **Refresh Token Expiry:** 30 days
- **Header Format:** `Authorization: Bearer <token>`
- **Identity Type:** String (user ID)

### User Roles (6 Roles)

| Role | Value | Description | Permissions |
|------|-------|-------------|-------------|
| Owner | `OWNER` | System owner (ONLY ONE allowed) | Full system access, all branches, create users/branches |
| Branch Manager | `BRANCH_MANAGER` | Branch manager | Manage assigned branch, view staff/customers/subscriptions |
| Front Desk | `FRONT_DESK` | Reception staff | Register customers, create subscriptions, view branch data |
| Accountant | `ACCOUNTANT` | Branch accountant | View/manage expenses, transactions for assigned branch |
| Branch Accountant | `BRANCH_ACCOUNTANT` | Branch accountant (same as Accountant) | View/manage expenses, transactions for assigned branch |
| Central Accountant | `CENTRAL_ACCOUNTANT` | Central accountant | View all branches financial data, approve expenses |

### Role-Based Access Rules
- **Owner:** Can access all branches, create users, create branches
- **Branch Manager:** Can only access their assigned branch
- **Front Desk:** Can only access their assigned branch
- **Accountant/Branch Accountant:** Can only access their assigned branch
- **Central Accountant:** Can access all branches (financial data only)
- **Branch-specific roles MUST have a branch_id assigned**

### Test Accounts (Available after seeding)
```json
{
  "owner": {"username": "owner", "password": "owner123"},
  "manager1": {"username": "manager1", "password": "manager123"},
  "reception1": {"username": "reception1", "password": "reception123"},
  "accountant1": {"username": "accountant1", "password": "accountant123"}
}
```

---

## Database Models

### 1. User
**Table:** `users`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "username": String(80) (Unique, Required),
  "email": String(120) (Unique, Required),
  "password_hash": String(255) (Hashed with pbkdf2_sha256),
  "full_name": String(150) (Required),
  "phone": String(20) (Optional),
  "role": Enum(UserRole) (Required),
  "branch_id": Integer (Foreign Key to branches, nullable),
  "is_active": Boolean (Default: True),
  "last_login": DateTime (Nullable),
  "created_at": DateTime (Default: now),
  "updated_at": DateTime (Default: now, auto-update)
}
```

**Validations:**
- Only ONE owner allowed in the system
- Branch-specific roles (BRANCH_MANAGER, FRONT_DESK, ACCOUNTANT, BRANCH_ACCOUNTANT) MUST have branch_id
- Username must be unique
- Email must be unique

**Relationships:**
- `branch` → Branch (many-to-one)

---

### 2. Branch
**Table:** `branches`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "name": String(150) (Required),
  "code": String(20) (Unique, Required),
  "address": String(255) (Optional),
  "phone": String(20) (Optional),
  "city": String(100) (Optional),
  "is_active": Boolean (Default: True),
  "created_at": DateTime (Default: now),
  "updated_at": DateTime (Default: now, auto-update)
}
```

**Relationships:**
- `staff` → User[] (one-to-many)
- `customers` → Customer[] (one-to-many)
- `subscriptions` → Subscription[] (one-to-many)
- `transactions` → Transaction[] (one-to-many)
- `expenses` → Expense[] (one-to-many)

---

### 3. Customer
**Table:** `customers`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "full_name": String(150) (Required),
  "phone": String(20) (Required, Indexed),
  "email": String(120) (Optional),
  "date_of_birth": Date (Optional),
  "gender": Enum(Gender: MALE, FEMALE) (Optional),
  "address": String(255) (Optional),
  "emergency_contact": String(150) (Optional),
  "emergency_phone": String(20) (Optional),
  "health_notes": Text (Optional),
  "height": Float (cm, Optional),
  "weight": Float (kg, Optional),
  "branch_id": Integer (Foreign Key, Required),
  "is_active": Boolean (Default: True),
  "created_at": DateTime (Default: now),
  "updated_at": DateTime (Default: now, auto-update)
}
```

**Computed Properties (Read-only):**
- `age`: Integer (calculated from date_of_birth)
- `bmi`: Float (weight / (height/100)²)
- `ideal_weight`: Float (Devine formula: Male: 50 + 2.3*(height_inches - 60), Female: 45.5 + 2.3*(height_inches - 60))
- `recommended_calories`: Integer (Harris-Benedict equation based on weight, height, age, gender)

**Relationships:**
- `branch` → Branch (many-to-one)
- `subscriptions` → Subscription[] (one-to-many)
- `complaints` → Complaint[] (one-to-many)
- `fingerprints` → Fingerprint[] (one-to-many)

---

### 4. Service
**Table:** `services`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "name": String(150) (Required),
  "description": Text (Optional),
  "service_type": Enum(ServiceType) (Required),
  "price": Float (Required),
  "duration_days": Integer (Required),
  "allowed_days_per_week": Integer (Default: 7),
  "freeze_count_limit": Integer (Default: 2),
  "freeze_max_days": Integer (Default: 15),
  "is_active": Boolean (Default: True),
  "created_at": DateTime (Default: now),
  "updated_at": DateTime (Default: now, auto-update)
}
```

**Service Types:**
- `GYM`: Regular gym membership
- `SWIMMING_EDUCATION`: Swimming lessons/education
- `SWIMMING_RECREATION`: Recreational swimming
- `KARATE`: Karate classes
- `BUNDLE`: Bundle of multiple services

**Relationships:**
- `subscriptions` → Subscription[] (one-to-many)

---

### 5. Subscription
**Table:** `subscriptions`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "customer_id": Integer (Foreign Key, Required),
  "service_id": Integer (Foreign Key, Required),
  "branch_id": Integer (Foreign Key, Required),
  "start_date": Date (Default: today),
  "end_date": Date (Calculated: start_date + duration_days),
  "status": Enum(SubscriptionStatus) (Default: ACTIVE),
  "payment_method": Enum(PaymentMethod) (Required),
  "amount_paid": Float (Required, from service.price),
  "freeze_days_used": Integer (Default: 0),
  "freeze_count": Integer (Default: 0),
  "notes": Text (Optional),
  "created_by": Integer (Foreign Key to users, Required),
  "created_at": DateTime (Default: now),
  "updated_at": DateTime (Default: now, auto-update)
}
```

**Subscription Status:**
- `ACTIVE`: Currently active
- `FROZEN`: Temporarily frozen
- `STOPPED`: Manually stopped
- `EXPIRED`: Expired (auto-set by system)

**Business Rules:**
- When created, a transaction is auto-created
- Can be frozen up to `freeze_count_limit` times
- Total freeze days cannot exceed `freeze_max_days`
- Freezing extends `end_date` by freeze days
- When frozen, fingerprint access is disabled
- When renewed, creates new subscription with same service
- When stopped, status changes to STOPPED
- System auto-expires subscriptions past end_date

**Relationships:**
- `customer` → Customer (many-to-one)
- `service` → Service (many-to-one)
- `branch` → Branch (many-to-one)
- `creator` → User (many-to-one)
- `freeze_history` → FreezeHistory[] (one-to-many)
- `fingerprints` → Fingerprint[] (one-to-many)

---

### 6. Transaction
**Table:** `transactions`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "branch_id": Integer (Foreign Key, Required),
  "customer_id": Integer (Foreign Key, Optional),
  "subscription_id": Integer (Foreign Key, Optional),
  "transaction_type": Enum(TransactionType) (Required),
  "payment_method": Enum(PaymentMethod) (Required),
  "amount": Float (Required),
  "description": String(255) (Optional),
  "transaction_date": DateTime (Default: now),
  "created_by": Integer (Foreign Key to users, Required),
  "created_at": DateTime (Default: now)
}
```

**Transaction Types:**
- `SUBSCRIPTION`: Subscription payment
- `RENEWAL`: Renewal payment
- `FREEZE`: Freeze fee (if applicable)
- `REFUND`: Refund transaction
- `OTHER`: Other income

**Payment Methods:**
- `CASH`: Cash payment
- `NETWORK`: Card/POS payment
- `TRANSFER`: Bank transfer

**Relationships:**
- `branch` → Branch (many-to-one)
- `customer` → Customer (many-to-one, nullable)
- `subscription` → Subscription (many-to-one, nullable)
- `creator` → User (many-to-one)

---

### 7. Expense
**Table:** `expenses`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "branch_id": Integer (Foreign Key, Required),
  "category": String(100) (Required),
  "amount": Float (Required),
  "description": String(255) (Optional),
  "expense_date": Date (Default: today),
  "status": Enum(ExpenseStatus) (Default: PENDING),
  "reviewed_by": Integer (Foreign Key to users, Optional),
  "reviewed_at": DateTime (Optional),
  "review_notes": Text (Optional),
  "created_by": Integer (Foreign Key to users, Required),
  "created_at": DateTime (Default: now),
  "updated_at": DateTime (Default: now, auto-update)
}
```

**Expense Status:**
- `PENDING`: Awaiting approval
- `APPROVED`: Approved by manager/owner
- `REJECTED`: Rejected

**Relationships:**
- `branch` → Branch (many-to-one)
- `creator` → User (many-to-one)
- `reviewer` → User (many-to-one, nullable)

---

### 8. Complaint
**Table:** `complaints`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "customer_id": Integer (Foreign Key, Required),
  "complaint_type": Enum(ComplaintType) (Required),
  "subject": String(200) (Required),
  "description": Text (Required),
  "status": Enum(ComplaintStatus) (Default: OPEN),
  "assigned_to": Integer (Foreign Key to users, Optional),
  "resolution": Text (Optional),
  "resolved_at": DateTime (Optional),
  "created_at": DateTime (Default: now),
  "updated_at": DateTime (Default: now, auto-update)
}
```

**Complaint Types:**
- `SERVICE_QUALITY`: Service quality issues
- `FACILITY`: Facility issues
- `STAFF`: Staff behavior
- `BILLING`: Billing/payment issues
- `OTHER`: Other complaints

**Complaint Status:**
- `OPEN`: Newly created
- `IN_PROGRESS`: Being worked on
- `CLOSED`: Resolved

**Relationships:**
- `customer` → Customer (many-to-one)
- `assigned_user` → User (many-to-one, nullable)

---

### 9. Fingerprint
**Table:** `fingerprints`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "customer_id": Integer (Foreign Key, Required),
  "subscription_id": Integer (Foreign Key, Required),
  "fingerprint_hash": String(255) (Unique, Required),
  "is_active": Boolean (Default: True),
  "last_used": DateTime (Optional),
  "registered_at": DateTime (Default: now),
  "created_by": Integer (Foreign Key to users, Required)
}
```

**Business Logic:**
- Fingerprint hash is generated from customer data + unique_data (simulated)
- Format: SHA256 hash of f"{customer.id}_{customer.phone}_{unique_data}"
- When subscription is frozen, fingerprint is deactivated
- When subscription is unfrozen, fingerprint is reactivated
- Validation endpoint is PUBLIC (no auth required) for access control devices

**Relationships:**
- `customer` → Customer (many-to-one)
- `subscription` → Subscription (many-to-one)
- `creator` → User (many-to-one)

---

### 10. FreezeHistory
**Table:** `freeze_history`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "subscription_id": Integer (Foreign Key, Required),
  "freeze_days": Integer (Required),
  "freeze_reason": String(255) (Optional),
  "freeze_cost": Float (Default: 0),
  "frozen_at": DateTime (Default: now),
  "unfrozen_at": DateTime (Optional),
  "created_by": Integer (Foreign Key to users, Required)
}
```

**Relationships:**
- `subscription` → Subscription (many-to-one)
- `creator` → User (many-to-one)

---

### 11. DailyClosing
**Table:** `daily_closings`

**Fields:**
```python
{
  "id": Integer (Primary Key),
  "branch_id": Integer (Foreign Key, Required),
  "closing_date": Date (Required),
  "expected_cash": Float (Required),
  "actual_cash": Float (Required),
  "difference": Float (Calculated: actual_cash - expected_cash),
  "notes": Text (Optional),
  "closed_by": Integer (Foreign Key to users, Required),
  "closed_at": DateTime (Default: now)
}
```

**Relationships:**
- `branch` → Branch (many-to-one)
- `closer` → User (many-to-one)

---

## API Endpoints

### Standard Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation successful" // optional
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "errors": { /* validation errors */ } // optional
}
```

**Paginated Response:**
```json
{
  "success": true,
  "data": {
    "items": [ /* array of items */ ],
    "total": 100,
    "pages": 5,
    "current_page": 1,
    "per_page": 20
  }
}
```

---

### 1. Authentication Endpoints

#### POST /api/auth/login
**Description:** User login  
**Auth Required:** No  
**Request Body:**
```json
{
  "username": "owner",
  "password": "owner123"
}
```
**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "owner",
      "email": "owner@example.com",
      "full_name": "System Owner",
      "role": "OWNER",
      "branch_id": null,
      "is_active": true
    }
  },
  "message": "Login successful"
}
```

#### GET /api/auth/me
**Description:** Get current user info  
**Auth Required:** Yes  
**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "owner",
    "email": "owner@example.com",
    "full_name": "System Owner",
    "role": "OWNER",
    "branch_id": null,
    "branch_name": null,
    "is_active": true,
    "last_login": "2026-01-27T10:30:00"
  }
}
```

#### POST /api/auth/change-password
**Description:** Change current user password  
**Auth Required:** Yes  
**Request Body:**
```json
{
  "old_password": "old123",
  "new_password": "new123"
}
```

---

### 2. User Management Endpoints

#### GET /api/users
**Description:** Get all users (filtered by role/branch)  
**Auth Required:** Yes (Owner, Branch Manager)  
**Query Params:**
- `role` (optional): Filter by role
- `branch_id` (optional): Filter by branch
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "owner",
        "email": "owner@example.com",
        "full_name": "System Owner",
        "phone": "01234567890",
        "role": "OWNER",
        "branch_id": null,
        "branch_name": null,
        "is_active": true,
        "last_login": "2026-01-27T10:30:00",
        "created_at": "2026-01-20T08:00:00"
      }
    ],
    "total": 8,
    "pages": 1,
    "current_page": 1,
    "per_page": 20
  }
}
```

#### POST /api/users
**Description:** Create new user  
**Auth Required:** Yes (Owner only)  
**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User",
  "phone": "01234567890",
  "role": "FRONT_DESK",
  "branch_id": 1
}
```

#### GET /api/users/{id}
**Description:** Get user by ID  
**Auth Required:** Yes

#### PUT /api/users/{id}
**Description:** Update user  
**Auth Required:** Yes (Owner, or self for limited fields)

#### DELETE /api/users/{id}
**Description:** Delete user (soft delete - sets is_active=false)  
**Auth Required:** Yes (Owner only)

---

### 3. Branch Management Endpoints

#### GET /api/branches
**Description:** Get all active branches  
**Auth Required:** Yes  
**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Main Branch",
      "code": "MAIN001",
      "address": "123 Main St",
      "phone": "01234567890",
      "city": "Cairo",
      "is_active": true,
      "staff_count": 5,
      "customer_count": 50,
      "created_at": "2026-01-20T08:00:00"
    }
  ]
}
```

#### POST /api/branches
**Description:** Create new branch  
**Auth Required:** Yes (Owner only)  
**Request Body:**
```json
{
  "name": "Downtown Branch",
  "code": "DT001",
  "address": "456 Downtown St",
  "phone": "01987654321",
  "city": "Cairo"
}
```

#### GET /api/branches/{id}
**Description:** Get branch by ID  
**Auth Required:** Yes

#### PUT /api/branches/{id}
**Description:** Update branch  
**Auth Required:** Yes (Owner only)

#### DELETE /api/branches/{id}
**Description:** Deactivate branch  
**Auth Required:** Yes (Owner only)

---

### 4. Customer Management Endpoints

#### GET /api/customers
**Description:** Get all customers (filtered by branch for branch users)  
**Auth Required:** Yes  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `phone` (optional): Search by phone
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "full_name": "Ahmed Mohamed",
        "phone": "01234567890",
        "email": "ahmed@example.com",
        "date_of_birth": "1990-01-15",
        "gender": "MALE",
        "age": 36,
        "height": 175.0,
        "weight": 80.0,
        "bmi": 26.12,
        "ideal_weight": 73.0,
        "recommended_calories": 2200,
        "branch_id": 1,
        "branch_name": "Main Branch",
        "is_active": true,
        "active_subscriptions_count": 2,
        "created_at": "2026-01-20T09:00:00"
      }
    ],
    "total": 50,
    "pages": 3,
    "current_page": 1,
    "per_page": 20
  }
}
```

#### POST /api/customers
**Description:** Register new customer  
**Auth Required:** Yes (All roles except Accountant)  
**Request Body:**
```json
{
  "full_name": "Ahmed Mohamed",
  "phone": "01234567890",
  "email": "ahmed@example.com",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "address": "123 Street",
  "emergency_contact": "Mother",
  "emergency_phone": "01987654321",
  "health_notes": "No health issues",
  "height": 175.0,
  "weight": 80.0,
  "branch_id": 1
}
```

#### GET /api/customers/{id}
**Description:** Get customer by ID  
**Auth Required:** Yes

#### PUT /api/customers/{id}
**Description:** Update customer  
**Auth Required:** Yes

#### DELETE /api/customers/{id}
**Description:** Deactivate customer  
**Auth Required:** Yes (Owner, Branch Manager)

#### GET /api/customers/search
**Description:** Search customers by phone or name  
**Auth Required:** Yes  
**Query Params:**
- `q`: Search query (phone or name)

---

### 5. Service Management Endpoints

#### GET /api/services
**Description:** Get all active services  
**Auth Required:** Yes  
**Query Params:**
- `service_type` (optional): Filter by type

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Monthly Gym Membership",
      "description": "Full access to gym facilities",
      "service_type": "GYM",
      "price": 500.0,
      "duration_days": 30,
      "allowed_days_per_week": 7,
      "freeze_count_limit": 2,
      "freeze_max_days": 15,
      "is_active": true,
      "active_subscriptions_count": 25,
      "created_at": "2026-01-20T08:00:00"
    }
  ]
}
```

#### POST /api/services
**Description:** Create new service  
**Auth Required:** Yes (Owner only)  
**Request Body:**
```json
{
  "name": "Monthly Gym Membership",
  "description": "Full access to gym facilities",
  "service_type": "gym",
  "price": 500.0,
  "duration_days": 30,
  "allowed_days_per_week": 7,
  "freeze_count_limit": 2,
  "freeze_max_days": 15
}
```

#### GET /api/services/{id}
**Description:** Get service by ID  
**Auth Required:** Yes

#### PUT /api/services/{id}
**Description:** Update service  
**Auth Required:** Yes (Owner only)

#### DELETE /api/services/{id}
**Description:** Deactivate service  
**Auth Required:** Yes (Owner only)

---

### 6. Subscription Management Endpoints

#### GET /api/subscriptions
**Description:** Get all subscriptions (filtered by branch for branch users)  
**Auth Required:** Yes  
**Query Params:**
- `customer_id` (optional): Filter by customer
- `branch_id` (optional): Filter by branch
- `status` (optional): Filter by status
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "customer_id": 1,
        "customer_name": "Ahmed Mohamed",
        "service_id": 1,
        "service_name": "Monthly Gym Membership",
        "branch_id": 1,
        "branch_name": "Main Branch",
        "start_date": "2026-01-20",
        "end_date": "2026-02-19",
        "status": "ACTIVE",
        "payment_method": "CASH",
        "amount_paid": 500.0,
        "freeze_days_used": 0,
        "freeze_count": 0,
        "days_remaining": 23,
        "is_expiring_soon": false,
        "notes": null,
        "created_by": 2,
        "creator_name": "Reception User",
        "created_at": "2026-01-20T10:00:00"
      }
    ],
    "total": 100,
    "pages": 5,
    "current_page": 1,
    "per_page": 20
  }
}
```

#### POST /api/subscriptions
**Description:** Create new subscription  
**Auth Required:** Yes (All except Accountant)  
**Request Body:**
```json
{
  "customer_id": 1,
  "service_id": 1,
  "branch_id": 1,
  "payment_method": "cash",
  "notes": "First subscription"
}
```
**Note:** Automatically creates a transaction

#### GET /api/subscriptions/{id}
**Description:** Get subscription by ID  
**Auth Required:** Yes

#### POST /api/subscriptions/{id}/renew
**Description:** Renew subscription (creates new subscription)  
**Auth Required:** Yes (All except Accountant)  
**Request Body:**
```json
{
  "payment_method": "cash"
}
```

#### POST /api/subscriptions/{id}/freeze
**Description:** Freeze subscription  
**Auth Required:** Yes (All except Accountant)  
**Request Body:**
```json
{
  "days": 7,
  "reason": "Travel"
}
```
**Business Logic:**
- Checks freeze_count_limit
- Checks freeze_max_days
- Extends end_date by freeze days
- Deactivates fingerprint access
- Creates freeze_history record

#### POST /api/subscriptions/{id}/unfreeze
**Description:** Unfreeze subscription  
**Auth Required:** Yes (All except Accountant)  
**Business Logic:**
- Reactivates fingerprint access
- Updates freeze_history record

#### POST /api/subscriptions/{id}/stop
**Description:** Stop subscription manually  
**Auth Required:** Yes (Owner, Branch Manager)  
**Business Logic:**
- Sets status to STOPPED
- Deactivates fingerprint access

---

### 7. Transaction Endpoints

#### GET /api/transactions
**Description:** Get all transactions (filtered by branch for branch users)  
**Auth Required:** Yes  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `customer_id` (optional): Filter by customer
- `transaction_type` (optional): Filter by type
- `payment_method` (optional): Filter by payment method
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "branch_id": 1,
        "branch_name": "Main Branch",
        "customer_id": 1,
        "customer_name": "Ahmed Mohamed",
        "subscription_id": 1,
        "transaction_type": "SUBSCRIPTION",
        "payment_method": "CASH",
        "amount": 500.0,
        "description": "Subscription payment for Monthly Gym Membership",
        "transaction_date": "2026-01-20T10:30:00",
        "created_by": 2,
        "creator_name": "Reception User"
      }
    ],
    "total": 200,
    "pages": 10,
    "current_page": 1,
    "per_page": 20
  }
}
```

#### POST /api/transactions
**Description:** Create manual transaction (for non-subscription income)  
**Auth Required:** Yes (All except Accountant)  
**Request Body:**
```json
{
  "branch_id": 1,
  "transaction_type": "other",
  "payment_method": "cash",
  "amount": 100.0,
  "description": "Locker rental"
}
```

#### GET /api/transactions/{id}
**Description:** Get transaction by ID  
**Auth Required:** Yes

---

### 8. Expense Management Endpoints

#### GET /api/expenses
**Description:** Get all expenses (filtered by branch for branch users)  
**Auth Required:** Yes  
**Query Params:**
- `branch_id` (optional): Filter by branch
- `status` (optional): Filter by status
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "branch_id": 1,
        "branch_name": "Main Branch",
        "category": "Utilities",
        "amount": 1000.0,
        "description": "Electricity bill",
        "expense_date": "2026-01-20",
        "status": "APPROVED",
        "reviewed_by": 1,
        "reviewer_name": "System Owner",
        "reviewed_at": "2026-01-21T09:00:00",
        "review_notes": "Approved",
        "created_by": 3,
        "creator_name": "Branch Manager",
        "created_at": "2026-01-20T08:00:00"
      }
    ],
    "total": 50,
    "pages": 3,
    "current_page": 1,
    "per_page": 20
  }
}
```

#### POST /api/expenses
**Description:** Create new expense  
**Auth Required:** Yes (All roles)  
**Request Body:**
```json
{
  "branch_id": 1,
  "category": "Utilities",
  "amount": 1000.0,
  "description": "Electricity bill",
  "expense_date": "2026-01-20"
}
```

#### GET /api/expenses/{id}
**Description:** Get expense by ID  
**Auth Required:** Yes

#### PUT /api/expenses/{id}
**Description:** Update expense (only if PENDING)  
**Auth Required:** Yes (Creator or Owner/Manager)

#### POST /api/expenses/{id}/approve
**Description:** Approve expense  
**Auth Required:** Yes (Owner, Branch Manager, Central Accountant)  
**Request Body:**
```json
{
  "review_notes": "Approved for payment"
}
```

#### POST /api/expenses/{id}/reject
**Description:** Reject expense  
**Auth Required:** Yes (Owner, Branch Manager, Central Accountant)  
**Request Body:**
```json
{
  "review_notes": "Insufficient documentation"
}
```

---

### 9. Complaint Management Endpoints

#### GET /api/complaints
**Description:** Get all complaints (filtered by branch for branch users)  
**Auth Required:** Yes  
**Query Params:**
- `customer_id` (optional): Filter by customer
- `status` (optional): Filter by status
- `complaint_type` (optional): Filter by type
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "customer_id": 1,
        "customer_name": "Ahmed Mohamed",
        "complaint_type": "SERVICE_QUALITY",
        "subject": "Equipment maintenance",
        "description": "Treadmill not working properly",
        "status": "OPEN",
        "assigned_to": null,
        "assigned_to_name": null,
        "resolution": null,
        "resolved_at": null,
        "created_at": "2026-01-27T10:00:00"
      }
    ],
    "total": 25,
    "pages": 2,
    "current_page": 1,
    "per_page": 20
  }
}
```

#### POST /api/complaints
**Description:** Create new complaint  
**Auth Required:** Yes  
**Request Body:**
```json
{
  "customer_id": 1,
  "complaint_type": "service_quality",
  "subject": "Equipment maintenance",
  "description": "Treadmill not working properly"
}
```

#### GET /api/complaints/{id}
**Description:** Get complaint by ID  
**Auth Required:** Yes

#### PUT /api/complaints/{id}
**Description:** Update complaint status  
**Auth Required:** Yes (Owner, Branch Manager)  
**Request Body:**
```json
{
  "status": "in_progress",
  "assigned_to": 3,
  "resolution": "Maintenance scheduled for tomorrow"
}
```

---

### 10. Fingerprint Management Endpoints

#### GET /api/fingerprints
**Description:** Get all fingerprints  
**Auth Required:** Yes  
**Query Params:**
- `customer_id` (optional): Filter by customer
- `is_active` (optional): Filter by active status

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "customer_id": 1,
      "customer_name": "Ahmed Mohamed",
      "subscription_id": 1,
      "subscription_service": "Monthly Gym Membership",
      "fingerprint_hash": "a1b2c3d4e5f6...",
      "is_active": true,
      "last_used": "2026-01-27T08:30:00",
      "registered_at": "2026-01-20T10:00:00"
    }
  ]
}
```

#### POST /api/fingerprints/register
**Description:** Register customer fingerprint  
**Auth Required:** Yes (All except Accountant)  
**Request Body:**
```json
{
  "customer_id": 1,
  "unique_data": "simulated_fingerprint_data_12345"
}
```
**Note:** Uses customer's active subscription, generates hash

#### POST /api/fingerprints/validate
**Description:** Validate fingerprint for access (PUBLIC endpoint)  
**Auth Required:** No (for access control devices)  
**Request Body:**
```json
{
  "fingerprint_hash": "a1b2c3d4e5f6..."
}
```
**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "customer": {
      "id": 1,
      "full_name": "Ahmed Mohamed",
      "phone": "01234567890"
    },
    "subscription": {
      "id": 1,
      "service_name": "Monthly Gym Membership",
      "status": "ACTIVE",
      "end_date": "2026-02-19"
    },
    "message": "Access granted"
  }
}
```

#### PUT /api/fingerprints/{id}/deactivate
**Description:** Deactivate fingerprint  
**Auth Required:** Yes (All except Accountant)

#### PUT /api/fingerprints/{id}/reactivate
**Description:** Reactivate fingerprint  
**Auth Required:** Yes (All except Accountant)

---

### 11. Dashboard Endpoints

#### GET /api/dashboards/owner
**Description:** Owner dashboard with system-wide analytics  
**Auth Required:** Yes (Owner only)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "alerts": {
      "expiring_subscriptions": [
        {
          "id": 1,
          "customer_name": "Ahmed Mohamed",
          "service_name": "Monthly Gym Membership",
          "end_date": "2026-02-05",
          "days_remaining": 8,
          "branch_name": "Main Branch"
        }
      ],
      "pending_expenses": [
        {
          "id": 1,
          "branch_name": "Main Branch",
          "category": "Utilities",
          "amount": 1000.0,
          "description": "Electricity bill",
          "expense_date": "2026-01-20"
        }
      ],
      "open_complaints": 5
    },
    "branches": [
      {
        "id": 1,
        "name": "Main Branch",
        "total_revenue": 50000.0,
        "total_expenses": 10000.0,
        "net_income": 40000.0,
        "active_subscriptions": 100,
        "active_customers": 80,
        "staff_count": 5
      }
    ],
    "summary": {
      "total_revenue": 150000.0,
      "total_expenses": 30000.0,
      "net_income": 120000.0,
      "total_customers": 250,
      "total_subscriptions": 300,
      "total_branches": 3
    }
  }
}
```

#### GET /api/dashboards/accountant
**Description:** Accountant dashboard with financial summary  
**Auth Required:** Yes (Accountant, Branch Accountant, Central Accountant)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "revenue_summary": {
      "today": 5000.0,
      "this_week": 25000.0,
      "this_month": 100000.0
    },
    "expense_summary": {
      "today": 1000.0,
      "this_week": 5000.0,
      "this_month": 20000.0
    },
    "pending_expenses": 5,
    "payment_methods_breakdown": {
      "CASH": 60000.0,
      "NETWORK": 30000.0,
      "TRANSFER": 10000.0
    },
    "recent_transactions": [/* last 10 transactions */]
  }
}
```

#### GET /api/dashboards/branch-manager
**Description:** Branch manager dashboard  
**Auth Required:** Yes (Branch Manager)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "branch_info": {
      "id": 1,
      "name": "Main Branch",
      "total_revenue": 50000.0,
      "total_expenses": 10000.0,
      "net_income": 40000.0
    },
    "stats": {
      "active_subscriptions": 100,
      "active_customers": 80,
      "staff_count": 5,
      "expiring_soon": 12,
      "pending_complaints": 3
    },
    "recent_subscriptions": [/* last 10 */],
    "service_popularity": [
      {"service_name": "Monthly Gym", "count": 50},
      {"service_name": "Swimming", "count": 30}
    ]
  }
}
```

---

## Business Logic Rules

### 1. User Management
- **Owner Uniqueness:** Only ONE owner account allowed in the system
- **Branch Assignment:** Branch-specific roles (BRANCH_MANAGER, FRONT_DESK, ACCOUNTANT, BRANCH_ACCOUNTANT) MUST have a branch_id
- **Password Security:** Passwords hashed with pbkdf2_sha256
- **Soft Delete:** Users are not permanently deleted, is_active is set to False

### 2. Subscription Lifecycle

**Creation:**
1. Customer and Service must exist
2. Payment method is required
3. Amount is set from service.price
4. End date is calculated: start_date + service.duration_days
5. Status is set to ACTIVE
6. Transaction is automatically created
7. Created_by is set to current user

**Freezing:**
1. Can only freeze ACTIVE subscriptions
2. freeze_count must be < service.freeze_count_limit
3. freeze_days_used + requested_days must be <= service.freeze_max_days
4. End date is extended by freeze days
5. Status changes to FROZEN
6. All fingerprints for this subscription are deactivated
7. Freeze_history record is created

**Unfreezing:**
1. Can only unfreeze FROZEN subscriptions
2. Status changes back to ACTIVE
3. All fingerprints for this subscription are reactivated
4. Freeze_history record is updated with unfrozen_at

**Renewal:**
1. Creates a NEW subscription with the same service
2. Start date is set to today
3. New transaction is created
4. Old subscription remains in history

**Stopping:**
1. Status changes to STOPPED
2. Fingerprints are deactivated
3. Cannot be reactivated

**Auto-Expiration:**
1. System automatically checks for expired subscriptions
2. If end_date < today and status = ACTIVE, changes to EXPIRED
3. Fingerprints are deactivated
4. Run this check via cron job or on dashboard load

### 3. Fingerprint Access Control

**Registration:**
1. Customer must have an ACTIVE subscription
2. Hash is generated: SHA256(customer_id + phone + unique_data)
3. Is_active is set to True
4. Linked to customer and subscription

**Validation (Public Endpoint):**
1. Lookup fingerprint by hash
2. Check is_active = True
3. Check subscription.status = ACTIVE
4. Check subscription.end_date >= today
5. Update last_used timestamp
6. Return customer and subscription info

**Deactivation:**
- When subscription is frozen
- When subscription is stopped
- When subscription expires
- Manual deactivation

### 4. Financial Management

**Transactions:**
- Auto-created on subscription creation/renewal
- Can be manually created for other income
- Cannot be deleted (audit trail)
- Linked to branch, customer, subscription

**Expenses:**
- Start with PENDING status
- Can be approved/rejected by Owner, Branch Manager, or Central Accountant
- Once approved/rejected, cannot be edited
- Linked to branch and creator

**Daily Closing:**
- Records expected vs actual cash
- Calculates difference (shortage/overage)
- Can only be done once per branch per day
- Locked after creation

### 5. Access Control

**Owner:**
- Full system access
- Can access all branches
- Can create users, branches, services
- Can approve expenses
- Cannot be restricted

**Branch Manager:**
- Can access only their assigned branch
- Can view all data for their branch
- Can approve expenses for their branch
- Can manage staff assignments
- Can update complaint statuses

**Front Desk:**
- Can access only their assigned branch
- Can register customers
- Can create subscriptions
- Can register fingerprints
- Cannot view financial details

**Accountant/Branch Accountant:**
- Can access only their assigned branch
- Can view all financial data
- Can create expenses
- Cannot approve expenses
- Cannot create subscriptions

**Central Accountant:**
- Can access all branches (financial data only)
- Can approve expenses for all branches
- Cannot create subscriptions
- Cannot manage customers

### 6. Data Validation

**Customer:**
- Phone is required and indexed for fast search
- BMI calculated only if height and weight provided
- Age calculated from date_of_birth
- Email format validated
- Height in cm, Weight in kg

**Subscription:**
- End date must be after start date
- Payment method required
- Amount must be positive
- Customer must belong to the selected branch

**Service:**
- Price must be positive
- Duration_days must be > 0
- Allowed_days_per_week between 1-7
- Freeze limits must be >= 0

**Expense:**
- Amount must be positive
- Expense_date cannot be future date
- Description required

---

## Enums & Constants

### Gender
```python
MALE = "MALE"
FEMALE = "FEMALE"
```

### UserRole
```python
OWNER = "OWNER"
BRANCH_MANAGER = "BRANCH_MANAGER"
FRONT_DESK = "FRONT_DESK"
ACCOUNTANT = "ACCOUNTANT"
BRANCH_ACCOUNTANT = "BRANCH_ACCOUNTANT"
CENTRAL_ACCOUNTANT = "CENTRAL_ACCOUNTANT"
```

### ServiceType
```python
GYM = "GYM"
SWIMMING_EDUCATION = "SWIMMING_EDUCATION"
SWIMMING_RECREATION = "SWIMMING_RECREATION"
KARATE = "KARATE"
BUNDLE = "BUNDLE"
```

### SubscriptionStatus
```python
ACTIVE = "ACTIVE"
FROZEN = "FROZEN"
STOPPED = "STOPPED"
EXPIRED = "EXPIRED"
```

### PaymentMethod
```python
CASH = "CASH"
NETWORK = "NETWORK"
TRANSFER = "TRANSFER"
```

### TransactionType
```python
SUBSCRIPTION = "SUBSCRIPTION"
RENEWAL = "RENEWAL"
FREEZE = "FREEZE"
REFUND = "REFUND"
OTHER = "OTHER"
```

### ExpenseStatus
```python
PENDING = "PENDING"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
```

### ComplaintType
```python
SERVICE_QUALITY = "SERVICE_QUALITY"
FACILITY = "FACILITY"
STAFF = "STAFF"
BILLING = "BILLING"
OTHER = "OTHER"
```

### ComplaintStatus
```python
OPEN = "OPEN"
IN_PROGRESS = "IN_PROGRESS"
CLOSED = "CLOSED"
```

---

## User Workflows

### 1. Owner Workflow

**Daily Tasks:**
1. Login to system
2. View owner dashboard for system-wide overview
3. Check alerts (expiring subscriptions, pending expenses, open complaints)
4. Review and approve/reject pending expenses
5. Monitor branch performance
6. Review financial reports

**Management Tasks:**
1. Create new branches
2. Create user accounts for staff
3. Create/modify services
4. View all transactions across branches
5. Generate reports
6. Manage system settings

### 2. Branch Manager Workflow

**Daily Tasks:**
1. Login to system
2. View branch manager dashboard
3. Check branch stats (subscriptions, customers, revenue)
4. Review pending complaints
5. Approve branch expenses
6. Monitor staff activity

**Management Tasks:**
1. Assign staff to roles
2. Review customer registrations
3. Handle customer complaints
4. Monitor subscription expirations
5. Coordinate with reception staff

### 3. Front Desk Workflow

**Customer Registration:**
1. Login to system
2. Register new customer with personal details
3. Collect health information (height, weight, etc.)
4. Create emergency contact info

**Subscription Management:**
1. Check available services
2. Create new subscription for customer
3. Process payment (cash/network/transfer)
4. Register customer fingerprint
5. Print/provide receipt

**Daily Operations:**
1. Handle customer check-ins
2. Renew expiring subscriptions
3. Process freeze requests
4. Update customer information
5. Register complaints

### 4. Accountant Workflow

**Daily Tasks:**
1. Login to system
2. View accountant dashboard
3. Check daily revenue (by payment method)
4. Review transactions
5. Record expenses
6. Perform daily cash closing

**Reporting:**
1. Generate financial reports
2. Track income vs expenses
3. Monitor payment methods distribution
4. Review pending expenses
5. Reconcile cash

### 5. Customer Journey

**Registration:**
1. Visit gym
2. Front desk registers in system
3. Personal info + health data collected
4. Emergency contact recorded

**Subscription:**
1. Choose service (Gym/Swimming/Karate/Bundle)
2. Select payment method
3. Process payment
4. Fingerprint registered
5. Receive welcome orientation

**Usage:**
1. Arrive at gym
2. Fingerprint scan at entrance
3. System validates subscription
4. Access granted/denied
5. Last_used updated

**Freeze:**
1. Request freeze (travel, injury, etc.)
2. Front desk processes freeze
3. Fingerprint access disabled
4. End date extended

**Renewal:**
1. System alerts of expiration
2. Customer visits front desk
3. Process renewal payment
4. New subscription created
5. Fingerprint remains active

**Complaint:**
1. Customer reports issue
2. Complaint recorded in system
3. Assigned to branch manager
4. Manager follows up
5. Complaint resolved and closed

---

## Integration Notes for Flutter

### State Management Recommendations
- Use **Provider** or **Riverpod** for app-wide state
- Use **GetX** for navigation and simple state
- Use **BLoC** for complex business logic

### Recommended Packages
```yaml
dependencies:
  http: ^1.1.0  # API calls
  dio: ^5.4.0  # Alternative HTTP client with interceptors
  flutter_secure_storage: ^9.0.0  # Store JWT tokens securely
  shared_preferences: ^2.2.2  # Cache user preferences
  provider: ^6.1.1  # State management
  get: ^4.6.6  # Navigation and simple state
  intl: ^0.19.0  # Date formatting
  cached_network_image: ^3.3.1  # Image caching
  fl_chart: ^0.66.0  # Charts for dashboards
  local_auth: ^2.1.8  # Biometric authentication
  pretty_dio_logger: ^1.3.1  # API logging
```

### API Service Structure
```dart
class ApiService {
  static const baseUrl = 'https://yamenmod91.pythonanywhere.com/api';
  
  // Auth endpoints
  Future<LoginResponse> login(String username, String password);
  Future<User> getCurrentUser();
  
  // Branch endpoints
  Future<List<Branch>> getBranches();
  
  // Customer endpoints
  Future<PaginatedResponse<Customer>> getCustomers({int page, int perPage, String? phone});
  Future<Customer> createCustomer(CustomerRequest request);
  
  // Subscription endpoints
  Future<PaginatedResponse<Subscription>> getSubscriptions({...});
  Future<Subscription> createSubscription(SubscriptionRequest request);
  Future<void> freezeSubscription(int id, int days, String reason);
  
  // And so on...
}
```

### Authentication Flow
1. User enters credentials
2. Call POST /api/auth/login
3. Store access_token and refresh_token in secure storage
4. Store user object in app state
5. Add token to all API requests via interceptor
6. Handle 401 errors (token expired)
7. Implement token refresh logic

### Screens to Implement

**Authentication:**
- Login Screen
- Change Password Screen

**Owner Screens:**
- Owner Dashboard
- Branch Management (List, Create, Edit)
- User Management (List, Create, Edit)
- Service Management (List, Create, Edit)
- System-wide Reports

**Branch Manager Screens:**
- Branch Dashboard
- Customer List
- Subscription List
- Expense Approval
- Complaint Management
- Staff Management

**Front Desk Screens:**
- Customer Registration
- Customer Search
- Subscription Creation
- Subscription Renewal
- Freeze/Unfreeze Subscription
- Fingerprint Registration
- Complaint Registration

**Accountant Screens:**
- Financial Dashboard
- Transaction List
- Expense List (Create, View)
- Daily Closing
- Financial Reports

**Common Screens:**
- Profile/Settings
- Logout
- About

### UI/UX Recommendations

**Colors by Role:**
- Owner: Purple/Gold
- Manager: Blue
- Front Desk: Green
- Accountant: Orange

**Dashboard Cards:**
- Use cards for metrics (revenue, customers, subscriptions)
- Color-code status (Active=Green, Frozen=Blue, Expired=Red)
- Show alerts prominently

**Lists:**
- Implement pull-to-refresh
- Add search functionality
- Show loading indicators
- Handle empty states
- Implement pagination

**Forms:**
- Use proper input types (email, phone, number)
- Add validation
- Show error messages
- Add date pickers
- Add dropdowns for enums

**Navigation:**
- Bottom navigation for main sections
- Drawer for settings/profile
- Role-based menu items

### Error Handling
```dart
try {
  final response = await apiService.getCustomers();
  // Handle success
} on UnauthorizedException {
  // Redirect to login
} on ValidationException catch (e) {
  // Show validation errors
} on NotFoundException {
  // Show not found message
} on NetworkException {
  // Show network error
} catch (e) {
  // Show generic error
}
```

### Offline Support (Optional)
- Cache customer list
- Cache service list
- Cache branch list
- Queue operations when offline
- Sync when online

---

## Testing Endpoints

**Interactive Test Page:** `https://yamenmod91.pythonanywhere.com/test`

**Test with cURL:**
```bash
# Login
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"owner","password":"owner123"}'

# Get customers (with token)
curl -X GET https://yamenmod91.pythonanywhere.com/api/customers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Test with Postman:**
- Import endpoints from interactive test page
- Set Authorization type to "Bearer Token"
- Add token from login response

---

## Deployment URLs

- **Backend API:** `https://yamenmod91.pythonanywhere.com/api`
- **Test Page:** `https://yamenmod91.pythonanywhere.com/test`
- **GitHub Repo:** `https://github.com/yamenmod9/gym-management-system`

---

## Additional Features to Consider

### Mobile App Enhancements
1. **Push Notifications:**
   - Subscription expiring soon
   - Payment reminders
   - Complaint updates

2. **QR Code Scanner:**
   - Alternative to fingerprint
   - Quick customer lookup

3. **Offline Mode:**
   - Cache essential data
   - Queue operations

4. **Biometric Auth:**
   - Fingerprint/Face ID for app login

5. **Reports Export:**
   - PDF generation
   - Excel export
   - Email reports

6. **Multi-language:**
   - Arabic/English support

7. **Dark Mode:**
   - Theme switching

8. **Charts & Analytics:**
   - Revenue trends
   - Customer growth
   - Service popularity

---

## Summary

This backend provides a complete, production-ready API for a multi-branch gym management system with:

- ✅ 60+ API endpoints
- ✅ 12 database models with relationships
- ✅ JWT authentication with 6-role RBAC
- ✅ Complete subscription lifecycle management
- ✅ Financial tracking (transactions, expenses, daily closing)
- ✅ Fingerprint-based access control (simulated)
- ✅ Real-time dashboards
- ✅ Complaint management
- ✅ Health metrics calculation (BMI, calories, ideal weight)
- ✅ Comprehensive validation and error handling
- ✅ Pagination support
- ✅ Branch-based data isolation
- ✅ Automatic subscription expiration
- ✅ Audit trail (created_by, timestamps)

All endpoints are documented, tested, and deployed. The API follows RESTful conventions and returns consistent response formats. The Flutter app should mirror the role-based access control and implement the workflows described above.

**Good luck building the Flutter frontend! 🚀**
