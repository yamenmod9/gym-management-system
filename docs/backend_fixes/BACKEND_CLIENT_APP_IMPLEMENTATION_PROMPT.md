# 🏗️ GYM MANAGEMENT SYSTEM - CLIENT APP BACKEND IMPLEMENTATION

## 📋 OVERVIEW

You need to implement a **complete backend system for the Gym Client App** that allows gym members (customers) to:
- Login using their phone/email + temporary password
- Change their temporary password on first login
- View their profile and subscription details
- Access their QR code for gym entry
- View their entry history

## 🎯 CURRENT SITUATION

### What Already Exists

1. **Staff Backend** - Working at `https://yamenmod91.pythonanywhere.com/api/`
   - Staff authentication (`/api/auth/login`)
   - Customer management (`/api/customers/`)
   - Subscription management (`/api/subscriptions/`)
   - Payment processing
   - Reports and analytics

2. **Flutter Client App** - Partially implemented
   - Login screen ready
   - Change password screen ready
   - Profile, QR, and entry history screens ready
   - Missing: Backend API endpoints

3. **Database Model** - Customer table already has:
   - `temporary_password` field
   - `password_changed` field (boolean)
   - `phone` and `email` fields

### What Needs to Be Implemented

**NEW CLIENT API ENDPOINTS** at `/api/clients/`:
- `POST /api/clients/auth/login` - Login with phone/email + temporary password
- `POST /api/clients/change-password` - Change password
- `GET /api/clients/profile` - Get client profile
- `GET /api/clients/subscription` - Get active subscription
- `GET /api/clients/qr` - Get QR code
- `GET /api/clients/entry-history` - Get entry logs
- `POST /api/clients/refresh` - Refresh JWT token

---

## 🗄️ DATABASE SCHEMA UPDATES

### 1. Update Customer Model

Add these fields to the existing `Customer` model:

```python
# models/customer.py

class Customer(db.Model):
    __tablename__ = 'customers'
    
    # EXISTING FIELDS (keep all current fields)
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    qr_code = db.Column(db.String(50), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NEW FIELDS for client app authentication
    temporary_password = db.Column(db.String(255), nullable=True)  # Hashed password
    password_changed = db.Column(db.Boolean, default=False)  # Track if password changed
    is_active = db.Column(db.Boolean, default=True)  # Account active status
    
    # Relationships
    branch = db.relationship('Branch', backref='customers')
    subscriptions = db.relationship('Subscription', backref='customer', lazy='dynamic')
    entry_logs = db.relationship('EntryLog', backref='customer', lazy='dynamic')
```

---

## 🔐 CLIENT AUTHENTICATION SYSTEM

### Authentication Flow

1. **Reception registers new customer**
   - Backend generates 6-character temporary password (e.g., "AB12CD")
   - Password is hashed and stored in `temporary_password` field
   - Reception receives plain password to give to customer
   - `password_changed = False`

2. **Customer logs in first time**
   - Uses phone/email + temporary password
   - Backend validates credentials
   - Issues JWT token with `type: 'client'`
   - Client app detects `password_changed = False`
   - Forces password change screen

3. **Customer changes password**
   - Sends current (temporary) password + new password
   - Backend validates and updates password
   - Sets `password_changed = True`
   - Customer can now use app normally

---

## 📱 CLIENT APP API ENDPOINTS

### Base Path: `/api/clients/`

---

### 1. Login

**Endpoint:** `POST /api/clients/auth/login`

**Description:** Authenticate customer with phone/email + password (temporary or changed)

**Request Body:**
```json
{
  "identifier": "01234567890",  // Phone OR email
  "password": "AB12CD"          // Temporary or permanent password
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "password_changed": false,
    "client": {
      "id": 123,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "qr_code": "GYM-123",
      "branch_name": "Dragon Club",
      "has_active_subscription": true
    }
  }
}
```

**Error Responses:**
```json
// Invalid credentials (401)
{
  "status": "error",
  "message": "Invalid phone/email or password",
  "code": "INVALID_CREDENTIALS"
}

// Account inactive (403)
{
  "status": "error",
  "message": "Your account has been deactivated. Please contact reception.",
  "code": "ACCOUNT_INACTIVE"
}

// Missing fields (400)
{
  "status": "error",
  "message": "Phone/email and password are required",
  "code": "MISSING_FIELDS"
}
```

**Implementation Notes:**
- Detect if `identifier` is phone (digits only) or email (contains @)
- Search customer by phone OR email
- Verify password using `werkzeug.security.check_password_hash()`
- Check if `is_active = True`
- Generate JWT with claims: `{'type': 'client', 'customer_id': id}`
- Return `password_changed` flag for frontend to force password change

