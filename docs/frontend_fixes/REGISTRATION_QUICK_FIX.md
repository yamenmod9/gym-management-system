# Registration Issue - Quick Fix Guide

## Current Status
✅ Frontend code is fixed and improved
❓ Registration still failing - likely backend issue

## What Was Fixed in Frontend

### 1. Enhanced Error Handling
- Better exception catching
- Detailed logging for debugging
- Stack traces on unexpected errors

### 2. Data Preparation
- Automatically adds `branch_id`
- Removes null values
- Removes `qr_code` field (backend generates)
- Removes `id` field (backend assigns)

### 3. Debug Logging
Every registration attempt logs:
- Request endpoint
- Data being sent
- Response status
- Response data
- Error details if failed

---

## How to Debug

### Run the app and try to register:

**Watch console for:**

```
=== API REQUEST ===
Endpoint: /api/customers/register
Data: {...}
```

Then one of:

**Success:**
```
Response Status: 201
Response Data: {message: ..., customer: {...}}
```

**Network Error:**
```
=== DIO EXCEPTION ===
Type: connectionError
Message: Connection refused
```

**Server Error:**
```
=== DIO EXCEPTION ===
Type: badResponse
Status Code: 400/401/500
Response: {message: error details}
```

---

## Common Issues & Fixes

### Issue: "Connection timeout"
**Cause**: Backend not accessible
**Fix**: Check internet, verify backend URL, test with curl

### Issue: "401 Unauthorized"
**Cause**: Token expired or invalid
**Fix**: Re-login to app, check token in API service

### Issue: "400 Bad Request"
**Cause**: Validation error, missing field, wrong format
**Fix**: Check response message for details, verify field names match backend

### Issue: "500 Server Error"
**Cause**: Backend crashed or database issue
**Fix**: Contact backend developer, check server logs

---

## Test Backend Directly

```bash
# 1. Login
curl https://yamenmod91.pythonanywhere.com/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "reception", "password": "your_password"}'

# 2. Register (use token from step 1)
curl https://yamenmod91.pythonanywhere.com/api/customers/register \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "full_name": "Test User",
    "gender": "male",
    "age": 25,
    "weight": 70.0,
    "height": 1.70,
    "branch_id": 1
  }'
```

---

## What Backend Must Do

1. Accept POST to `/api/customers/register`
2. Validate required fields
3. Generate QR code: `GYM-{customer_id}`
4. Return:
```json
{
  "message": "Customer registered successfully",
  "customer": {
    "id": 123,
    "full_name": "Test User",
    "qr_code": "GYM-123",
    ...
  }
}
```

---

## Next Step

Run the app and copy the exact console output when registration fails.
The logs will tell us exactly what's wrong.

---

## All Frontend Changes Complete ✅

1. ✅ Dark theme (black/grey with red)
2. ✅ App icon (dark with red dumbbell)
3. ✅ QR code display (in customer profile)
4. ✅ Registration improved (better error handling)
5. ✅ Fingerprint removed

**Just need to fix backend connection issue!**
