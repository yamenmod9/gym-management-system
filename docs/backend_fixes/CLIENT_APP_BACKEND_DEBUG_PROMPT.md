# 🔧 GYM CLIENT APP - BACKEND DEBUG PROMPT FOR CLAUDE SONNET 4.5

## 📋 ISSUE SUMMARY

I have a Flutter gym **CLIENT app** (NOT staff app) that allows gym members to:
- Activate their account via activation code (phone/email)
- View subscription details
- Display QR/barcode for gym entry
- Track expiry & coin balance
- View entry history

**CURRENT PROBLEM:** Registration/activation is failing with "Resource not found" error.

---

## 🌐 BACKEND API

**Base URL:** `https://yamenmod91.pythonanywhere.com`

### Expected Client Endpoints:

```
POST /api/clients/request-activation
Body: { "identifier": "phone_or_email" }
Response: { "status": "success", "message": "Code sent" }

POST /api/clients/verify-activation  
Body: { "identifier": "phone_or_email", "activation_code": "123456" }
Response: { 
  "status": "success",
  "data": {
    "access_token": "jwt_token",
    "client": {
      "id": 1,
      "full_name": "John Doe",
      "phone": "01234567890",
      "email": "john@example.com",
      "qr_code": "unique_client_code",
      "subscription_status": "active"
    }
  }
}

GET /api/clients/profile
Headers: { "Authorization": "Bearer <token>" }
Response: {
  "status": "success",
  "data": {
    "id": 1,
    "full_name": "John Doe",
    "phone": "01234567890",
    "email": "john@example.com",
    "qr_code": "GYM-CLIENT-001",
    "subscription_status": "active"
  }
}

GET /api/clients/subscription
Headers: { "Authorization": "Bearer <token>" }
Response: {
  "status": "success",
  "data": {
    "id": 1,
    "subscription_type": "Gold Membership",
    "start_date": "2026-01-01",
    "expiry_date": "2026-12-31",
    "status": "active",
    "remaining_coins": 50,
    "allowed_services": ["Gym", "Pool", "Spa"],
    "freeze_history": []
  }
}

GET /api/clients/entry-history
Headers: { "Authorization": "Bearer <token>" }
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

POST /api/clients/refresh-qr
Headers: { "Authorization": "Bearer <token>" }
Response: {
  "status": "success",
  "data": {
    "qr_code": "GYM-CLIENT-001-REFRESH",
    "expires_at": "2026-02-10T10:00:00"
  }
}
```

---

## 🐛 CURRENT ERROR

When trying to register/activate a client account:
- **Error:** "Resource not found" (404)
- **Request:** POST to `/api/clients/request-activation` or similar
- **Possible causes:**
  1. Endpoint doesn't exist on backend
  2. Wrong HTTP method
  3. Wrong URL path
  4. Missing authentication header where required
  5. Backend route not configured for client activation

---

## ✅ WHAT I NEED YOU TO CHECK

### 1. **Verify Client Endpoints Exist**

Please check if these endpoints are implemented in the Flask backend:

```python
# Expected routes in Flask backend
@app.route('/api/clients/request-activation', methods=['POST'])
@app.route('/api/clients/verify-activation', methods=['POST'])
@app.route('/api/clients/profile', methods=['GET'])
@app.route('/api/clients/subscription', methods=['GET'])
@app.route('/api/clients/entry-history', methods=['GET'])
@app.route('/api/clients/refresh-qr', methods=['POST'])
```

### 2. **Check Database Schema**

Does the backend have:
- `clients` or `customers` table with:
  - `activation_code` column (6-digit string)
  - `activation_code_expires` column (datetime)
  - `qr_code` column (unique identifier)
  - `is_activated` boolean column
  - JWT token generation for clients

### 3. **Authentication Flow**

For CLIENT authentication (not staff):
- Should use activation code (not password)
- Should generate a separate JWT token (different from staff tokens)
- Token should identify the customer/client ID

### 4. **Expected Backend Logic**

**Request Activation:**
```python
@app.route('/api/clients/request-activation', methods=['POST'])
def request_activation():
    identifier = request.json.get('identifier')  # phone or email
    
    # Find customer by phone or email
    customer = Customer.query.filter(
        (Customer.phone == identifier) | (Customer.email == identifier)
    ).first()
    
    if not customer:
        return jsonify({'status': 'error', 'message': 'Customer not found'}), 404
    
    # Generate 6-digit code
    activation_code = generate_6_digit_code()
    customer.activation_code = activation_code
    customer.activation_code_expires = datetime.now() + timedelta(minutes=10)
    db.session.commit()
    
    # Send code via SMS or email (can be mocked)
    send_activation_code(customer.phone, activation_code)
    
    return jsonify({'status': 'success', 'message': 'Code sent'})
```

**Verify Activation:**
```python
@app.route('/api/clients/verify-activation', methods=['POST'])
def verify_activation():
    identifier = request.json.get('identifier')
    code = request.json.get('activation_code')
    
    customer = Customer.query.filter(
        (Customer.phone == identifier) | (Customer.email == identifier),
        Customer.activation_code == code,
        Customer.activation_code_expires > datetime.now()
    ).first()
    
    if not customer:
        return jsonify({'status': 'error', 'message': 'Invalid or expired code'}), 401
    
    # Generate JWT token for client
    access_token = create_access_token(identity=customer.id, additional_claims={'type': 'client'})
    
    # Mark as activated
    customer.is_activated = True
    customer.activation_code = None
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'data': {
            'access_token': access_token,
            'client': customer.to_dict()
        }
    })
```

---

## 🎯 WHAT I NEED FROM YOU

1. **Check if these endpoints exist** in the backend code
2. **If they don't exist, implement them** following the structure above
3. **Ensure proper database columns** are present
4. **Test with Postman** or curl:

```bash
# Test 1: Request activation code
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/request-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890"}'

# Expected: {"status": "success", "message": "Code sent"}

# Test 2: Verify activation code
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/verify-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890", "activation_code": "123456"}'

# Expected: {"status": "success", "data": {"access_token": "...", "client": {...}}}
```

5. **Return the complete backend implementation** for client activation endpoints

---

## 📊 CONTEXT: EXISTING STAFF ENDPOINTS

The backend already has staff authentication working:

```
POST /api/auth/login
Body: { "username": "owner", "password": "owner123" }
Response: { "status": "success", "data": { "access_token": "...", "user": {...} } }
```

**Staff roles:** owner, branch_manager, front_desk, central_accountant, branch_accountant

**CLIENT authentication should be separate** and use activation codes instead of passwords.

---

## 🔍 KEY DIFFERENCES

| Feature | Staff App | Client App |
|---------|-----------|------------|
| Auth Method | Username + Password | Phone/Email + 6-digit code |
| JWT Claims | role, branch_id | client_id, type='client' |
| Endpoints | /api/auth/login | /api/clients/verify-activation |
| QR Code | Not needed | Primary feature |

---

## ✅ SUCCESS CRITERIA

After your fixes, I should be able to:

1. Enter phone number (e.g., "01234567890") in Flutter app
2. Receive "Code sent" confirmation
3. Enter 6-digit activation code
4. Get authenticated and see client dashboard
5. View QR code for gym entry

---

## 📝 ADDITIONAL INFO

- Backend is hosted on PythonAnywhere
- Database: SQLAlchemy with Flask
- Already has Customer/Client table with registered gym members
- Flutter app is ready, just needs backend endpoints to work

Please review the backend and implement the missing client authentication endpoints!
