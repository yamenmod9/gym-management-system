# 🔧 Backend Fix Request for Flask Gym Management API

## 🚨 CRITICAL ISSUE

My Flutter gym management app is getting a **"Resource not found"** error when trying to register new customers. I need you to analyze my Flask backend and fix the registration endpoint.

---

## 📱 CURRENT SITUATION

### What Works ✅
- Login endpoint returns correct data structure
- Authentication with JWT tokens
- User roles are defined in database
- Other API endpoints functioning

### What's Broken ❌
1. **Registration endpoint returns 404** - `/api/customers/register` not found
2. **Role strings might be inconsistent** - Need exact role names validated

---

## 🎯 EXACT REQUIREMENTS

### 1. Registration Endpoint Must:

**URL**: `POST /api/customers/register`

**Authentication**: Requires Bearer JWT token (from reception/front_desk user)

**Request Body**:
```json
{
  "full_name": "John Doe",
  "phone": "01234567890",
  "email": "john@example.com",
  "gender": "male",
  "age": 25,
  "weight": 75.0,
  "height": 1.75,
  "bmi": 24.5,
  "bmi_category": "Normal",
  "bmr": 1700.0,
  "daily_calories": 2500.0,
  "branch_id": 1
}
```

**Success Response (201 Created)**:
```json
{
  "message": "Customer registered successfully",
  "customer": {
    "id": 123,
    "full_name": "John Doe",
    "phone": "01234567890",
    "email": "john@example.com",
    "gender": "male",
    "age": 25,
    "weight": 75.0,
    "height": 1.75,
    "bmi": 24.5,
    "bmi_category": "Normal",
    "bmr": 1700.0,
    "daily_calories": 2500.0,
    "qr_code": "GYM-123",
    "branch_id": 1,
    "is_active": true,
    "created_at": "2026-02-09T12:00:00Z"
  }
}
```

**Important**: The `qr_code` field MUST be generated as: `f"GYM-{customer.id}"`

### 2. Role Strings Must Be Exact:

The login endpoint MUST return these **exact lowercase strings with underscores**:

| Role Name | Exact String | Has branch_id? |
|-----------|--------------|----------------|
| Owner | `owner` | No (null) |
| Branch Manager | `branch_manager` | Yes |
| Reception | `front_desk` | Yes |
| Central Accountant | `central_accountant` | No (null) |
| Branch Accountant | `branch_accountant` | Yes |

**Critical**: Do NOT use `'reception'` - must be `'front_desk'`

### 3. Login Response Must Match:

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi...",
    "user": {
      "id": 5,
      "username": "reception1",
      "email": "reception1@gymchain.com",
      "full_name": "Sara Mohamed",
      "phone": "0202220001",
      "role": "front_desk",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "is_active": true,
      "created_at": "2026-02-08T21:09:47.596924",
      "last_login": null
    }
  },
  "message": "Login successful"
}
```

---

## 🧪 TEST ACCOUNTS

These accounts exist in your database. Verify they return correct role strings:

```python
# Test with these credentials
test_accounts = [
    {"username": "owner", "password": "owner123", "expected_role": "owner", "branch_id": None},
    {"username": "manager1", "password": "manager123", "expected_role": "branch_manager", "branch_id": 1},
    {"username": "reception1", "password": "reception123", "expected_role": "front_desk", "branch_id": 1},
    {"username": "reception3", "password": "reception123", "expected_role": "front_desk", "branch_id": 3},
    {"username": "accountant1", "password": "accountant123", "expected_role": "central_accountant", "branch_id": None},
    {"username": "baccountant1", "password": "accountant123", "expected_role": "branch_accountant", "branch_id": 1}
]
```

---

## 📋 WHAT I NEED FROM YOU

### Task 1: Analyze My Backend Structure
Look at my Flask backend code and identify:
1. Where routes are defined (app.py? blueprints?)
2. How authentication is handled
3. Where the customer registration endpoint should be
4. Why it's returning 404

### Task 2: Fix Registration Endpoint
Provide complete, working code for:
1. The route definition
2. The controller/handler function
3. QR code generation logic
4. Proper error handling
5. Database operations

### Task 3: Verify Role Strings
Check all places where user roles are set/returned:
1. User model definition
2. Login endpoint response
3. Registration/creation of users
4. Any role-checking decorators

### Task 4: Provide Test Commands
Give me exact cURL commands to test:
1. Registration endpoint (after getting token)
2. Login for each role
3. Verify QR code generation

---

## 🗂️ EXPECTED DATABASE SCHEMA

### customers table:
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100),
    gender VARCHAR(10) NOT NULL,
    age INTEGER NOT NULL,
    weight FLOAT NOT NULL,
    height FLOAT NOT NULL,
    bmi FLOAT,
    bmi_category VARCHAR(20),
    bmr FLOAT,
    daily_calories FLOAT,
    qr_code VARCHAR(50) UNIQUE,
    branch_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);
```

### users table (has role column):
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL,  -- Must be one of the 5 exact strings
    branch_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);
```

---

## 🔍 COMMON ISSUES TO CHECK

### Issue 1: Route Not Registered
```python
# Check if customers blueprint is registered
from flask import Blueprint

customers_bp = Blueprint('customers', __name__)

# In app.py or __init__.py
app.register_blueprint(customers_bp, url_prefix='/api/customers')
```

### Issue 2: Route Path Wrong
```python
# ❌ WRONG
@app.route('/customers/register', methods=['POST'])

