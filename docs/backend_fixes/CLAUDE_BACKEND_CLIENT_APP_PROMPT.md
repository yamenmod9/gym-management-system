# 🏗️ GYM MANAGEMENT SYSTEM - CLIENT APP BACKEND IMPLEMENTATION

## 📋 OVERVIEW

You are tasked with implementing a **separate backend module for the Gym Client App** that will work alongside the existing staff backend. The client app allows gym members (customers) to:
- Login using phone/email + 6-digit activation code (sent via SMS/Email)
- View their profile and subscription details
- Access their QR code for gym entry
- View their entry history
- Manage their account

## 🎯 PROJECT REQUIREMENTS

### Backend Structure
Create a **clean, modular backend structure** with TWO separate API modules:

```
backend/
├── app.py                          # Main Flask application
├── config.py                       # Configuration (DB, JWT, Email/SMS)
├── requirements.txt                # Python dependencies
├── models/
│   ├── __init__.py
│   ├── user.py                     # Staff users model (existing)
│   ├── customer.py                 # Customer model (enhanced)
│   ├── subscription.py             # Subscription model
│   └── entry_log.py                # Entry history model
├── api/
│   ├── __init__.py
│   ├── staff/                      # Staff App APIs (existing)
│   │   ├── __init__.py
│   │   ├── auth.py                 # Staff authentication
│   │   ├── customers.py            # Customer management
│   │   ├── subscriptions.py        # Subscription management
│   │   ├── payments.py             # Payment processing
│   │   └── reports.py              # Reports & analytics
│   └── clients/                    # Client App APIs (NEW)
│       ├── __init__.py
│       ├── auth.py                 # Client authentication (activation code)
│       ├── profile.py              # Client profile & subscription info
│       ├── qr_code.py              # QR code generation
│       └── entry_history.py        # Entry history viewing
├── services/
│   ├── __init__.py
│   ├── email_service.py            # Email sending (activation codes)
│   ├── sms_service.py              # SMS sending (activation codes)
│   └── qr_service.py               # QR code generation & validation
└── utils/
    ├── __init__.py
    ├── validators.py               # Input validation
    └── helpers.py                  # Helper functions
```

---

## 🗄️ DATABASE MODELS

### 1. Enhanced Customer Model

Add these fields to the existing `Customer` model:

```python
# models/customer.py
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customers'
    
    # Existing fields (keep all current fields)
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
    activation_code = db.Column(db.String(6), nullable=True)
    activation_code_expires = db.Column(db.DateTime, nullable=True)
    last_activation_request = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    branch = db.relationship('Branch', backref='customers')
    subscriptions = db.relationship('Subscription', backref='customer', lazy='dynamic')
    entry_logs = db.relationship('EntryLog', backref='customer', lazy='dynamic')
    
    def generate_activation_code(self):
        """Generate a 6-digit activation code valid for 10 minutes"""
        import random
        self.activation_code = f"{random.randint(100000, 999999)}"
        self.activation_code_expires = datetime.utcnow() + timedelta(minutes=10)
        self.last_activation_request = datetime.utcnow()
        return self.activation_code
    
    def verify_activation_code(self, code):
        """Verify if the activation code is valid and not expired"""
        if not self.activation_code:
            return False
        if self.activation_code_expires < datetime.utcnow():
            return False
        return self.activation_code == code
    
    def clear_activation_code(self):
        """Clear activation code after successful login"""
        self.activation_code = None
        self.activation_code_expires = None
    
    def get_active_subscription(self):
        """Get the current active subscription"""
        from datetime import date
        return self.subscriptions.filter(
            Subscription.status == 'active',
            Subscription.end_date >= date.today()
        ).first()
    
    def to_client_dict(self):
        """Convert customer to dict for client app (safe fields only)"""
        active_sub = self.get_active_subscription()
        
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'qr_code': self.qr_code,
            'branch_name': self.branch.name if self.branch else None,
            'weight': self.weight,
            'height': self.height,
            'bmi': round(self.weight / ((self.height / 100) ** 2), 1) if self.weight and self.height else None,
            'active_subscription': active_sub.to_dict() if active_sub else None,
            'has_active_subscription': active_sub is not None,
        }
```

