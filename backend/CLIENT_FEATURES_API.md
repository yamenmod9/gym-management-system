# Client Activation and Entry System - API Documentation

## Overview

This document describes the new client-facing features for the gym management system:
- **Client Activation**: OTP-based authentication for mobile app
- **Client JWT**: Separate token system for clients
- **QR/Barcode Access**: Time-limited QR codes and static barcodes for gym entry
- **Entry Logging**: Track and validate all gym entries
- **Coins/Visits System**: Automatic deduction of entry credits

## Base URL

Production: `https://yamenmod91.pythonanywhere.com`
Local: `http://localhost:5000`

---

## 1. Client Authentication

### 1.1 Request Activation Code

Request a 6-digit OTP code for client login.

**Endpoint:** `POST /api/client/auth/request-code`

**Request Body:**
```json
{
  "identifier": "01234567890",
  "delivery_method": "sms"
}
```

**Parameters:**
- `identifier` (required): Phone number or email
- `delivery_method` (optional): `"sms"` or `"email"` (auto-detected if not specified)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Activation code sent via sms",
    "delivery_target": "01****7890",
    "expires_in": 900
  }
}
```

**Notes:**
- Code expires in 15 minutes (900 seconds)
- Only one active code per customer
- Old codes are invalidated when new one is requested
- Phone/email is masked in response for security

---

### 1.2 Verify Activation Code

Verify the OTP code and receive a client JWT token.

**Endpoint:** `POST /api/client/auth/verify-code`

**Request Body:**
```json
{
  "identifier": "01234567890",
  "code": "123456"
}
```

**Parameters:**
- `identifier` (required): Phone number or email
- `code` (required): 6-digit activation code

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGci...",
    "token_type": "Bearer",
    "customer": {
      "id": 151,
      "full_name": "Ahmed Mohamed",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "qr_code": "GYM-151",
      "branch_id": 1,
      "branch_name": "Dragon Club"
    }
  }
}
```

**Error Responses:**
- 401: Invalid code or expired
- 401: Maximum attempts exceeded (3 attempts per code)

**Notes:**
- Client token expires in 7 days
- Token includes `scope: 'client'` claim
- Use token in Authorization header: `Bearer {token}`

---

## 2. Client Profile & Data

All endpoints require client JWT token in header:
```
Authorization: Bearer {client_token}
```

### 2.1 Get Profile

**Endpoint:** `GET /api/client/me`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Ahmed Mohamed",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "age": 24,
    "gender": "male",
    "height": 175.0,
    "weight": 78.5,
    "bmi": 25.63,
    "bmi_category": "Overweight",
    "bmr": 1843.6,
    "qr_code": "GYM-151",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "is_active": true,
    "active_subscription": {
      "id": 45,
      "service_name": "Gold Membership",
      "remaining_visits": 28,
      "start_date": "2026-02-01",
      "end_date": "2026-03-01",
      "status": "active"
    }
  }
}
```

---

### 2.2 Get Active Subscription

**Endpoint:** `GET /api/client/subscription`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 45,
    "customer_id": 151,
    "service_name": "Gold Membership",
    "branch_name": "Dragon Club",
    "start_date": "2026-02-01",
    "end_date": "2026-03-01",
    "remaining_visits": 28,
    "remaining_classes": 10,
    "status": "active",
    "is_frozen": false,
    "service": {
      "id": 3,
      "name": "Gold Membership",
      "service_type": "both",
      "has_visits": true,
      "has_classes": true,
      "duration_days": 30
    }
  }
}
```

---

### 2.3 Get Subscription History

**Endpoint:** `GET /api/client/subscriptions/history`

**Query Parameters:**
- `page` (optional): Page number (default 1)
- `per_page` (optional): Items per page (default 10)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "subscriptions": [
      {
        "id": 45,
        "service_name": "Gold Membership",
        "start_date": "2026-02-01",
        "end_date": "2026-03-01",
        "status": "active"
      }
    ],
    "pagination": {
      "total": 3,
      "pages": 1,
      "current_page": 1,
      "per_page": 10
    }
  }
}
```

---

## 3. QR Code & Entry

### 3.1 Generate QR Code

Generate a time-limited QR code for gym entry.

**Endpoint:** `GET /api/client/qr`

**Query Parameters:**
- `expiry_minutes` (optional): Token validity in minutes (default 5, max 10)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "qr_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2026-02-10T10:05:00",
    "expires_in": 300,
    "static_barcode": "GYM-151",
    "subscription": {
      "id": 45,
      "service_name": "Gold Membership",
      "remaining_visits": 28,
      "remaining_classes": 10,
      "end_date": "2026-03-01"
    }
  }
}
```

**Error Responses:**
- 403: No active subscription
- 403: Subscription expired/frozen
- 403: No remaining visits

**QR Token Payload:**
```json
{
  "customer_id": 151,
  "subscription_id": 45,
  "token_type": "qr_access",
  "iat": 1707559500,
  "exp": 1707559800
}
```

---

### 3.2 Get Entry History

