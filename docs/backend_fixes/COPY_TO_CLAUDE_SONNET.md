# 🚨 URGENT: COPY THIS ENTIRE FILE TO CLAUDE SONNET 4.5

---

I have a Flask backend for a gym management system at:
**https://yamenmod91.pythonanywhere.com**

The backend currently has staff authentication working, but I need to add CLIENT authentication for gym members.

## 🎯 WHAT I NEED

Implement these 6 endpoints for gym clients (customers):

### 1. Request Activation Code
```
POST /api/clients/request-activation
Body: {"identifier": "phone_or_email"}
Response: {"status": "success", "message": "Activation code sent"}
```

**Logic:**
- Find customer by phone OR email
- Generate random 6-digit code
- Save code to customer record with 10-minute expiration
- Return success (SMS sending can be mocked)

### 2. Verify Activation Code
```
POST /api/clients/verify-activation
Body: {
  "identifier": "phone_or_email",
  "activation_code": "123456"
}
Response: {
  "status": "success",
  "data": {
    "access_token": "jwt_token",
    "client": {
      "id": 1,
      "full_name": "John Doe",
      "phone": "01234567890",
      "email": "john@example.com",
      "qr_code": "GYM-CLIENT-001",
      "subscription_status": "active"
    }
  }
}
```

**Logic:**
- Verify customer exists with matching phone/email
- Check activation code matches
- Check code hasn't expired
- Generate JWT token with `type: 'client'` claim
- Mark customer as activated
- Clear activation code
- Return token + customer data

### 3. Get Client Profile
```
GET /api/clients/profile
Headers: {"Authorization": "Bearer <token>"}
Response: {
  "status": "success",
  "data": {
    "id": 1,
    "full_name": "John Doe",
    "phone": "01234567890",
    "email": "john@example.com",
    "qr_code": "GYM-CLIENT-001",
    "subscription_status": "active",
    "branch_name": "Dragon Club"
  }
}
```

### 4. Get Client Subscription
```
GET /api/clients/subscription
Headers: {"Authorization": "Bearer <token>"}
Response: {
  "status": "success",
  "data": {
    "subscription_type": "Gold Membership",
    "start_date": "2026-01-01",
    "expiry_date": "2026-12-31",
    "status": "active",
    "remaining_coins": 50,
    "allowed_services": ["Gym", "Pool", "Spa"],
    "freeze_history": []
  }
}
```

### 5. Get Entry History
```
GET /api/clients/entry-history
Headers: {"Authorization": "Bearer <token>"}
Response: {
  "status": "success",
  "data": [
    {
      "date": "2026-02-10",
      "time": "08:30:00",
      "branch": "Dragon Club",
      "service": "Gym",
      "coins_used": 1
    }
  ]
}
```

### 6. Refresh QR Code
```
POST /api/clients/refresh-qr
Headers: {"Authorization": "Bearer <token>"}
Response: {
  "status": "success",
  "data": {
    "qr_code": "GYM-CLIENT-001-NEW",
    "expires_at": "2026-02-10T10:00:00"
  }
}
```

---

## 📊 DATABASE CHANGES NEEDED

Add these columns to the `Customer` (or `clients`) table:

```python
class Customer(db.Model):
    # ... existing columns ...
    
    # NEW COLUMNS:
    activation_code = db.Column(db.String(6), nullable=True)
    activation_code_expires = db.Column(db.DateTime, nullable=True)
    qr_code = db.Column(db.String(50), unique=True, nullable=False)
    is_activated = db.Column(db.Boolean, default=False)
    last_qr_refresh = db.Column(db.DateTime, nullable=True)
```

---

## 🔐 JWT TOKEN REQUIREMENTS

Client tokens should include:
```python
{
  "identity": customer_id,
  "type": "client",  # To distinguish from staff tokens
  "exp": expiration_time
}
```

---

## 📝 UTILITY FUNCTIONS NEEDED

### Generate 6-digit code:
```python
import random

def generate_activation_code():
    return str(random.randint(100000, 999999))
```

### Generate unique QR code:
```python
import uuid

def generate_qr_code(customer_id):
    return f"GYM-CLIENT-{customer_id:06d}-{uuid.uuid4().hex[:8].upper()}"
```

---

## ✅ AUTHENTICATION DECORATOR

Create a decorator to verify client JWT tokens:

```python
from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def client_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('type') != 'client':
            return jsonify({'status': 'error', 'message': 'Client access only'}), 403
        return fn(*args, **kwargs)
    return wrapper
```

Usage:
```python
@app.route('/api/clients/profile', methods=['GET'])
@client_required
def get_client_profile():
    # endpoint logic
```

---

## 🧪 TEST CASES

After implementation, test with:

```bash
# 1. Request code
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/request-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890"}'

# 2. Verify code (use code from database)
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/verify-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890", "activation_code": "123456"}'

# 3. Get profile (use token from step 2)
curl -X GET https://yamenmod91.pythonanywhere.com/api/clients/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 DELIVERABLES

Please provide:
1. ✅ Complete Flask routes code
2. ✅ Updated Customer model with new columns
3. ✅ Database migration script
4. ✅ Utility functions
5. ✅ Authentication decorator
6. ✅ Test examples

---

## 📌 IMPORTANT NOTES

- This is SEPARATE from staff authentication
- Clients use phone/email + code (NO passwords)
- JWT tokens must have `type: 'client'`
- QR codes must be unique per customer
- Activation codes expire in 10 minutes
- All endpoints return JSON in format: `{"status": "success/error", "data": {...}, "message": "..."}`

---

## 🚀 CONTEXT

My existing Customer table has:
- id (primary key)
- full_name
- phone
- email
- branch_id (foreign key to branches)
- subscription_id (foreign key to subscriptions)
- created_at
- ... other fields

I just need to ADD the activation columns and implement these 6 endpoints.

---

**Please implement this now. Provide complete, production-ready code.**
