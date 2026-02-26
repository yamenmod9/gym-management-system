# 🚀 CLAUDE SONNET 4.5 - COMPLETE BACKEND IMPLEMENTATION PROMPT
**Date:** February 16, 2026  
**Gym Management System - Backend Implementation**

---

## 📋 OVERVIEW

This prompt contains everything needed to implement a complete backend API for a Gym Management System with two mobile apps:
1. **Staff App** (Flutter) - For owners, managers, accountants, and receptionists
2. **Client App** (Flutter) - For gym customers

---

## 🎯 YOUR TASK

Implement a complete Flask/FastAPI Python backend with the following:

### 1. **67 API Endpoints** (See detailed specification below)
   - 55 endpoints for Staff App
   - 12 endpoints for Client App

### 2. **Complete Seed Data** (See detailed specification below)
   - 3 branches
   - 10 services
   - 15 staff accounts
   - 150 customers
   - 150 subscriptions (120 active, 30 expired)
   - 2,000 attendance records
   - 150 payment records
   - 50 expense records (optional)

### 3. **Database Models**
   - Branches
   - Staff
   - Customers
   - Services
   - Subscriptions
   - Attendance
   - Payments
   - Expenses (optional)
   - Settings

---

## 📖 DETAILED SPECIFICATIONS

### Part 1: API Endpoints Specification
**File:** `COMPLETE_API_ENDPOINTS_SPECIFICATION_FEB16.md`

This document contains:
- ✅ All 67 endpoint specifications with request/response examples
- ✅ Authentication requirements
- ✅ Query parameters and filtering
- ✅ Error responses
- ✅ Pagination details
- ✅ Test credentials
- ✅ Priority levels (critical vs optional endpoints)

**Key Sections:**
1. Staff App Endpoints (55 total)
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

2. Client App Endpoints (12 total)
   - Authentication (3)
   - Profile Management (3)
   - Subscription (3)
   - Attendance (2)
   - Complaints (1)

### Part 2: Seed Data Specification
**File:** `BACKEND_SEED_DATA_COMPLETE_SPECIFICATION_FEB16.md`

This document contains:
- ✅ Complete data structure for all seed data
- ✅ Sample records with realistic values
- ✅ Distribution guidelines (branches, types, statuses)
- ✅ Helper functions for data generation
- ✅ Calculated fields (BMI, BMR, display labels)
- ✅ Unique constraint requirements

**What to Generate:**
- 3 branches (Dragon Club, Tigers Gym, Lions Fitness)
- 10 services (5 gym, 3 training, 2 special)
- 15 staff (2 owners, 3 managers, 4 accountants, 6 receptionists)
- 150 customers (distributed across branches)
- 150 subscriptions (120 active, 30 expired)
- 2,000 attendance records (last 30 days)
- 150 payments
- 50 expenses (optional)

---

## 🔥 CRITICAL ISSUES TO FIX

### Issue 1: QR Check-In Returns 404 Error
**Problem:** `POST /api/attendance` endpoint is missing  
**Status:** 🔴 CRITICAL - Blocking receptionist operations

**Required Response:**
```json
{
  "success": true,
  "message": "Check-in recorded successfully",
  "data": {
    "attendance_id": 789,
    "customer_name": "Adel Saad",
    "check_in_time": "2026-02-16T10:30:00Z",
    "coins_deducted": 1,
    "remaining_coins": 24
  }
}
```

### Issue 2: Subscription Display Data Missing
**Problem:** Client dashboard shows wrong metrics (e.g., "25 days" instead of "25 coins")  
**Status:** 🔴 CRITICAL - Poor UX

**Required Fields in Subscription Response:**
```json
{
  "subscription_type": "coins",
  "remaining_coins": 25,
  "display_metric": "coins",
  "display_value": 25,
  "display_label": "25 Coins"
}
```

**Display Logic:**
- **Coins:** display_label = "{remaining_coins} Coins"
- **Time-based:** display_label = "{months} months, {days} days"
- **Sessions:** display_label = "{remaining_sessions} Sessions"
- **Training:** display_label = "{remaining_sessions} Training Sessions"

### Issue 3: Subscriptions Don't Auto-Expire
**Problem:** Expired subscriptions stay active  
**Status:** 🟡 IMPORTANT

**Required Logic:**
- Time-based: Expire when `end_date` < current_date
- Coin-based: Expire when `remaining_coins` = 0
- Session-based: Expire when `remaining_sessions` = 0
- Implement cron job: `POST /api/subscriptions/expire-old`

### Issue 4: Branch Validation Error
**Problem:** Error message "Cannot create subscription for another branch" is confusing  
**Status:** 🟡 IMPORTANT

**Current Issue:**
```json
{
  "error": "Cannot create subscription for another branch",
  "success": false
}
```

**Required Fix:**
```json
{
  "success": false,
  "error": "Cannot create subscription for another branch. Customer is in branch 2 (Tigers Gym), but you are trying to create subscription for branch 1 (Dragon Club)"
}
```