**Endpoint:** `GET /api/client/history`

**Query Parameters:**
- `page` (optional): Page number (default 1)
- `per_page` (optional): Items per page (default 20)
- `from_date` (optional): Start date filter (ISO format)
- `to_date` (optional): End date filter (ISO format)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "entries": [
      {
        "id": 234,
        "entry_type": "qr_scan",
        "entry_status": "approved",
        "branch_name": "Dragon Club",
        "coins_deducted": 1,
        "entry_time": "2026-02-10T08:30:00"
      }
    ],
    "pagination": {
      "total": 15,
      "pages": 1,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

---

### 3.3 Get Client Stats

**Endpoint:** `GET /api/client/stats`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_visits": 45,
    "visits_this_month": 12,
    "current_streak": 5,
    "active_subscription": {
      "id": 45,
      "service_name": "Gold Membership",
      "remaining_visits": 28
    }
  }
}
```

---

## 4. Entry Validation (Staff Only)

These endpoints require **staff JWT token** with appropriate roles:
- owner
- branch_manager
- front_desk

### 4.1 Validate QR Code

Scan and validate a client's QR code.

**Endpoint:** `POST /api/validation/qr`

**Headers:**
```
Authorization: Bearer {staff_token}
```

**Request Body:**
```json
{
  "qr_token": "eyJhbGci...",
  "branch_id": 1
}
```

**Response (200 OK - Entry Approved):**
```json
{
  "success": true,
  "message": "Entry approved",
  "data": {
    "entry": {
      "id": 234,
      "entry_type": "qr_scan",
      "entry_status": "approved",
      "coins_deducted": 1,
      "entry_time": "2026-02-10T08:30:00"
    },
    "customer": {
      "id": 151,
      "full_name": "Ahmed Mohamed",
      "qr_code": "GYM-151"
    },
    "subscription": {
      "id": 45,
      "remaining_visits": 27,
      "remaining_classes": 10,
      "end_date": "2026-03-01"
    }
  }
}
```

**Error Response (403 - Entry Denied):**
```json
{
  "success": false,
  "error": "No remaining visits on subscription",
  "data": {
    "entry_id": 235,
    "status": "denied"
  }
}
```

**Error Cases:**
- Invalid or expired QR token
- Subscription expired
- Subscription frozen
- No remaining visits/classes
- Wrong branch

---

### 4.2 Validate Barcode

Scan and validate a static barcode (customer's permanent QR code).

**Endpoint:** `POST /api/validation/barcode`

**Request Body:**
```json
{
  "barcode": "GYM-151",
  "branch_id": 1
}
```

**Response:** Same format as QR validation

---

### 4.3 Manual Entry

Process entry manually (when QR/barcode fails).

**Endpoint:** `POST /api/validation/manual`

**Request Body:**
```json
{
  "customer_id": 151,
  "branch_id": 1,
  "notes": "QR scanner not working"
}
```

**Response:** Same format as QR validation

---

### 4.4 Get Entry Logs

View all entry logs (staff only).

**Endpoint:** `GET /api/validation/entry-logs`

**Query Parameters:**
- `page`, `per_page`: Pagination
- `branch_id`: Filter by branch
- `customer_id`: Filter by customer
- `status`: Filter by status (`approved` or `denied`)
- `from_date`, `to_date`: Date range

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "entries": [
      {
        "id": 234,
        "customer_name": "Ahmed Mohamed",
        "entry_type": "qr_scan",
        "entry_status": "approved",
        "branch_name": "Dragon Club",
        "coins_deducted": 1,
        "processed_by": "Sara Mohamed",
        "entry_time": "2026-02-10T08:30:00"
      }
    ],
    "pagination": {
      "total": 150,
      "pages": 8,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

---

## 5. Security Model

### Token Scopes

**Staff Token:**
```json
{
  "scope": "staff",
  "sub": "5",
  "exp": "..."
}
```
- Access: All admin endpoints
- Cannot: Access client-only endpoints

**Client Token:**
```json
{
  "scope": "client",
  "customer_id": 151,
  "sub": "151",
  "exp": "..."
}
```
- Access: Only own data and client endpoints
- Cannot: Access staff endpoints, modify data, see other clients

### Token Lifetimes

- **Activation Code**: 15 minutes
- **QR Access Token**: 5-10 minutes
- **Client JWT**: 7 days
- **Staff JWT**: 12 hours (unchanged)

### Rate Limiting

- Activation code requests: Max 3 per hour per customer
- Code verification attempts: Max 3 per code

---

## 6. Entry Flow Examples

### Example 1: QR Code Entry

1. **Client generates QR:**
   ```http
   GET /api/client/qr
   Authorization: Bearer {client_token}
   ```

2. **Client shows QR to scanner**

3. **Staff scans and validates:**
   ```http
   POST /api/validation/qr
   Authorization: Bearer {staff_token}
   Content-Type: application/json

   {
     "qr_token": "eyJhbGci..."
   }
   ```

4. **System validates and logs entry:**
   - Checks token validity
   - Checks subscription status
   - Deducts visit/class
   - Creates entry log
   - Returns approval

### Example 2: Barcode Entry

1. **Client shows membership card with barcode (GYM-151)**

2. **Staff scans barcode:**
   ```http
   POST /api/validation/barcode
   Authorization: Bearer {staff_token}
   Content-Type: application/json

   {
     "barcode": "GYM-151"
   }
   ```

3. **System validates and logs entry**

### Example 3: Manual Entry (Fallback)

1. **QR scanner not working**

2. **Staff searches customer by phone**

3. **Staff processes manual entry:**
   ```http
   POST /api/validation/manual
   Authorization: Bearer {staff_token}
   Content-Type: application/json

   {
     "customer_id": 151,
     "notes": "QR scanner malfunction"
   }
   ```

---

## 7. Database Schema

### activation_codes Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| customer_id | Integer | FK to customers |
| code_hash | String(64) | SHA-256 hash of code |
| code_type | Enum | login/registration/password_reset |
| delivery_method | String(20) | sms/email |
| delivery_target | String(120) | Phone or email |
| is_used | Boolean | Code used flag |
| attempts | Integer | Verification attempts |
| max_attempts | Integer | Max attempts (default 3) |
| created_at | DateTime | Creation time |
| expires_at | DateTime | Expiry time |
| used_at | DateTime | When used |

### entry_logs Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| customer_id | Integer | FK to customers |
| subscription_id | Integer | FK to subscriptions |
| branch_id | Integer | FK to branches |
| entry_type | Enum | qr_scan/barcode/fingerprint/manual |
| entry_status | Enum | approved/denied/pending |
| validation_token | String(500) | Token used (truncated) |
| coins_deducted | Integer | Visits/classes deducted |
| denial_reason | String(200) | Reason if denied |
| processed_by_user_id | Integer | FK to staff user |
| notes | Text | Additional notes |
| entry_time | DateTime | Entry timestamp |
| created_at | DateTime | Log creation time |

---

## 8. Migration Instructions

### Local Development

```bash
cd backend
python migrate_client_features.py
```

### Production (PythonAnywhere)

```bash
cd ~/gym-management-system/backend
source ~/virtualenvs/your-venv/bin/activate
python migrate_client_features.py
```

This creates:
- `activation_codes` table
- `entry_logs` table
- Sample activation codes (5 customers)
- Sample entry logs (3-5 per customer with active subscription)

---

## 9. Notification Service

### Architecture

```python
NotificationProvider (ABC)
├── send_sms()
└── send_email()

