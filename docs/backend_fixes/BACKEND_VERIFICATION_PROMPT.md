# 🔍 BACKEND VERIFICATION PROMPT FOR CLAUDE SONNET

## 📋 Overview
This document outlines all backend requirements for the Gym Management System mobile apps (Client App & Staff App). Please verify that all these endpoints exist and function correctly with the expected request/response formats.

---

## 🎯 Critical Client App Features to Verify

### 1. Client Authentication & Profile

#### POST /api/client/login
**Purpose:** Authenticate client with phone/email and password

**Request:**
```json
{
  "identifier": "01234567890",
  "password": "temporary123"
}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "password_changed": true,
    "customer": {
      "id": 151,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "branch_id": 1,
      "is_active": true,
      "qr_code": "GYM-151"
    }
  }
}
```

**IMPORTANT:** 
- Must include `password_changed` boolean
- Must include customer/client data in response
- If first login, `password_changed` should be `false`

---

#### GET /api/client/me
**Purpose:** Get current client profile including active subscription

**Headers:**
```
Authorization: Bearer {client_jwt_token}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "date_of_birth": "1995-01-15",
    "gender": "male",
    "height": 1.75,
    "weight": 75.0,
    "branch_id": 1,
    "branch_name": "Main Branch",
    "qr_code": "GYM-151",
    "qr_image_url": "/api/client/qr-image",
    "is_active": true,
    "password_changed": true,
    "active_subscription": {
      "id": 127,
      "service_name": "Monthly Gym Membership",
      "service_type": "gym",
      "start_date": "2026-02-13",
      "end_date": "2026-03-15",
      "status": "active",
      "coins": 20,
      "remaining_coins": 18,
      "can_access": true,
      "is_expired": false,
      "freeze_count": 0,
      "total_frozen_days": 0,
      "branch_id": 1,
      "branch_name": "Main Branch"
    }
  }
}
```

**CRITICAL FIELDS:**
- `active_subscription` object (null if no active subscription)
- `service_name` or `service_type` (at least one must exist)
- `start_date` and `end_date` (can also be `expiry_date`)
- `status` must be string: "active", "frozen", "expired", or "stopped"
- `coins` or `remaining_coins` for coin-based subscriptions

---

### 2. Client Subscription Management

#### GET /api/client/subscription/history
**Purpose:** Get client's subscription history and entry logs

**Headers:**
```
Authorization: Bearer {client_jwt_token}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "entries": [
      {
        "id": 1234,
        "entry_date": "2026-02-14T10:30:00",
        "service_used": "Gym Entry",
        "coins_used": 1,
        "remaining_coins": 19,
        "branch_name": "Main Branch"
      },
      {
        "id": 1233,
        "entry_date": "2026-02-13T18:45:00",
        "service_used": "Gym Entry",
        "coins_used": 1,
        "remaining_coins": 20,
        "branch_name": "Main Branch"
      }
    ],
    "subscription_history": [
      {
        "id": 127,
        "service_name": "Monthly Gym Membership",
        "start_date": "2026-02-13",
        "end_date": "2026-03-15",
        "status": "active",
        "initial_coins": 20,
        "remaining_coins": 19
      },
      {
        "id": 126,
        "service_name": "Monthly Gym Membership",
        "start_date": "2026-01-13",
        "end_date": "2026-02-13",
        "status": "expired",
        "initial_coins": 20,
        "remaining_coins": 0
      }
    ]
  }
}
```

---

### 3. Client QR Code System

#### GET /api/client/qr-code
**Purpose:** Get client's unique QR code for gym entry

**Headers:**
```
Authorization: Bearer {client_jwt_token}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "qr_code": "GYM-151",
    "qr_image_url": "/api/client/qr-image",
    "qr_data": "GYM-151-20260214",
    "expires_at": "2026-02-14T23:59:59"
  }
}
```

---

#### POST /api/client/qr-code/refresh
**Purpose:** Refresh QR code (for security, expires after certain time)

**Headers:**
```
Authorization: Bearer {client_jwt_token}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "QR code refreshed successfully",
  "data": {
    "qr_code": "GYM-151",
    "qr_data": "GYM-151-20260214-v2",
    "expires_at": "2026-02-14T23:59:59"
  }
}
```

---

#### POST /api/staff/qr-scan
**Purpose:** Staff scans client QR code to record entry

**Headers:**
```
Authorization: Bearer {staff_jwt_token}
```