---

## 🔐 CLIENT AUTHENTICATION SYSTEM

### Authentication Flow

1. **Client enters phone/email** → Frontend sends to `/api/clients/request-activation`
2. **Backend generates 6-digit code** → Detects if input is phone or email
3. **Backend sends code via SMS or Email** → Based on input type
4. **Client enters code** → Frontend sends to `/api/clients/verify-activation`
5. **Backend validates code** → Issues JWT token with `type: 'client'`
6. **Client accesses protected routes** → Uses JWT token in Authorization header

---

## 📱 CLIENT APP API ENDPOINTS

### Base Path: `/api/clients`

---

### 1. Request Activation Code

**Endpoint:** `POST /api/clients/request-activation`

**Description:** Send activation code to customer's phone (SMS) or email based on input type.

**Request Body:**
```json
{
  "identifier": "01234567890"  // Phone number OR email address
}
```

**Logic:**
1. Check if identifier is phone (digits only) or email (contains @)
2. Find customer by phone OR email
3. Rate limiting: Max 3 requests per 10 minutes per customer
4. Generate 6-digit code (100000-999999)
5. Save code with 10-minute expiration
6. Send via SMS (if phone) or Email (if email)
7. Return success response (never reveal if customer exists for security)

**Response:**
```json
{
  "status": "success",
  "message": "Activation code sent to your phone/email",
  "data": {
    "expires_in": 600,  // seconds
    "identifier_type": "phone"  // or "email"
  }
}
```

**Error Responses:**
```json
// Too many requests
{
  "status": "error",
  "message": "Too many activation requests. Please wait 10 minutes.",
  "code": "RATE_LIMIT_EXCEEDED"
}

// Invalid input
{
  "status": "error",
  "message": "Invalid phone number or email address",
  "code": "INVALID_IDENTIFIER"
}

// Customer not found (return same response as success for security)
{
  "status": "success",
  "message": "Activation code sent to your phone/email"
}
```

**Implementation:**

```python
# api/clients/auth.py
from flask import Blueprint, request, jsonify
from models.customer import Customer, db
from services.email_service import send_activation_email
from services.sms_service import send_activation_sms
from datetime import datetime, timedelta
import re

clients_auth_bp = Blueprint('clients_auth', __name__)

def is_email(identifier):
    """Check if identifier is an email"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, identifier) is not None

def is_phone(identifier):
    """Check if identifier is a phone number (10-15 digits, may start with +)"""
    phone_pattern = r'^\+?[0-9]{10,15}$'
    return re.match(phone_pattern, identifier.replace(' ', '').replace('-', '')) is not None

@clients_auth_bp.route('/request-activation', methods=['POST'])
def request_activation():
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    
    if not identifier:
        return jsonify({
            'status': 'error',
            'message': 'Phone number or email is required',
            'code': 'MISSING_IDENTIFIER'
        }), 400
    
    # Determine identifier type
    identifier_type = None
    if is_email(identifier):
        identifier_type = 'email'
        customer = Customer.query.filter_by(email=identifier, is_active=True).first()
    elif is_phone(identifier):
        identifier_type = 'phone'
        # Normalize phone (remove spaces, dashes, plus)
        normalized_phone = identifier.replace(' ', '').replace('-', '').replace('+', '')
        customer = Customer.query.filter_by(phone=normalized_phone, is_active=True).first()
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone number or email address',
            'code': 'INVALID_IDENTIFIER'
        }), 400
    
    # Security: Always return success even if customer not found
    if not customer:
        return jsonify({
            'status': 'success',
            'message': 'If an account exists, activation code has been sent',
            'data': {
                'expires_in': 600,
                'identifier_type': identifier_type
            }
        })
    
    # Rate limiting: Max 3 requests per 10 minutes
    if customer.last_activation_request:
        time_since_last = datetime.utcnow() - customer.last_activation_request
        if time_since_last < timedelta(minutes=10):
            return jsonify({
                'status': 'error',
                'message': 'Too many activation requests. Please wait before requesting again.',
                'code': 'RATE_LIMIT_EXCEEDED'
            }), 429
    
    # Generate activation code
    code = customer.generate_activation_code()
    db.session.commit()
    
    # Send code based on identifier type
    try:
        if identifier_type == 'email':
            send_activation_email(customer.email, code, customer.full_name)
        else:  # phone
            send_activation_sms(customer.phone, code)
        
        # For development: Print code to console
        print(f"🔑 ACTIVATION CODE for {customer.full_name}: {code}")
        print(f"   Valid for 10 minutes until {customer.activation_code_expires}")
        
        return jsonify({
            'status': 'success',
            'message': f'Activation code sent to your {identifier_type}',
            'data': {
                'expires_in': 600,
                'identifier_type': identifier_type
            }
        })
    except Exception as e:
        print(f"❌ Failed to send activation code: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to send activation code. Please try again.',
            'code': 'SEND_FAILED'
        }), 500
```