Implementations:
├── ConsoleNotificationProvider (default, for development)
├── TwilioNotificationProvider (stub for future)
└── SMTPNotificationProvider (stub for future)
```

### Current Implementation

By default, uses `ConsoleNotificationProvider` which prints codes to console/logs.

### Future Integration

To integrate Twilio:

```python
from app.services.notification_service import (
    configure_notification_service,
    TwilioNotificationProvider
)

provider = TwilioNotificationProvider(
    account_sid="your_sid",
    auth_token="your_token",
    from_number="+1234567890"
)

configure_notification_service(provider)
```

---

## 10. Testing

### Test Client Authentication

```bash
# Request code
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/request-code \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890"}'

# Check console/logs for code (e.g., "123456")

# Verify code
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890", "code": "123456"}'
```

### Test QR Generation

```bash
curl -X GET https://yamenmod91.pythonanywhere.com/api/client/qr \
  -H "Authorization: Bearer {client_token}"
```

### Test Entry Validation

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/validation/qr \
  -H "Authorization: Bearer {staff_token}" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "{qr_token_from_client}"}'
```

---

## 11. Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Identifier required | Missing phone/email |
| 400 | Code required | Missing activation code |
| 401 | Invalid credentials | Wrong phone/email |
| 401 | Invalid activation code | Wrong code entered |
| 401 | Maximum attempts exceeded | 3+ failed attempts |
| 403 | Client access required | Using staff token on client endpoint |
| 403 | Staff access required | Using client token on staff endpoint |
| 403 | No active subscription | Customer has no valid subscription |
| 403 | Subscription expired | Subscription end_date passed |
| 403 | Subscription frozen | Subscription is_frozen = true |
| 403 | No remaining visits | remaining_visits = 0 |
| 404 | Customer not found | Invalid customer_id |
| 404 | No active subscription | No active subscription found |

---

## Summary

✅ **Implemented:**
- Client OTP authentication (6-digit codes)
- Separate client JWT system
- QR code generation & validation
- Static barcode validation
- Entry logging with coins/visits deduction
- Client mobile app endpoints
- Staff validation endpoints
- Pluggable notification service
- Database migrations
- Sample data generation

✅ **Security:**
- Separate token scopes (client vs staff)
- Time-limited QR codes (5-10 min)
- Hashed activation codes
- Max 3 verification attempts
- Masked phone/email in responses

✅ **Compatible:**
- Existing admin APIs unchanged
- Fingerprint system intact
- All existing features working

🎯 **Ready for Production!**
