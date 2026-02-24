# 🚀 GYM BACKEND - CLIENT APP & SUBSCRIPTION ACTIVATION - COMPLETE IMPLEMENTATION GUIDE

## 📋 OVERVIEW

You need to implement **TWO** separate backend modules:

1. **Client App Backend** (`/api/clients/*`) - For gym members to access via mobile app
2. **Subscription Activation Fix** - Fix the subscription activation endpoint for reception staff

The backend should be organized in a clean, modular structure with separate API namespaces for staff and clients.

---

## 🏗️ PART 1: PROJECT STRUCTURE

Organize the Flask backend into separate modules:

```
gym_backend/
├── app.py                          # Main Flask app
├── config.py                       # Configuration
├── models/
│   ├── __init__.py
│   ├── user.py                     # Staff users (reception, manager, etc.)
│   ├── customer.py                 # Gym members/clients
│   ├── subscription.py             # Subscription records
│   └── service.py                  # Gym services
├── api/
│   ├── __init__.py
│   ├── auth/                       # Staff authentication
│   │   ├── __init__.py
│   │   └── routes.py               # POST /api/auth/login
│   ├── customers/                  # Staff customer management
│   │   ├── __init__.py
│   │   └── routes.py               # GET/POST /api/customers/*
│   ├── subscriptions/              # Staff subscription management
│   │   ├── __init__.py
│   │   └── routes.py               # POST /api/subscriptions/activate, etc.
│   └── clients/                    # 🆕 CLIENT APP ENDPOINTS
│       ├── __init__.py
│       ├── auth.py                 # Client authentication
│       └── profile.py              # Client profile, QR, subscription
├── services/
│   ├── __init__.py
│   ├── password_service.py         # Password generation and hashing
│   └── email_service.py            # Email sending (optional)
└── utils/
    ├── __init__.py
    └── decorators.py               # JWT decorators
```

---

## 🗄️ PART 2: DATABASE CHANGES

### Update Customer Model

Add these fields to the `Customer` model:

```python
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

class Customer(db.Model):
    __tablename__ = 'customers'
    
    # Existing fields
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    qr_code = db.Column(db.String(50), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    bmi = db.Column(db.Float)
    bmi_category = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 🆕 NEW FIELDS FOR CLIENT APP
    temporary_password = db.Column(db.String(255), nullable=True)  # Hashed password
    password_changed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Helper methods
    @staticmethod
    def generate_temp_password(length=6):
        """Generate 6-character temporary password (uppercase + digits)"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def set_password(self, password):
        """Hash and set password"""
        self.temporary_password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        if not self.temporary_password:
            return False
        return check_password_hash(self.temporary_password, password)
    
    def to_dict_with_credentials(self):
        """Return dict including temporary password for reception"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'qr_code': self.qr_code,
            'branch_id': self.branch_id,
            'password_changed': self.password_changed,
            'is_active': self.is_active,
            'has_active_subscription': self.has_active_subscription,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def has_active_subscription(self):
        """Check if customer has active subscription"""
        active_sub = Subscription.query.filter_by(
            customer_id=self.id,
            status='active'
        ).first()
        return active_sub is not None
```

### Migration Script

```python
# migrations/add_client_auth_fields.py
from flask_migrate import Migrate
from app import app, db

def upgrade():
    with app.app_context():
        # Add new columns
        db.engine.execute("""
            ALTER TABLE customers 
            ADD COLUMN temporary_password VARCHAR(255),
            ADD COLUMN password_changed BOOLEAN DEFAULT FALSE,
            ADD COLUMN is_active BOOLEAN DEFAULT TRUE,
            ADD COLUMN last_login TIMESTAMP
        """)
        
        # Set all existing customers to active
        db.engine.execute("""
            UPDATE customers 
            SET is_active = TRUE, password_changed = FALSE
            WHERE temporary_password IS NULL
        """)
```

---

## 👥 PART 3: CLIENT APP ENDPOINTS

### 3.1 Client Login

**Endpoint:** `POST /api/clients/auth/login`

**Purpose:** Allow clients to login with phone/email + password (temporary or changed)

**Request:**
```json
{
  "identifier": "01234567890",  // Phone OR email
  "password": "AB12CD"           // Temporary password or changed password
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "password_changed": false,  // 🔥 IMPORTANT: Tells app to force password change
    "client": {
      "id": 123,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "qr_code": "GYM-123",
      "branch_name": "Dragon Club",
      "subscription_status": "active"
    }
  }
}
```