### Issue 5: Temporary Password Not Showing
**Problem:** Temporary password shows "Not Set" instead of actual password  
**Status:** 🔴 CRITICAL

**Required:**
- Store `temp_password` in database (plain text, 6 chars like "AB12CD")
- Return `temp_password` in customer details response
- Show to receptionist when viewing customer

### Issue 6: Dashboard Data Shows 0
**Problem:** Owner/Manager dashboards show all zeros despite having data  
**Status:** 🔴 CRITICAL

**Required:**
- `GET /api/dashboard/owner` must return actual counts and revenue
- `GET /api/dashboard/manager` must return branch-specific data
- `GET /api/dashboard/customers/count` must return real customer count
- `GET /api/dashboard/subscriptions/active-count` must return real active count

---

## 📊 DATABASE SCHEMA REQUIREMENTS

### Customers Table (Extended)
```python
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    national_id = db.Column(db.String(14), unique=True)
    password_hash = db.Column(db.String(255))
    temp_password = db.Column(db.String(6))  # IMPORTANT: Plain text for display
    password_changed = db.Column(db.Boolean, default=False)
    qr_code = db.Column(db.String(50), unique=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)
    bmi_category = db.Column(db.String(20))
    bmr = db.Column(db.Float)
    daily_calories = db.Column(db.Float)
    ideal_weight = db.Column(db.Float)
    health_notes = db.Column(db.Text)
    address = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

### Subscriptions Table (Extended)
```python
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    subscription_type = db.Column(db.String(20))  # coins, time_based, sessions, training
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    validity_months = db.Column(db.Integer)
    status = db.Column(db.String(20), default='active')  # active, expired, frozen, cancelled
    remaining_coins = db.Column(db.Integer)
    total_coins = db.Column(db.Integer)
    remaining_sessions = db.Column(db.Integer)
    total_sessions = db.Column(db.Integer)
    amount = db.Column(db.Float)
    payment_method = db.Column(db.String(20))
    discount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # IMPORTANT: Display fields
    @property
    def display_metric(self):
        if self.subscription_type == 'coins':
            return 'coins'
        elif self.subscription_type == 'time_based':
            return 'time'
        elif self.subscription_type == 'sessions':
            return 'sessions'
        elif self.subscription_type == 'training':
            return 'training'
    
    @property
    def display_value(self):
        if self.subscription_type == 'coins':
            return self.remaining_coins
        elif self.subscription_type == 'time_based':
            return (self.end_date - datetime.now().date()).days
        elif self.subscription_type in ['sessions', 'training']:
            return self.remaining_sessions
    
    @property
    def display_label(self):
        if self.subscription_type == 'coins':
            return f"{self.remaining_coins} Coins"
        elif self.subscription_type == 'time_based':
            days = (self.end_date - datetime.now().date()).days
            months = days // 30
            remaining_days = days % 30
            if months > 0:
                return f"{months} months, {remaining_days} days"
            return f"{days} days"
        elif self.subscription_type == 'sessions':
            return f"{self.remaining_sessions} Sessions"
        elif self.subscription_type == 'training':
            return f"{self.remaining_sessions} Training Sessions"
```

### Attendance Table (NEW - CRITICAL)
```python
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50))  # check_in, check_in_with_coin, check_in_with_session
    coins_deducted = db.Column(db.Integer, default=0)
    sessions_deducted = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🔑 TEST CREDENTIALS

### Staff App
```
# Owner
Phone: 01012345678
Password: owner123

# Manager (Dragon Club)
Phone: 01087654321
Password: manager123

# Accountant (Dragon Club)
Phone: 01054321098
Password: accountant123

# Receptionist (Dragon Club)
Phone: 01045678901
Password: receptionist123
```