**Python Example:**
```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash
from models import Customer, db
import re

clients_auth_bp = Blueprint('clients_auth', __name__)

def is_email(identifier):
    """Check if identifier is an email"""
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', identifier) is not None

@clients_auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '').strip()
    
    if not identifier or not password:
        return jsonify({
            'status': 'error',
            'message': 'Phone/email and password are required',
            'code': 'MISSING_FIELDS'
        }), 400
    
    # Find customer by phone or email
    if is_email(identifier):
        customer = Customer.query.filter_by(email=identifier).first()
    else:
        # Normalize phone (remove spaces, dashes)
        normalized_phone = identifier.replace(' ', '').replace('-', '')
        customer = Customer.query.filter_by(phone=normalized_phone).first()
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone/email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401
    
    if not customer.is_active:
        return jsonify({
            'status': 'error',
            'message': 'Your account has been deactivated. Please contact reception.',
            'code': 'ACCOUNT_INACTIVE'
        }), 403
    
    # Verify password
    if not customer.temporary_password or not check_password_hash(customer.temporary_password, password):
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone/email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401
    
    # Generate JWT tokens
    access_token = create_access_token(
        identity=customer.id,
        additional_claims={'type': 'client', 'customer_id': customer.id}
    )
    refresh_token = create_refresh_token(
        identity=customer.id,
        additional_claims={'type': 'client', 'customer_id': customer.id}
    )
    
    # Get active subscription
    active_sub = customer.get_active_subscription()
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 86400,
            'password_changed': customer.password_changed,
            'client': {
                'id': customer.id,
                'full_name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email,
                'qr_code': customer.qr_code,
                'branch_name': customer.branch.name if customer.branch else None,
                'has_active_subscription': active_sub is not None
            }
        }
    }), 200
```

---

### 2. Change Password

**Endpoint:** `POST /api/clients/change-password`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "current_password": "AB12CD",
  "new_password": "mynewpassword123"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

**Error Responses:**
```json
// Invalid current password (401)
{
  "status": "error",
  "message": "Current password is incorrect",
  "code": "INVALID_PASSWORD"
}

// Password too short (400)
{
  "status": "error",
  "message": "New password must be at least 6 characters",
  "code": "PASSWORD_TOO_SHORT"
}

// Same password (400)
{
  "status": "error",
  "message": "New password must be different from current password",
  "code": "SAME_PASSWORD"
}
```

**Implementation Notes:**
- Verify current password
- Hash new password with `werkzeug.security.generate_password_hash()`
- Update `temporary_password` field with new hashed password
- Set `password_changed = True`
- Validate new password length (min 6 characters)

**Python Example:**
```python
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

def require_client_auth(f):
    """Decorator to ensure JWT is for client"""
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('type') != 'client':
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized. Client access only.',
                'code': 'UNAUTHORIZED'
            }), 403
        return f(*args, **kwargs)
    return wrapper

@clients_auth_bp.route('/change-password', methods=['POST'])
@require_client_auth
def change_password():
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Customer not found',
            'code': 'NOT_FOUND'
        }), 404
    
    data = request.get_json()
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    
    if not current_password or not new_password:
        return jsonify({
            'status': 'error',
            'message': 'Current password and new password are required',
            'code': 'MISSING_FIELDS'
        }), 400
    
    # Verify current password
    if not check_password_hash(customer.temporary_password, current_password):
        return jsonify({
            'status': 'error',
            'message': 'Current password is incorrect',
            'code': 'INVALID_PASSWORD'
        }), 401
    
    # Validate new password
    if len(new_password) < 6:
        return jsonify({
            'status': 'error',
            'message': 'New password must be at least 6 characters',
            'code': 'PASSWORD_TOO_SHORT'
        }), 400
    
    if current_password == new_password:
        return jsonify({
            'status': 'error',
            'message': 'New password must be different from current password',
            'code': 'SAME_PASSWORD'
        }), 400
    
    # Update password
    customer.temporary_password = generate_password_hash(new_password)
    customer.password_changed = True
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Password changed successfully'
    }), 200
```

---

### 3. Get Profile