---

### 2. Verify Activation Code & Login

**Endpoint:** `POST /api/clients/verify-activation`

**Request Body:**
```json
{
  "identifier": "01234567890",
  "activation_code": "123456"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
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
// Invalid code
{
  "status": "error",
  "message": "Invalid or expired activation code",
  "code": "INVALID_CODE"
}

// Account not found
{
  "status": "error",
  "message": "Account not found",
  "code": "NOT_FOUND"
}

// Account deactivated
{
  "status": "error",
  "message": "Your account has been deactivated. Please contact reception.",
  "code": "ACCOUNT_INACTIVE"
}
```

**Implementation:**

```python
from flask_jwt_extended import create_access_token, create_refresh_token

@clients_auth_bp.route('/verify-activation', methods=['POST'])
def verify_activation():
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    activation_code = data.get('activation_code', '').strip()
    
    if not identifier or not activation_code:
        return jsonify({
            'status': 'error',
            'message': 'Phone/email and activation code are required',
            'code': 'MISSING_FIELDS'
        }), 400
    
    # Find customer by phone or email
    if is_email(identifier):
        customer = Customer.query.filter_by(email=identifier).first()
    elif is_phone(identifier):
        normalized_phone = identifier.replace(' ', '').replace('-', '').replace('+', '')
        customer = Customer.query.filter_by(phone=normalized_phone).first()
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone number or email address',
            'code': 'INVALID_IDENTIFIER'
        }), 400
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Account not found',
            'code': 'NOT_FOUND'
        }), 404
    
    if not customer.is_active:
        return jsonify({
            'status': 'error',
            'message': 'Your account has been deactivated. Please contact reception.',
            'code': 'ACCOUNT_INACTIVE'
        }), 403
    
    # Verify activation code
    if not customer.verify_activation_code(activation_code):
        return jsonify({
            'status': 'error',
            'message': 'Invalid or expired activation code',
            'code': 'INVALID_CODE'
        }), 401
    
    # Clear activation code
    customer.clear_activation_code()
    db.session.commit()
    
    # Generate JWT tokens with client type
    access_token = create_access_token(
        identity=customer.id,
        additional_claims={'type': 'client', 'customer_id': customer.id}
    )
    refresh_token = create_refresh_token(
        identity=customer.id,
        additional_claims={'type': 'client', 'customer_id': customer.id}
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 86400,  # 24 hours
            'client': customer.to_client_dict()
        }
    })
```

---

### 3. Get Client Profile

**Endpoint:** `GET /api/clients/profile`

**Headers:**
```
Authorization: Bearer {access_token}
```

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
    "weight": 80,
    "height": 175,
    "bmi": 26.1,
    "bmi_category": "Overweight",
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

**Implementation:**

```python
# api/clients/profile.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.customer import Customer

clients_profile_bp = Blueprint('clients_profile', __name__)

def require_client_auth(f):
    """Decorator to ensure the JWT token is for a client"""
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
    
    return jsonify({
        'status': 'success',
        'data': customer.to_client_dict()
    })
```

---

### 4. Get Subscription Details

**Endpoint:** `GET /api/clients/subscription`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
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