**Implementation:**

```python
# api/clients/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from models.customer import Customer
from models.branch import Branch
from datetime import datetime

clients_auth_bp = Blueprint('clients_auth', __name__)

@clients_auth_bp.route('/login', methods=['POST'])
def client_login():
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '').strip()
    
    if not identifier or not password:
        return jsonify({
            'status': 'error',
            'message': 'Phone/email and password are required',
            'code': 'MISSING_CREDENTIALS'
        }), 400
    
    # Detect if identifier is phone or email
    customer = None
    if '@' in identifier and '.' in identifier:
        # It's an email
        customer = Customer.query.filter_by(email=identifier).first()
    else:
        # It's a phone number - normalize it
        normalized_phone = identifier.replace(' ', '').replace('-', '').replace('+', '')
        customer = Customer.query.filter_by(phone=normalized_phone).first()
    
    # Check if customer exists
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone/email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401
    
    # Check if account is active
    if not customer.is_active:
        return jsonify({
            'status': 'error',
            'message': 'Your account has been deactivated. Please contact reception.',
            'code': 'ACCOUNT_INACTIVE'
        }), 403
    
    # Verify password
    if not customer.check_password(password):
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone/email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401
    
    # Update last login
    customer.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate JWT tokens
    identity = {
        'id': customer.id,
        'type': 'client',  # Differentiate from staff tokens
        'branch_id': customer.branch_id
    }
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    
    # Get branch name
    branch = Branch.query.get(customer.branch_id)
    branch_name = branch.name if branch else None
    
    # Get subscription status
    active_sub = Subscription.query.filter_by(
        customer_id=customer.id,
        status='active'
    ).first()
    
    subscription_status = 'active' if active_sub else 'inactive'
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 86400,  # 24 hours
            'password_changed': customer.password_changed,  # 🔥 Critical field
            'client': {
                'id': customer.id,
                'full_name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email,
                'qr_code': customer.qr_code,
                'branch_name': branch_name,
                'subscription_status': subscription_status
            }
        }
    }), 200
```

---

### 3.2 Change Password

**Endpoint:** `POST /api/clients/change-password`

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "current_password": "AB12CD",
  "new_password": "mynewpassword123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

**Implementation:**

```python
# api/clients/auth.py
from flask_jwt_extended import jwt_required, get_jwt_identity

@clients_auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    identity = get_jwt_identity()
    
    # Verify this is a client token
    if identity.get('type') != 'client':
        return jsonify({
            'status': 'error',
            'message': 'Invalid token type',
            'code': 'INVALID_TOKEN_TYPE'
        }), 403
    
    customer_id = identity.get('id')
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Customer not found',
            'code': 'CUSTOMER_NOT_FOUND'
        }), 404
    
    data = request.get_json()
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    
    # Validation
    if not current_password or not new_password:
        return jsonify({
            'status': 'error',
            'message': 'Current password and new password are required',
            'code': 'MISSING_PASSWORDS'
        }), 400
    
    if len(new_password) < 6:
        return jsonify({
            'status': 'error',
            'message': 'New password must be at least 6 characters',
            'code': 'PASSWORD_TOO_SHORT'
        }), 400
    
    # Verify current password
    if not customer.check_password(current_password):
        return jsonify({
            'status': 'error',
            'message': 'Current password is incorrect',
            'code': 'INCORRECT_PASSWORD'
        }), 401
    
    # Check if new password is same as current
    if customer.check_password(new_password):
        return jsonify({
            'status': 'error',
            'message': 'New password must be different from current password',
            'code': 'SAME_PASSWORD'
        }), 400
    
    # Update password
    customer.set_password(new_password)
    customer.password_changed = True
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Password changed successfully'
    }), 200
```

---

### 3.3 Get Client Profile

**Endpoint:** `GET /api/clients/profile`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "GYM-123",
    "branch_name": "Dragon Club",
    "gender": "male",
    "age": 25,
    "weight": 80,
    "height": 175,
    "bmi": 26.1,
    "bmi_category": "Overweight",
    "subscription_status": "active",
    "active_subscription": {
      "id": 45,
      "service_name": "Monthly Gym",
      "start_date": "2026-02-10",
      "end_date": "2026-03-10",
      "status": "active",
      "days_remaining": 25
    }
  }
}
```

**Implementation:**

```python
# api/clients/profile.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.customer import Customer
from models.subscription import Subscription
from models.service import Service
from models.branch import Branch
from datetime import datetime