**Endpoint:** `GET /api/clients/profile`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
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
    "weight": 80,
    "height": 175,
    "bmi": 26.1,
    "bmi_category": "Overweight",
    "password_changed": true,
    "active_subscription": {
      "id": 45,
      "service_name": "Monthly Gym",
      "start_date": "2026-01-11",
      "end_date": "2026-02-11",
      "status": "active",
      "remaining_days": 0
    },
    "has_active_subscription": true
  }
}
```

**Python Example:**
```python
@clients_profile_bp.route('/profile', methods=['GET'])
@require_client_auth
def get_profile():
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Customer not found',
            'code': 'NOT_FOUND'
        }), 404
    
    active_sub = customer.get_active_subscription()
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,
            'branch_name': customer.branch.name if customer.branch else None,
            'weight': customer.weight,
            'height': customer.height,
            'bmi': round(customer.weight / ((customer.height / 100) ** 2), 1) if customer.weight and customer.height else None,
            'bmi_category': customer.bmi_category,
            'password_changed': customer.password_changed,
            'active_subscription': {
                'id': active_sub.id,
                'service_name': active_sub.service.name,
                'start_date': active_sub.start_date.isoformat(),
                'end_date': active_sub.end_date.isoformat(),
                'status': active_sub.status,
                'remaining_days': (active_sub.end_date - datetime.now().date()).days
            } if active_sub else None,
            'has_active_subscription': active_sub is not None
        }
    }), 200
```

---

### 4. Get Subscription

**Endpoint:** `GET /api/clients/subscription`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "current_subscription": {
      "id": 45,
      "service_name": "Monthly Gym",
      "service_type": "gym",
      "start_date": "2026-01-11",
      "end_date": "2026-02-11",
      "status": "active",
      "remaining_days": 0,
      "freeze_days_remaining": 5
    },
    "subscription_history": [
      {
        "id": 44,
        "service_name": "Monthly Gym",
        "start_date": "2025-12-11",
        "end_date": "2026-01-11",
        "status": "completed"
      }
    ]
  }
}
```

---

### 5. Get QR Code

**Endpoint:** `GET /api/clients/qr`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "qr_code": "GYM-123",
    "qr_image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "customer_name": "Ahmed Hassan",
    "has_active_subscription": true
  }
}
```

**Python Example:**
```python
import qrcode
import io
import base64

def generate_qr_image(data):
    """Generate QR code image as base64"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

@clients_qr_bp.route('/qr', methods=['GET'])
@require_client_auth
def get_qr():
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Customer not found',
            'code': 'NOT_FOUND'
        }), 404
    
    qr_image = generate_qr_image(customer.qr_code)
    active_sub = customer.get_active_subscription()
    
    return jsonify({
        'status': 'success',
        'data': {
            'qr_code': customer.qr_code,
            'qr_image_base64': qr_image,
            'customer_name': customer.full_name,
            'has_active_subscription': active_sub is not None
        }
    }), 200
```

---

### 6. Get Entry History

**Endpoint:** `GET /api/clients/entry-history`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "entries": [
      {
        "id": 1234,
        "entry_time": "2026-02-11T09:30:00Z",
        "branch_name": "Dragon Club",
        "entry_type": "qr_scan"
      }
    ],
    "total": 125,
    "limit": 50,
    "offset": 0
  }
}
```

---

### 7. Refresh Token

**Endpoint:** `POST /api/clients/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

---

## 🔧 CUSTOMER REGISTRATION UPDATE

### Update Registration Endpoint

When reception registers a new customer via `/api/customers/register`, the backend should:

1. Generate a 6-character temporary password (uppercase + digits)
2. Hash the password
3. Store hashed password in `temporary_password` field
4. Set `password_changed = False`
5. Set `is_active = True`
6. Return the PLAIN temporary password in response for reception to give to customer

**Updated Registration Response:**
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
    "temporary_password": "AB12CD",  // PLAIN PASSWORD for reception
    "password_changed": false,
    "note": "Give these credentials to the customer for their mobile app login"
  }
}
```

**Python Example:**
```python
import random
import string

def generate_temporary_password(length=6):
    """Generate random 6-character password (uppercase + digits)"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@customers_bp.route('/register', methods=['POST'])
@jwt_required()
def register_customer():
    # ... existing validation ...
    
    # Generate temporary password
    temp_password = generate_temporary_password()
    hashed_password = generate_password_hash(temp_password)
    
    # Create customer
    customer = Customer(
        full_name=data['full_name'],
        phone=data['phone'],
        email=data.get('email'),
        # ... other fields ...
        temporary_password=hashed_password,
        password_changed=False,
        is_active=True
    )
    
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
            'temporary_password': temp_password,  # Return PLAIN password
            'password_changed': False,
            'note': 'Give these credentials to the customer for their mobile app login'
        }
    }), 201
```

---

## 📦 REQUIRED DEPENDENCIES

Add to `requirements.txt`:

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
qrcode[pil]==7.4.2
Pillow==10.2.0
werkzeug==3.0.1
```

---

## 🔒 SECURITY CONSIDERATIONS

