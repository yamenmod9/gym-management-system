# Quick Start Guide - Client Features

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Backend running on http://localhost:5000 (or PythonAnywhere)
- Python 3.11+ with requests library
- Database migrated with client features

### Step 1: Run Migration

```bash
cd backend
python migrate_client_features.py
```

Expected output:
```
✓ Will create activation_codes table
✓ Will create entry_logs table
✅ Database tables created successfully!
✅ Sample data created successfully!
```

### Step 2: Test Client Authentication

```bash
# Run interactive test script
python test_client_features.py
```

Or manually:

```bash
# Request activation code
curl -X POST http://localhost:5000/api/client/auth/request-code \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890"}'

# Check console for 6-digit code (e.g., 123456)

# Verify code and get token
curl -X POST http://localhost:5000/api/client/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890", "code": "123456"}'
```

### Step 3: Generate QR Code

```bash
# Use client token from step 2
curl -X GET http://localhost:5000/api/client/qr \
  -H "Authorization: Bearer {CLIENT_TOKEN}"
```

### Step 4: Validate Entry (Staff)

```bash
# Login as staff
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "reception1", "password": "reception123"}'

# Validate QR code
curl -X POST http://localhost:5000/api/validation/qr \
  -H "Authorization: Bearer {STAFF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "{QR_TOKEN_FROM_STEP_3}"}'
```

### Step 5: Check Entry History

```bash
# Client checks their history
curl -X GET http://localhost:5000/api/client/history \
  -H "Authorization: Bearer {CLIENT_TOKEN}"
```

---

## 📱 Mobile App Integration

### Flutter/React Native Example

```dart
// 1. Request activation code
final response = await http.post(
  Uri.parse('$baseUrl/client/auth/request-code'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'identifier': phoneNumber}),
);

// 2. User enters code from SMS
// 3. Verify code
final authResponse = await http.post(
  Uri.parse('$baseUrl/client/auth/verify-code'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'identifier': phoneNumber,
    'code': userEnteredCode,
  }),
);

// 4. Store token
final token = jsonDecode(authResponse.body)['data']['access_token'];
await secureStorage.write(key: 'auth_token', value: token);

// 5. Generate QR for entry
final qrResponse = await http.get(
  Uri.parse('$baseUrl/client/qr'),
  headers: {'Authorization': 'Bearer $token'},
);

final qrToken = jsonDecode(qrResponse.body)['data']['qr_token'];

// 6. Display QR code
QrImageView(
  data: qrToken,
  version: QrVersions.auto,
  size: 300.0,
);
```

---

## 🔐 Security Checklist

- ✅ Activation codes are SHA-256 hashed
- ✅ Codes expire in 15 minutes
- ✅ Max 3 verification attempts per code
- ✅ QR tokens expire in 5-10 minutes
- ✅ Separate JWT scopes for clients vs staff
- ✅ Client tokens can only access own data
- ✅ All entry operations logged with audit trail

---

## 📊 API Endpoints Summary

### Client Endpoints (require client token)
- `POST /api/client/auth/request-code` - Request OTP
- `POST /api/client/auth/verify-code` - Verify OTP & login
- `GET /api/client/me` - Get profile
- `GET /api/client/subscription` - Active subscription
- `GET /api/client/qr` - Generate QR code
- `GET /api/client/history` - Entry history
- `GET /api/client/stats` - Statistics

### Staff Endpoints (require staff token)
- `POST /api/validation/qr` - Validate QR code
- `POST /api/validation/barcode` - Validate barcode
- `POST /api/validation/manual` - Manual entry
- `GET /api/validation/entry-logs` - View entries

---

## 🧪 Testing Scenarios

### Scenario 1: Happy Path
1. Client requests code ✅
2. Receives SMS with code ✅
3. Verifies code and gets JWT ✅
4. Generates QR code ✅
5. Shows QR at gym ✅
6. Staff scans and approves ✅
7. Visit deducted from subscription ✅

### Scenario 2: Expired QR
1. Client generates QR
2. Waits 10+ minutes
3. Staff scans QR
4. System rejects (expired) ❌
5. Client generates new QR
6. Staff scans new QR ✅

### Scenario 3: No Visits Left
1. Customer has 0 remaining visits
2. Client generates QR
3. Staff scans QR
4. System rejects (no visits) ❌
5. Client sees error message
6. Needs to renew subscription

### Scenario 4: Barcode Entry
1. Client shows membership card
2. Staff scans barcode (GYM-151)
3. System looks up customer
4. Validates subscription ✅
5. Deducts visit ✅

---

## 🔧 Configuration

### Notification Provider

**Default (Console):**
```python
# No configuration needed
# Codes printed to console/logs
```

**Twilio (SMS):**
```python
from app.services.notification_service import (
    configure_notification_service,
    TwilioNotificationProvider
)

provider = TwilioNotificationProvider(
    account_sid=os.getenv('TWILIO_SID'),
    auth_token=os.getenv('TWILIO_TOKEN'),
    from_number=os.getenv('TWILIO_NUMBER')
)
configure_notification_service(provider)
```

**SMTP (Email):**
```python
provider = SMTPNotificationProvider(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    username=os.getenv('EMAIL_USER'),
    password=os.getenv('EMAIL_PASS')
)
configure_notification_service(provider)
```

---

## 📝 Common Issues

### Issue: "No active subscription"
**Cause:** Customer doesn't have active subscription  
**Fix:** Create subscription for customer first

### Issue: "Invalid or expired QR code"
**Cause:** QR token expired (>10 min old)  
**Fix:** Generate new QR code

### Issue: "No remaining visits"
**Cause:** Subscription has 0 visits left  
**Fix:** Renew or upgrade subscription

### Issue: "Activation code not received"
**Cause:** Using default console provider  
**Fix:** Check console/logs for the code, or configure real SMS provider

---

## 📚 Documentation

- **[Complete API Reference](CLIENT_FEATURES_API.md)** - All endpoints with examples
- **[Implementation Details](CLIENT_FEATURES_IMPLEMENTATION.md)** - Architecture & flows
- **[Main README](README.md)** - Backend overview

---

## 🎯 Next Steps

1. ✅ Test locally with `test_client_features.py`
2. ✅ Deploy to PythonAnywhere
3. ✅ Integrate with mobile app
4. ✅ Configure SMS provider (optional)
5. ✅ Monitor entry logs for analytics

---

**Need Help?** Check [CLIENT_FEATURES_API.md](CLIENT_FEATURES_API.md) for detailed documentation.