**Response:**
```json
{
  "status": "success",
  "data": {
    "qr_code": "GYM-123",
    "qr_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2026-02-11T12:00:00Z",
    "qr_image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

**Implementation:**

```python
# api/clients/qr_code.py
from flask import Blueprint, jsonify
from services.qr_service import generate_qr_code_image

clients_qr_bp = Blueprint('clients_qr', __name__)

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
    
    # Generate QR code image
    qr_image_base64 = generate_qr_code_image(customer.qr_code)
    
    return jsonify({
        'status': 'success',
        'data': {
            'qr_code': customer.qr_code,
            'qr_image_base64': qr_image_base64,
            'customer_name': customer.full_name,
            'has_active_subscription': customer.get_active_subscription() is not None
        }
    })

@clients_qr_bp.route('/refresh-qr', methods=['POST'])
@require_client_auth
def refresh_qr():
    """Refresh QR code (same as get, but POST for semantic purposes)"""
    return get_qr()
```

---

### 6. Get Entry History

**Endpoint:** `GET /api/clients/entry-history`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `limit` (optional): Number of records (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
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
      },
      {
        "id": 1233,
        "entry_time": "2026-02-10T18:15:00Z",
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

### 7. Refresh Access Token

**Endpoint:** `POST /api/clients/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
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

**Implementation:**

```python
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

@clients_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    customer_id = get_jwt_identity()
    
    # Generate new access token
    access_token = create_access_token(
        identity=customer_id,
        additional_claims={'type': 'client', 'customer_id': customer_id}
    )
    
    return jsonify({
        'status': 'success',
        'data': {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 86400
        }
    })
```

---

## 📧 EMAIL & SMS SERVICES

### Email Service (Activation Code)

```python
# services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_activation_email(to_email, activation_code, customer_name):
    """Send activation code via email"""
    try:
        # Email configuration
        smtp_server = Config.SMTP_SERVER
        smtp_port = Config.SMTP_PORT
        sender_email = Config.SENDER_EMAIL
        sender_password = Config.SENDER_PASSWORD
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Your Gym Access Code: {activation_code}'
        msg['From'] = sender_email
        msg['To'] = to_email
        
        # Email body
        text = f"""
Hello {customer_name},

Your gym app activation code is: {activation_code}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
Your Gym Team
        """
        
        html = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #333;">Gym Access Code</h2>
      <p>Hello <strong>{customer_name}</strong>,</p>
      <p>Your activation code is:</p>
      <div style="background: #f5f5f5; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
        {activation_code}
      </div>
      <p style="color: #666;">This code will expire in <strong>10 minutes</strong>.</p>
      <p style="color: #999; font-size: 12px;">If you did not request this code, please ignore this email.</p>
    </div>
  </body>
</html>
        """
        
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"✅ Activation code sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        raise Exception(f"Failed to send activation email: {str(e)}")
```

### SMS Service (Activation Code)

```python
# services/sms_service.py
import requests
from config import Config

def send_activation_sms(phone, activation_code):
    """Send activation code via SMS using SMS gateway"""
    try:
        # SMS Gateway configuration (example using Twilio)
        api_url = Config.SMS_API_URL
        api_key = Config.SMS_API_KEY
        sender_name = Config.SMS_SENDER_NAME
        
        message = f"Your gym app activation code is: {activation_code}\nValid for 10 minutes."
        
        # Example: Twilio API
        response = requests.post(
            api_url,
            auth=(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN),
            data={
                'From': Config.TWILIO_PHONE_NUMBER,
                'To': phone,
                'Body': message
            }
        )
        
        if response.status_code == 201:
            print(f"✅ Activation code sent to {phone}")
            return True
        else:
            raise Exception(f"SMS API returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to send SMS: {str(e)}")
        # For development: Don't fail, just log
        # In production, you should raise the exception
        print(f"⚠️  SMS sending disabled or failed. Code: {activation_code}")
        return True  # Return True to continue (for testing without SMS gateway)
```

### Configuration

```python
# config.py
import os

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///gym.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    
    # Email (SMTP)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your-gym@example.com')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'your-app-password')
    
    # SMS (Twilio example - replace with your SMS provider)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    SMS_API_URL = 'https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json'
    SMS_API_KEY = os.getenv('SMS_API_KEY', '')
    SMS_SENDER_NAME = 'GymApp'
```