1. **Password Hashing:** Always use `werkzeug.security.generate_password_hash()` and `check_password_hash()`
2. **JWT Claims:** Include `type: 'client'` to differentiate from staff tokens
3. **Token Expiry:** Access token: 24 hours, Refresh token: 30 days
4. **HTTPS Only:** All endpoints must use HTTPS in production
5. **Input Validation:** Validate all phone numbers and emails
6. **Rate Limiting:** Consider adding rate limiting to prevent brute force

---

## ✅ IMPLEMENTATION CHECKLIST

### Backend Tasks

- [ ] Update Customer model with new fields (`temporary_password`, `password_changed`, `is_active`)
- [ ] Run database migration to add new columns
- [ ] Implement `POST /api/clients/auth/login` endpoint
- [ ] Implement `POST /api/clients/change-password` endpoint
- [ ] Implement `GET /api/clients/profile` endpoint
- [ ] Implement `GET /api/clients/subscription` endpoint
- [ ] Implement `GET /api/clients/qr` endpoint
- [ ] Implement `GET /api/clients/entry-history` endpoint
- [ ] Implement `POST /api/clients/refresh` endpoint
- [ ] Update `POST /api/customers/register` to generate temporary password
- [ ] Add QR code generation service
- [ ] Test all endpoints with Postman
- [ ] Deploy to production

### Database Migration

```sql
-- Add new columns to customers table
ALTER TABLE customers ADD COLUMN temporary_password VARCHAR(255);
ALTER TABLE customers ADD COLUMN password_changed BOOLEAN DEFAULT FALSE;
ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT TRUE;

-- Generate temporary passwords for existing customers (optional)
-- You can run a Python script to:
-- 1. Generate random 6-char passwords
-- 2. Hash them
-- 3. Update existing customers
```

---

## 🧪 TESTING GUIDE

### Test 1: Login with Temporary Password

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890", "password": "AB12CD"}'
```

**Expected Response:**
- Status 200
- JWT tokens returned
- `password_changed: false`
- Client data included

### Test 2: Change Password

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"current_password": "AB12CD", "new_password": "mynewpass123"}'
```

**Expected Response:**
- Status 200
- Success message
- `password_changed` set to `true` in database

### Test 3: Get Profile

```bash
curl -X GET https://yamenmod91.pythonanywhere.com/api/clients/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
- Status 200
- Full customer profile
- Active subscription details
- `password_changed: true` (after password change)

### Test 4: Get QR Code

```bash
curl -X GET https://yamenmod91.pythonanywhere.com/api/clients/qr \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
- Status 200
- QR code as base64 image
- Customer name
- Subscription status

---

## 🎯 EXPECTED OUTCOME

After implementation:

1. ✅ Reception registers customer → Gets temporary password to give to customer
2. ✅ Customer receives phone/email + temporary password
3. ✅ Customer opens Flutter app → Enters phone/email + temporary password
4. ✅ Backend validates credentials → Issues JWT token
5. ✅ Flutter app checks `password_changed = false` → Forces password change screen
6. ✅ Customer changes password → Backend updates and sets `password_changed = true`
7. ✅ Customer navigates to home → Can view profile, QR code, entry history
8. ✅ Customer can login again with new password

---

## 📞 SUPPORT & DEBUGGING

### Common Issues

1. **"Invalid credentials" error**
   - Check if password is hashed correctly
   - Verify phone/email format
   - Check if `is_active = True`

2. **"Token expired" error**
   - Implement refresh token endpoint
   - Check JWT expiry settings

3. **QR code not generating**
   - Install `qrcode[pil]` and `Pillow`
   - Check if QR code data exists

4. **Database migration fails**
   - Backup database first
   - Run migration script manually
   - Check for duplicate column names

---

## 🚀 DEPLOYMENT STEPS

1. **Backup Database**
   ```bash
   pg_dump your_database > backup.sql
   ```

2. **Run Migration**
   ```python
   # In Python shell
   from app import db
   db.create_all()
   ```

3. **Generate Passwords for Existing Customers** (Optional)
   ```python
   from models import Customer
   from werkzeug.security import generate_password_hash
   import random, string
   
   customers = Customer.query.filter_by(temporary_password=None).all()
   for customer in customers:
       temp_pass = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
       customer.temporary_password = generate_password_hash(temp_pass)
       customer.password_changed = False
       customer.is_active = True
       print(f"{customer.full_name}: {temp_pass}")  # Print for records
   db.session.commit()
   ```

4. **Test Endpoints**
   - Use Postman to test each endpoint
   - Verify JWT tokens work
   - Check database updates

5. **Update Flutter App**
   - Ensure API base URL is correct
   - Test login flow
   - Test password change
   - Verify all screens work

---

**Ready to implement! 🎉**

Copy this entire document to your backend developer or implement it yourself following the examples provided.