# ❌ WRONG
@customers_bp.route('/register', methods=['POST'])  # if blueprint has wrong prefix

# ✅ CORRECT (option 1)
@app.route('/api/customers/register', methods=['POST'])

# ✅ CORRECT (option 2)
@customers_bp.route('/register', methods=['POST'])  # if blueprint url_prefix='/api/customers'
```

### Issue 3: Missing QR Code Generation
```python
# After creating customer object
new_customer = Customer(
    full_name=data['full_name'],
    phone=data['phone'],
    # ... other fields
)
db.session.add(new_customer)
db.session.flush()  # Get the ID

# Generate QR code using the ID
new_customer.qr_code = f"GYM-{new_customer.id}"
db.session.commit()
```

### Issue 4: Role String Inconsistency
```python
# ❌ BAD - Different formats
user.role = 'Reception'
user.role = 'RECEPTION'
user.role = 'reception'

# ✅ GOOD - Exact match with Flutter
user.role = 'front_desk'
```

---

## ✅ DELIVERABLES I NEED

1. **Complete Registration Route Code**
   - Full function with all imports
   - Error handling
   - QR code generation
   - Proper response format

2. **Role Verification Code**
   - Show me where roles are defined
   - Any changes needed to match exact strings
   - Updated login response code

3. **Test Commands**
   - cURL command to get token
   - cURL command to register customer
   - Expected responses

4. **Database Migrations** (if needed)
   - Any ALTER TABLE statements
   - Schema updates

5. **Deployment Instructions**
   - How to apply changes to PythonAnywhere
   - Any restarts needed

---

## 🚀 EXAMPLE WORKING CODE STRUCTURE

Here's what I expect the registration endpoint to look like:

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer, User
from datetime import datetime

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/register', methods=['POST'])
@jwt_required()
def register_customer():
    """
    Register a new customer (reception/front_desk only)
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if user has permission (optional - remove if not needed)
        if current_user.role not in ['front_desk', 'owner', 'branch_manager']:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'phone', 'gender', 'age', 'weight', 'height']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create customer
        new_customer = Customer(
            full_name=data['full_name'],
            phone=data['phone'],
            email=data.get('email'),
            gender=data['gender'],
            age=data['age'],
            weight=data['weight'],
            height=data['height'],
            bmi=data.get('bmi'),
            bmi_category=data.get('bmi_category'),
            bmr=data.get('bmr'),
            daily_calories=data.get('daily_calories'),
            branch_id=data.get('branch_id', current_user.branch_id),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_customer)
        db.session.flush()  # Get the ID
        
        # Generate QR code
        new_customer.qr_code = f"GYM-{new_customer.id}"
        
        db.session.commit()
        
        # Return response
        return jsonify({
            "message": "Customer registered successfully",
            "customer": {
                "id": new_customer.id,
                "full_name": new_customer.full_name,
                "phone": new_customer.phone,
                "email": new_customer.email,
                "gender": new_customer.gender,
                "age": new_customer.age,
                "weight": new_customer.weight,
                "height": new_customer.height,
                "bmi": new_customer.bmi,
                "bmi_category": new_customer.bmi_category,
                "bmr": new_customer.bmr,
                "daily_calories": new_customer.daily_calories,
                "qr_code": new_customer.qr_code,
                "branch_id": new_customer.branch_id,
                "is_active": new_customer.is_active,
                "created_at": new_customer.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
```

---

## 📞 API BASE URL

```
https://yamenmod91.pythonanywhere.com
```

All endpoints should be accessible at:
- Login: `POST /api/auth/login`
- Register: `POST /api/customers/register` ← **THIS IS BROKEN**
- Get Customers: `GET /api/customers`

---

## 🎯 SUCCESS CRITERIA

You've successfully fixed the backend when:

1. ✅ `curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register` returns 201 (not 404)
2. ✅ Response includes `qr_code` field in format `GYM-123`
3. ✅ All 6 test accounts return correct `role` strings on login
4. ✅ No "Resource not found" errors
5. ✅ Customer is saved to database with all fields

---

## 📝 PASTE YOUR BACKEND CODE HERE

Please share these files so I can analyze them:

1. `app.py` or `__init__.py` (main application)
2. `routes/customers.py` or relevant routes file
3. `routes/auth.py` (login endpoint)
4. `models.py` or `models/customer.py` and `models/user.py`
5. Any blueprint registration code

Once you share the code, I'll provide:
- ✅ Exact fixes needed
- ✅ Complete working code
- ✅ Test commands
- ✅ Deployment instructions

---

**PRIORITY**: 🔥 CRITICAL - App cannot register customers (core feature broken)

**TIMELINE**: Need fix ASAP - Flutter app is ready and waiting

**YOUR TASK**: Analyze my backend code, identify the issue, and provide complete working solution with test commands.

---

## 🆘 QUICK CHECKLIST FOR YOU

Before responding, please verify:

- [ ] Registration endpoint exists and is accessible
- [ ] Route is properly registered (blueprint or direct)
- [ ] QR code generation uses format `GYM-{id}`
- [ ] All 5 role strings match exact format (lowercase with underscore)
- [ ] Response structure matches expected format
- [ ] Provided cURL commands to test everything
- [ ] Included deployment instructions

---

**I'm ready to share my backend code - please analyze it and fix the issues!**