**Request:**
```json
{
  "qr_code": "GYM-151",
  "entry_type": "gym",
  "branch_id": 1
}
```

**Expected Response (Success):**
```json
{
  "success": true,
  "message": "Entry recorded successfully",
  "data": {
    "customer_name": "Ahmed Hassan",
    "service_used": "Gym Entry",
    "coins_used": 1,
    "remaining_coins": 19,
    "entry_time": "2026-02-14T10:30:00"
  }
}
```

**Expected Response (Errors):**
```json
{
  "success": false,
  "message": "No active subscription"
}
```

```json
{
  "success": false,
  "message": "Insufficient coins"
}
```

```json
{
  "success": false,
  "message": "Subscription is frozen"
}
```

```json
{
  "success": false,
  "message": "Wrong branch - customer belongs to Branch A"
}
```

---

### 4. Client Password Management

#### POST /api/client/change-password
**Purpose:** Change client password

**Headers:**
```
Authorization: Bearer {client_jwt_token}
```

**Request:**
```json
{
  "current_password": "temporary123",
  "new_password": "mySecure123!",
  "confirm_password": "mySecure123!"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## 🏢 Critical Staff/Reception App Features to Verify

### 5. Staff Authentication

#### POST /api/staff/login
**Purpose:** Authenticate staff member

**Request:**
```json
{
  "identifier": "reception@gym.com",
  "password": "staff123"
}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "staff": {
      "id": 5,
      "username": "reception1",
      "email": "reception@gym.com",
      "role": "reception",
      "branch_id": 1,
      "branch_name": "Main Branch"
    }
  }
}
```

---

### 6. Customer Management (Branch-Filtered)

#### GET /api/staff/customers
**Purpose:** Get all customers for staff member's branch ONLY

**Headers:**
```
Authorization: Bearer {staff_jwt_token}
```

**Query Parameters:**
```
?page=1&limit=20&search=ahmed&status=active
```

**Expected Response:**
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
        "branch_id": 1,
        "branch_name": "Main Branch",
        "is_active": true,
        "active_subscription": {
          "service_name": "Monthly Gym",
          "status": "active",
          "end_date": "2026-03-15"
        },
        "created_at": "2026-01-15T10:00:00"
      }
    ],
    "total": 45,
    "page": 1,
    "limit": 20,
    "total_pages": 3
  }
}
```

**CRITICAL:** Must filter by `branch_id` of the authenticated staff member automatically on backend. Receptionists should ONLY see customers from their own branch.

---

#### POST /api/staff/customers
**Purpose:** Register new customer (must be assigned to staff's branch)

**Headers:**
```
Authorization: Bearer {staff_jwt_token}
```

**Request:**
```json
{
  "full_name": "Ahmed Hassan",
  "phone": "01234567890",
  "email": "ahmed@example.com",
  "date_of_birth": "1995-01-15",
  "gender": "male",
  "height": 1.75,
  "weight": 75.0,
  "password": "temporary123",
  "branch_id": 1
}
```

**CRITICAL:** Backend must validate that `branch_id` matches the staff member's `branch_id`. Receptionists should NOT be able to register customers for other branches.

**Expected Response:**
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "id": 152,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "qr_code": "GYM-152",
    "temporary_password": "temporary123",
    "branch_id": 1
  }
}
```

---

### 7. Subscription Operations (Branch-Filtered)

#### POST /api/staff/subscriptions/activate
**Purpose:** Activate subscription for customer

**Headers:**
```
Authorization: Bearer {staff_jwt_token}
```

**Request:**
```json
{
  "customer_id": 151,
  "service_id": 1,
  "branch_id": 1,
  "amount": 500.0,
  "payment_method": "cash",
  "subscription_type": "coins",
  "coins": 20,
  "validity_months": 1
}
```

**CRITICAL:** 
- Backend must validate customer belongs to staff's branch
- Backend must validate service is available at that branch
- Update active_subscriptions count for that branch

**Expected Response:**
```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 127,
    "customer_name": "Ahmed Hassan",
    "service_name": "Monthly Gym Membership",
    "start_date": "2026-02-14",
    "end_date": "2026-03-14",
    "coins": 20,
    "amount_paid": 500.0
  }
}
```

---

### 8. Dashboard Statistics (Branch-Filtered)

#### GET /api/staff/dashboard/stats
**Purpose:** Get dashboard statistics for staff's branch ONLY

**Headers:**
```
Authorization: Bearer {staff_jwt_token}
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "total_customers": 45,
    "active_subscriptions": 38,
    "new_today": 3,
    "expiring_soon": 7,
    "revenue_today": 2500.0,
    "revenue_this_month": 45000.0,
    "branch_id": 1,
    "branch_name": "Main Branch"
  }
}
```

**CRITICAL:** All statistics must be filtered by staff member's `branch_id`.

---

## 🔐 Security Requirements

### Branch Isolation
1. **Receptionists:**
   - Can ONLY see customers from their branch
   - Can ONLY register customers to their branch
   - Can ONLY activate subscriptions for their branch customers
   - Dashboard stats show ONLY their branch

2. **Backend Validation:**
   - Every staff API call must include branch check
   - Use JWT token to get staff's branch_id
   - Automatically filter all queries by branch_id
   - Return 403 Forbidden if trying to access other branch data

### Example Middleware (Pseudo-code):
```python
def verify_branch_access(staff_user, customer_id):
    customer = get_customer(customer_id)
    if customer.branch_id != staff_user.branch_id:
        raise PermissionDenied("Cannot access customer from different branch")
    return True