clients_profile_bp = Blueprint('clients_profile', __name__)

@clients_profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    
    if identity.get('type') != 'client':
        return jsonify({
            'status': 'error',
            'message': 'Invalid token type'
        }), 403
    
    customer_id = identity.get('id')
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Customer not found'
        }), 404
    
    # Get branch name
    branch = Branch.query.get(customer.branch_id)
    branch_name = branch.name if branch else None
    
    # Get active subscription
    active_sub = Subscription.query.filter_by(
        customer_id=customer.id,
        status='active'
    ).first()
    
    subscription_data = None
    subscription_status = 'inactive'
    
    if active_sub:
        subscription_status = 'active'
        service = Service.query.get(active_sub.service_id)
        days_remaining = (active_sub.end_date - datetime.now().date()).days if active_sub.end_date else 0
        
        subscription_data = {
            'id': active_sub.id,
            'service_name': service.name if service else 'Unknown',
            'start_date': active_sub.start_date.isoformat() if active_sub.start_date else None,
            'end_date': active_sub.end_date.isoformat() if active_sub.end_date else None,
            'status': active_sub.status,
            'days_remaining': max(0, days_remaining)
        }
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,
            'branch_name': branch_name,
            'gender': customer.gender,
            'age': customer.age,
            'weight': customer.weight,
            'height': customer.height,
            'bmi': customer.bmi,
            'bmi_category': customer.bmi_category,
            'subscription_status': subscription_status,
            'active_subscription': subscription_data
        }
    }), 200
```

---

### 3.4 Get QR Code

**Endpoint:** `GET /api/clients/qr`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "status": "success",
  "data": {
    "qr_code": "GYM-123",
    "full_name": "Ahmed Hassan",
    "subscription_status": "active",
    "can_enter": true
  }
}
```

---

### 3.5 Get Entry History

**Endpoint:** `GET /api/clients/entry-history`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "status": "success",
  "data": {
    "total": 45,
    "entries": [
      {
        "id": 123,
        "entry_time": "2026-02-13T10:30:00",
        "branch_name": "Dragon Club",
        "verified_by": "Reception Staff"
      }
    ]
  }
}
```

---

## 📝 PART 4: UPDATE CUSTOMER REGISTRATION

Update the existing `/api/customers/register` endpoint to generate temporary password:

**Endpoint:** `POST /api/customers/register`

**Updated Response:**
```json
{
  "status": "success",
  "message": "Customer registered successfully",
  "data": {
    "id": 123,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "GYM-123",
    "branch_id": 1,
    "temporary_password": "AB12CD",  // 🔥 PLAIN PASSWORD - Give to customer
    "password_changed": false,
    "note": "Give these credentials to the customer for their mobile app login"
  }
}
```

**Implementation:**

```python
# api/customers/routes.py
@customers_bp.route('/register', methods=['POST'])
@jwt_required()
def register_customer():
    data = request.get_json()
    
    # ... existing validation ...
    
    # Generate QR code
    qr_code = f"GYM-{Customer.query.count() + 1:06d}"
    
    # 🆕 Generate temporary password
    temp_password = Customer.generate_temp_password()
    
    # Create customer
    customer = Customer(
        full_name=data['full_name'],
        phone=data.get('phone'),
        email=data.get('email'),
        gender=data.get('gender'),
        age=data.get('age'),
        weight=data.get('weight'),
        height=data.get('height'),
        bmi=data.get('bmi'),
        bmi_category=data.get('bmi_category'),
        qr_code=qr_code,
        branch_id=data['branch_id'],
        is_active=True,
        password_changed=False
    )
    
    # Set hashed password
    customer.set_password(temp_password)
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Customer registered successfully',
        'data': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,
            'branch_id': customer.branch_id,
            'temporary_password': temp_password,  # 🔥 PLAIN PASSWORD
            'password_changed': False,
            'note': 'Give these credentials to the customer for their mobile app login'
        }
    }), 201
