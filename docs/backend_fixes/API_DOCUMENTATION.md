# API Integration Guide

## Backend Base URL
```
https://yamenmod91.pythonanywhere.com
```

## Authentication

### Login
**Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "owner",
      "full_name": "System Owner",
      "email": "owner@gym.com",
      "phone": "0201234567",
      "role": "owner",
      "branch_id": null,
      "branch_name": null,
      "is_active": true,
      "created_at": "2026-01-28T00:44:23.555315",
      "last_login": "2026-01-28T00:45:42.535708"
    }
  }
}
```

**Note:** The token is located at `data.access_token` (nested structure).

## Customer Management

### Register Customer
**Endpoint:** `POST /api/customers/register`

**Request:**
```json
{
  "full_name": "John Doe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "gender": "male",
  "age": 30,
  "weight": 75.5,
  "height": 180,
  "bmi": 23.3,
  "bmi_category": "Normal",
  "bmr": 1750.5,
  "daily_calories": 2712.5,
  "fingerprint_hash": "abc123def456",
  "branch_id": 1
}
```

## Subscription Management

### Activate Subscription
**Endpoint:** `POST /api/subscriptions/activate`

**Request:**
```json
{
  "customer_id": 1,
  "service_id": 1,
  "branch_id": 1,
  "amount": 100.00,
  "payment_method": "cash|card|transfer"
}
```

### Renew Subscription
**Endpoint:** `POST /api/subscriptions/renew`

**Request:**
```json
{
  "subscription_id": 1,
  "amount": 100.00,
  "payment_method": "cash"
}
```

### Freeze Subscription
**Endpoint:** `POST /api/subscriptions/freeze`

**Request:**
```json
{
  "subscription_id": 1,
  "freeze_days": 7
}
```

### Stop Subscription
**Endpoint:** `POST /api/subscriptions/stop`

**Request:**
```json
{
  "subscription_id": 1
}
```

## Payment Management

### Record Payment
**Endpoint:** `POST /api/payments/record`

**Request:**
```json
{
  "customer_id": 1,
  "amount": 100.00,
  "payment_method": "cash",
  "branch_id": 1,
  "subscription_id": 1,
  "notes": "Monthly payment",
  "payment_date": "2026-01-28T10:00:00Z"
}
```

### Daily Closing
**Endpoint:** `POST /api/payments/daily-closing`

**Request:**
```json
{
  "branch_id": 1,
  "closing_date": "2026-01-28"
}
```

## Reports

### Revenue Report
**Endpoint:** `GET /api/reports/revenue`

**Query Parameters:**
- `branch_id` (optional): Filter by branch
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `group_by` (optional): service, branch, payment_method

**Response:**
```json
{
  "total_revenue": 50000.00,
  "total_customers": 150,
  "active_subscriptions": 120,
  "total_expenses": 15000.00,
  "net_profit": 35000.00
}
```

### Branch Comparison
**Endpoint:** `GET /api/reports/branch-comparison`

**Query Parameters:**
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

**Response:**
```json
{
  "branches": [
    {
      "id": 1,
      "name": "Main Branch",
      "revenue": 25000.00,
      "customers": 80,
      "active_subscriptions": 65
    }
  ]
}
```

### Employee Performance
**Endpoint:** `GET /api/reports/employee-performance`

**Query Parameters:**
- `branch_id` (optional)
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

## Finance

### Daily Sales
**Endpoint:** `GET /api/finance/daily-sales`

**Query Parameters:**
- `branch_id` (optional)
- `service_id` (optional)
- `payment_method` (optional)
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

### Expenses
**Endpoint:** `GET /api/finance/expenses`

**Query Parameters:**
- `branch_id` (optional)
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

### Cash Differences
**Endpoint:** `GET /api/finance/cash-differences`

**Query Parameters:**
- `branch_id` (optional)
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

**Response:**
```json
{
  "expected_cash": 5000.00,
  "actual_cash": 4950.00,
  "difference": -50.00
}
```

## Complaints

### Submit Complaint
**Endpoint:** `POST /api/complaints/submit`

**Request:**
```json
{
  "title": "Equipment not working",
  "description": "Treadmill 3 is broken",
  "branch_id": 1,
  "customer_id": 1
}
```

### List Complaints
**Endpoint:** `GET /api/complaints`

**Query Parameters:**
- `branch_id` (optional)
- `status` (optional): pending, resolved
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

## Common Response Codes

- `200` - Success
- `201` - Created successfully
- `400` - Bad request (validation error)
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Server error

## Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "errors": {
    "field_name": ["Error message 1", "Error message 2"]
  }
}
```

## Request Headers

All authenticated requests must include:

```
Authorization: Bearer {jwt_token}
Content-Type: application/json
Accept: application/json
```
