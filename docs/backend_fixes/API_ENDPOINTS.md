# 🌐 GYM MANAGEMENT SYSTEM - API DOCUMENTATION

**Base URL:** `https://yourusername.pythonanywhere.com`  
**Version:** 1.0  
**Date:** February 17, 2026

---

## 🔐 AUTHENTICATION

All endpoints (except login) require JWT token in header:
```
Authorization: Bearer {token}
```

---

## 📱 CLIENT APP ENDPOINTS

### 1. Login

```http
POST /api/auth/client/login
Content-Type: application/json

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
    "token": "eyJhbGc...",
    "customer": {
      "id": 115,
      "full_name": "Mohamed Salem",
      "phone": "01077827638",
      "branch_id": 1,
      "qr_code": "GYM-115"
    },
    "password_changed": false
  }
}
```

---

### 2. Change Password

```http
POST /api/auth/client/change-password
Authorization: Bearer {token}
Content-Type: application/json

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

---

### 3. Get Customer Profile

```http
GET /api/customers/{customer_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 115,
    "full_name": "Mohamed Salem",
    "phone": "01077827638",
    "email": "customer@example.com",
    "qr_code": "GYM-115",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "bmi": 26.1,
    "weight": 80,
    "height": 175
  }
}
```

---

### 4. Get Customer Subscriptions

```http
GET /api/customers/{customer_id}/subscriptions
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 124,
        "status": "active",
        "subscription_type": "coins",
        "coins": 50,
        "remaining_coins": 35,
        "start_date": "2026-02-16",
        "end_date": null,
        "is_expired": false
      }
    ]
  }
}
```

---

## 🏢 STAFF APP ENDPOINTS

### 5. Staff Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "phone": "01511111111",
  "password": "reception123"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGc...",
    "user": {
      "id": 5,
      "full_name": "Reception One",
      "phone": "01511111111",
      "role": "front_desk",
      "branch_id": 1
    }
  }
}
```

---

### 6. Register Customer

```http
POST /api/customers/register
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Ahmed Hassan",
  "phone": "01234567890",
  "email": "ahmed@example.com",
  "gender": "male",
  "age": 25,
  "weight": 75,
  "height": 175,
  "branch_id": 1
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "qr_code": "GYM-151",
    "branch_id": 1,
    "client_credentials": {
      "phone": "01234567890",
      "temporary_password": "AB12CD",
      "note": "Give these credentials to the client"
    }
  }
}
```

---

### 7. Get Customers by Branch

```http
GET /api/customers?branch_id={branch_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 115,
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "branch_id": 1,
        "is_active": true
      }
    ]
  }
}
```

---

### 8. Activate Subscription

```http
POST /api/subscriptions/activate
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 115,
  "service_id": 1,
  "amount": 100.0,
  "payment_method": "cash"
}
```

**Note:** `branch_id` is NOT needed - uses customer's branch automatically

**Response (201):**
```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "id": 125,
    "customer_id": 115,
    "service_id": 1,
    "status": "active",
    "start_date": "2026-02-17",
    "coins": 50,
    "remaining_coins": 50
  }
}
```

---

### 9. Check-in Customer

```http
POST /api/checkins
Authorization: Bearer {token}
Content-Type: application/json

{
  "qr_code": "GYM-115"
}
```

**Note:** 
- Only `qr_code` is needed
- `customer_id` and `branch_id` extracted automatically
- Supports formats: `GYM-115` or `customer_id:115`

**Response (201):**
```json
{
  "success": true,
  "message": "Check-in recorded successfully",
  "data": {
    "id": 450,
    "customer_id": 115,
    "customer_name": "Mohamed Salem",
    "check_in_time": "2026-02-17T14:30:00",
    "remaining_coins": 34
  }
}
```

---

### 10. Regenerate QR Code

```http
POST /api/customers/{customer_id}/regenerate-qr
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "message": "QR code regenerated successfully",
  "data": {
    "qr_code": "GYM-115"
  }
}
```

---

## 🎯 COMMON PATTERNS

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## 📊 SUBSCRIPTION TYPES

1. **Coins:** Fixed number of visits (e.g., 50 coins)
   - `subscription_type`: "coins"
   - Has `coins` and `remaining_coins`
   - No expiry date (unlimited time)

2. **Time-based:** Monthly access (e.g., 1 month, 3 months)
   - `subscription_type`: "time_based"
   - Has `end_date`
   - Unlimited visits during period

3. **Personal Training:** Sessions with trainer
   - `subscription_type`: "personal_training"
   - Has `coins` (sessions) and `end_date`

---

## 🔒 ROLE PERMISSIONS

**Owner:**
- All access
- Any branch

**Manager:**
- Branch-specific access
- Can't register for other branches

**Receptionist:**
- Branch-specific access
- Register customers (own branch)
- Activate subscriptions (any customer)
- Check-in customers

**Accountant:**
- View financial data
- Branch-specific

---

## 🧪 TEST DATA

### Staff Accounts

**Receptionist:**
- Phone: `01511111111`
- Password: `reception123`
- Branch: 1 (Dragon Club)

**Owner:**
- Phone: `01500000001`
- Password: `owner123`
- All branches

### Customer Accounts

**Customer 1:**
- Phone: `01077827638`
- Temp Password: `RX04AF`
- Name: Mohamed Salem
- Branch: 1

**Customer 2:**
- Phone: `01022981052`
- Temp Password: `SI19IC`
- Name: Layla Rashad
- Branch: 1

---

**END OF DOCUMENTATION**