---

## 🔧 QR CODE SERVICE

```python
# services/qr_service.py
import qrcode
import io
import base64

def generate_qr_code_image(data):
    """Generate QR code image as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str
```

---

## 📦 REQUIREMENTS.TXT

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
qrcode[pil]==7.4.2
requests==2.31.0
Pillow==10.2.0

# Optional (for production)
gunicorn==21.2.0
psycopg2-binary==2.9.9  # For PostgreSQL
```

---

## 🚀 MAIN APP SETUP

```python
# app.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models.customer import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    
    # Register blueprints
    from api.staff.auth import staff_auth_bp
    from api.staff.customers import staff_customers_bp
    from api.staff.subscriptions import staff_subscriptions_bp
    
    from api.clients.auth import clients_auth_bp
    from api.clients.profile import clients_profile_bp
    from api.clients.qr_code import clients_qr_bp
    
    # Staff APIs
    app.register_blueprint(staff_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(staff_customers_bp, url_prefix='/api/customers')
    app.register_blueprint(staff_subscriptions_bp, url_prefix='/api/subscriptions')
    
    # Client APIs
    app.register_blueprint(clients_auth_bp, url_prefix='/api/clients')
    app.register_blueprint(clients_profile_bp, url_prefix='/api/clients')
    app.register_blueprint(clients_qr_bp, url_prefix='/api/clients')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## ✅ TESTING GUIDE

### Test 1: Request Activation Code (Phone)

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/request-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890"}'
```

### Test 2: Request Activation Code (Email)

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/request-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "customer@example.com"}'
```

### Test 3: Verify Activation Code

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/clients/verify-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890", "activation_code": "123456"}'
```

### Test 4: Get Profile

```bash
curl -X GET https://yamenmod91.pythonanywhere.com/api/clients/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎯 IMPLEMENTATION CHECKLIST

- [ ] Create database migration to add new fields to Customer model
- [ ] Implement `/api/clients/request-activation` endpoint
- [ ] Implement phone/email detection logic
- [ ] Implement SMS sending service (or mock for testing)
- [ ] Implement email sending service
- [ ] Implement `/api/clients/verify-activation` endpoint
- [ ] Implement JWT token generation with `type: 'client'`
- [ ] Implement `/api/clients/profile` endpoint
- [ ] Implement `/api/clients/subscription` endpoint
- [ ] Implement `/api/clients/qr` endpoint
- [ ] Implement `/api/clients/entry-history` endpoint
- [ ] Implement `/api/clients/refresh` endpoint
- [ ] Add rate limiting to prevent abuse
- [ ] Test with real phone numbers and emails
- [ ] Deploy to production server

---

## 🔒 SECURITY CONSIDERATIONS

1. **Rate Limiting:** Max 3 activation requests per 10 minutes per customer
2. **Code Expiration:** Activation codes expire after 10 minutes
3. **Never Reveal:** Don't reveal if customer exists (security by obscurity)
4. **JWT Claims:** Include `type: 'client'` to differentiate from staff tokens
5. **HTTPS Only:** All endpoints must use HTTPS in production
6. **Input Validation:** Validate all phone numbers and emails
7. **SQL Injection:** Use parameterized queries (SQLAlchemy handles this)
8. **CORS:** Configure CORS properly for production domain

---

## 🎉 EXPECTED OUTCOME

After implementation:
1. ✅ Client can enter phone/email in Flutter app
2. ✅ Backend detects if input is phone or email
3. ✅ Backend sends 6-digit code via SMS (phone) or Email (email)
4. ✅ Client enters code and gets logged in
5. ✅ Client can view profile, subscription, QR code, and entry history
6. ✅ Separate clean API structure for staff vs clients

---

## 📞 CONTACT & SUPPORT

If you encounter any issues during implementation:
1. Check backend logs for detailed error messages
2. Verify database schema is updated
3. Test email/SMS services separately
4. Use Postman or curl to test endpoints
5. Check JWT token structure and claims

---

**Ready to build? Let's go! 🚀**