```

---

## 🔄 PART 5: GET ALL CUSTOMERS WITH CREDENTIALS

Add endpoint for reception to view all customers with their credentials:

**Endpoint:** `GET /api/customers/list-with-credentials`

**Headers:** `Authorization: Bearer <staff_token>`

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 123,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "qr_code": "GYM-123",
      "password_changed": false,
      "is_active": true,
      "has_active_subscription": true,
      "created_at": "2026-02-10T10:00:00"
    }
  ]
}
```

**Note:** This endpoint should NOT return the actual password (even hashed). Reception can only see if password has been changed.

---

## 🔧 PART 6: FIX SUBSCRIPTION ACTIVATION

Fix the existing subscription activation endpoint to work properly:

**Endpoint:** `POST /api/subscriptions/activate`

**Request:**
```json
{
  "customer_id": 123,
  "service_id": 5,
  "branch_id": 1,
  "amount": 500.00,
  "payment_method": "cash"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 45,
    "customer_id": 123,
    "customer_name": "Ahmed Hassan",
    "service_name": "Monthly Gym",
    "start_date": "2026-02-13",
    "end_date": "2026-03-13",
    "amount": 500.00,
    "status": "active"
  }
}
```

**Common Issues to Fix:**
1. ✅ Ensure endpoint exists and is registered
2. ✅ Check CORS headers are properly set
3. ✅ Validate all required fields
4. ✅ Check foreign key constraints
5. ✅ Handle duplicate active subscriptions (deactivate old ones)
6. ✅ Calculate end_date based on service duration
7. ✅ Return proper error messages

---

## 🎯 TESTING

### Test 1: Customer Registration
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register \
  -H "Authorization: Bearer <staff_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01234567890",
    "email": "test@example.com",
    "branch_id": 1,
    "gender": "male",
    "age": 25,
    "weight": 75,
    "height": 175
  }'
```

**Expected:** Returns temporary password like "AB12CD"

### Test 2: Client Login
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "01234567890",
    "password": "AB12CD"
  }'
```

**Expected:** Returns access token with `password_changed: false`

### Test 3: Change Password
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/change-password \
  -H "Authorization: Bearer <client_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "AB12CD",
    "new_password": "mynewpass123"
  }'
```

**Expected:** Success message

### Test 4: Login with New Password
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "01234567890",
    "password": "mynewpass123"
  }'
```

**Expected:** Returns access token with `password_changed: true`

### Test 5: Get Profile
```bash
curl -X GET https://yamenmod91.pythonanywhere.com/api/clients/profile \
  -H "Authorization: Bearer <client_token>"
```

**Expected:** Returns full customer profile with subscription details

### Test 6: Activate Subscription
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/activate \
  -H "Authorization: Bearer <staff_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "service_id": 5,
    "branch_id": 1,
    "amount": 500.00,
    "payment_method": "cash"
  }'
```

**Expected:** Returns subscription details with start/end dates

---

## ✅ SUCCESS CRITERIA

The implementation is complete when:

1. ✅ Customer registration generates temporary password
2. ✅ Temporary password is returned in plain text to reception
3. ✅ Client can login with phone/email + temporary password
4. ✅ Login response includes `password_changed` flag
5. ✅ Client can change password
6. ✅ Password change sets `password_changed = true`
7. ✅ Client can login with new password
8. ✅ Client can access profile, QR code, entry history
9. ✅ Reception can view all customers (without seeing passwords)
10. ✅ Subscription activation works correctly

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Add new database columns to production
- [ ] Run migration script
- [ ] Test all client endpoints
- [ ] Test subscription activation
- [ ] Update API documentation
- [ ] Test CORS headers
- [ ] Verify JWT token generation
- [ ] Test on Android app
- [ ] Monitor error logs

---

## 📧 CONTACT

If you need clarification on any endpoint or behavior, please ask!

**Backend Base URL:** `https://yamenmod91.pythonanywhere.com`

**Test Accounts:**
- Reception: `reception1` / `reception123`
- Manager: `manager1` / `manager123`
- Owner: `owner` / `owner123`

---

## 🎉 READY TO IMPLEMENT!

This is a complete guide with:
- ✅ Clear project structure
- ✅ Database schema changes
- ✅ Complete endpoint implementations
- ✅ Request/response examples
- ✅ Testing commands
- ✅ Security considerations

**Please implement this backend system and let me know when it's ready for testing!**