### Client App
```
# Customer 1 (Password changed)
Phone: 01077827638
Temp Password: RX04AF
Name: Mohamed Salem

# Customer 61 (Password NOT changed)
Phone: 01025867870
Temp Password: AB12CD
Name: Adel Saad
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Phase 1: Critical Endpoints (Priority 1)
- [ ] `POST /api/staff/auth/login` - Staff login
- [ ] `POST /api/client/auth/login` - Client login
- [ ] `POST /api/client/auth/change-password` - Change password
- [ ] `POST /api/attendance` - Record check-in (QR scan) **MISSING**
- [ ] `GET /api/dashboard/owner` - Owner dashboard **RETURNS ZEROS**
- [ ] `GET /api/dashboard/manager` - Manager dashboard **RETURNS ZEROS**
- [ ] `GET /api/customers` - List customers
- [ ] `GET /api/customers/{id}` - Customer details with temp_password
- [ ] `POST /api/customers` - Register customer
- [ ] `GET /api/subscriptions` - List subscriptions
- [ ] `POST /api/subscriptions/activate` - Activate subscription
- [ ] `GET /api/client/subscription` - Get subscription with display data
- [ ] `GET /api/branches` - List branches **EMPTY RESPONSE**
- [ ] `GET /api/staff` - List staff **EMPTY RESPONSE**

### Phase 2: Important Endpoints
- [ ] `POST /api/subscriptions/expire-old` - Expire old subscriptions
- [ ] `POST /api/subscriptions/{id}/deduct-coin` - Deduct coin
- [ ] `POST /api/subscriptions/{id}/deduct-session` - Deduct session
- [ ] `GET /api/attendance` - Attendance history
- [ ] `GET /api/payments` - Payment list
- [ ] `GET /api/dashboard/customers/count` - Customer count
- [ ] `GET /api/dashboard/subscriptions/active-count` - Active count

### Phase 3: Seed Data
- [ ] Create 3 branches
- [ ] Create 10 services
- [ ] Create 15 staff accounts
- [ ] Create 150 customers with temp_password
- [ ] Create 150 subscriptions with display fields
- [ ] Create 2,000 attendance records
- [ ] Create 150 payments

---

## 🎯 SUCCESS CRITERIA

### 1. QR Check-In Works
- ✅ Receptionist scans QR code
- ✅ System finds customer and active subscription
- ✅ Deducts coin/session if needed
- ✅ Records attendance
- ✅ Returns success message

### 2. Client Dashboard Shows Correct Data
- ✅ Coins subscription shows "25 Coins"
- ✅ Time subscription shows "1 month, 14 days"
- ✅ Sessions subscription shows "8 Sessions"
- ✅ Training subscription shows "7 Training Sessions"

### 3. Staff Dashboard Shows Real Data
- ✅ Owner sees total customers: 150
- ✅ Owner sees total revenue: >0
- ✅ Manager sees branch customers: >0
- ✅ Active subscriptions count: 120

### 4. Temporary Password Visible
- ✅ Receptionist can see temp_password in customer details
- ✅ Shows "AB12CD" format
- ✅ Password_changed flag works correctly

### 5. Subscriptions Auto-Expire
- ✅ Time-based subscriptions expire after end_date
- ✅ Coin subscriptions expire when coins = 0
- ✅ Session subscriptions expire when sessions = 0

---

## 📁 DELIVERABLES

Please provide:

1. **Complete Backend Code**
   - Flask/FastAPI application
   - All 67 endpoints implemented
   - Database models
   - Authentication/authorization
   - Error handling

2. **seed.py File**
   - Complete seed data generation
   - All 150 customers
   - All 150 subscriptions
   - All attendance records
   - Test accounts

3. **requirements.txt**
   - All dependencies

4. **README.md**
   - Setup instructions
   - How to run seed data
   - How to test endpoints

5. **API Testing Collection** (Optional)
   - Postman/Thunder Client collection
   - Sample requests for all endpoints

---

## 🚨 IMPORTANT NOTES

1. **Base URL:** `https://yamenmod91.pythonanywhere.com/api`

2. **Authentication:**
   - Use JWT tokens
   - Include customer/staff ID, role, branch_id in token
   - Token expiry: 30 days

3. **Branch Validation:**
   - Staff can only access their branch data
   - Exception: Owners can access all branches
   - Return clear error messages for branch mismatches

4. **Calculated Fields:**
   - Auto-calculate BMI, BMR, daily_calories on customer create/update
   - Auto-calculate display_metric, display_value, display_label on subscription fetch

5. **QR Code Format:**
   - Format: `CUST-{customer_id:03d}-{BRANCH_PREFIX}`
   - Example: `CUST-001-DRAGON`

6. **Temporary Password Format:**
   - 6 random alphanumeric characters
   - Example: "AB12CD", "RX04AF", "SI19IC"
   - Store in plain text (for display to receptionist)

7. **Subscription Expiration:**
   - Run expiration check on every subscription fetch
   - Implement cron job endpoint for scheduled checks

---

## 📚 REFERENCE DOCUMENTS

1. **Complete API Endpoints:** `COMPLETE_API_ENDPOINTS_SPECIFICATION_FEB16.md`
2. **Complete Seed Data:** `BACKEND_SEED_DATA_COMPLETE_SPECIFICATION_FEB16.md`
3. **QR & Display Fix:** `QR_CHECKIN_AND_SUBSCRIPTION_DISPLAY_FIX_FEB16.md`

---

## 🎬 START HERE

1. Read both specification documents carefully
2. Set up Flask/FastAPI project structure
3. Create database models
4. Implement authentication endpoints first
5. Implement critical endpoints (Phase 1)
6. Create seed.py with all data
7. Test critical flows (login, check-in, dashboard)
8. Implement remaining endpoints
9. Test with Flutter apps

---

**Priority:** 🔴 CRITICAL  
**Estimated Time:** 8-12 hours for complete implementation  
**Status:** Ready for Implementation

---

**Good luck! 🚀**