```

---

## 📝 Testing Checklist for Backend Developer

### Client App Tests:
- [ ] Login returns `password_changed` field
- [ ] Login includes customer/client data
- [ ] GET /api/client/me includes `active_subscription` object
- [ ] Subscription data includes all required fields
- [ ] QR code endpoints work and return proper data
- [ ] Entry history endpoint returns past entries
- [ ] Password change endpoint works

### Staff App Tests:
- [ ] Staff login returns branch information
- [ ] GET /api/staff/customers filters by staff's branch automatically
- [ ] POST /api/staff/customers validates branch_id
- [ ] Cannot register customer to different branch
- [ ] Dashboard stats show only staff's branch data
- [ ] Active subscriptions count updates after activation
- [ ] QR scan validates branch access

### Branch Isolation Tests:
- [ ] Receptionist A (Branch 1) cannot see customers from Branch 2
- [ ] Receptionist A cannot register customer to Branch 2
- [ ] Receptionist A cannot activate subscription for Branch 2 customer
- [ ] Dashboard stats are correctly filtered by branch

---

## 🚨 Common Issues to Fix

### Issue 1: No password_changed field in login response
**Impact:** Client app cannot determine if user needs password change  
**Fix:** Add `password_changed` boolean to login response

### Issue 2: No active_subscription in profile response
**Impact:** Client dashboard shows 404 error  
**Fix:** Add `active_subscription` object to GET /api/client/me response (null if no subscription)

### Issue 3: No branch filtering on staff endpoints
**Impact:** Receptionists can see/modify customers from other branches  
**Fix:** Add automatic branch filtering to all staff customer queries

### Issue 4: Active subscription count always 0
**Impact:** Dashboard shows incorrect statistics  
**Fix:** Count subscriptions with status='active' for the branch

### Issue 5: Subscription model mismatch
**Impact:** Type errors when parsing subscription data  
**Fix:** Ensure response includes `service_name` or `service_type`, `start_date`, `end_date`, `status`, `coins`

---

## 📤 Response Format Standardization

All API responses should follow this format:

**Success:**
```json
{
  "success": true,
  "data": { /* actual data */ },
  "message": "Optional success message"
}
```

**Error:**
```json
{
  "success": false,
  "message": "Error description",
  "errors": { /* field-specific errors if applicable */ }
}
```

---

## 🎯 Priority Fixes

### High Priority (Blocking Features):
1. ✅ Add `password_changed` to login response
2. ✅ Add `active_subscription` to profile endpoint
3. ✅ Implement branch filtering for staff endpoints
4. ✅ Fix subscription response format (include all required fields)

### Medium Priority (Important):
5. ✅ Implement QR scan with entry recording
6. ✅ Add entry history endpoint
7. ✅ Fix dashboard stats to show actual counts

### Low Priority (Nice to Have):
8. ⏳ QR code refresh endpoint
9. ⏳ Advanced filtering on customer list
10. ⏳ Export reports by branch

---

## 📞 Questions for Backend Team

1. Is JWT token being used for authentication?
2. Does JWT token include `branch_id` for staff users?
3. Are all staff endpoints currently filtering by branch?
4. Does the subscription activation update the dashboard counts?
5. Is there a QR scan endpoint implemented?
6. How are entry logs being recorded?

---

**Date:** February 14, 2026  
**Frontend Version:** v2.0  
**Status:** Ready for Backend Verification


