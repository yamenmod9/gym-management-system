# 🔧 BACKEND FIX: CLIENT LOGIN WITH PHONE OR EMAIL

## Current Situation

✅ **Working:** Client can login with phone number  
❌ **Not Working:** Client cannot login with email  

**Current Backend Endpoint:** `POST /api/client/auth/login`

**Current Behavior:**
```json
// Works:
{ "phone": "01234567890", "password": "ABC123" }

// Doesn't work:
{ "phone": "user@example.com", "password": "ABC123" }
```

## Required Fix

Update the backend to accept EITHER phone OR email in the login request.

---

## Backend Implementation (Python/Flask)

### Current Code (Needs Update):
```python
@app.route('/api/client/auth/login', methods=['POST'])
def client_login():
    data = request.get_json()
    phone = data.get('phone')  # Only accepts phone
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({
            'success': False,
            'error': 'Phone and password are required'
        }), 400
    
    # Find customer by phone only
    customer = Customer.query.filter_by(phone=phone).first()
    # ...
```

### Updated Code (Copy This):
```python
import re

def is_email(identifier):
    """Check if identifier is an email"""
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', identifier) is not None

def normalize_phone(phone):
    """Remove spaces, dashes, and plus signs from phone"""
    return re.sub(r'[\s\-\+]', '', phone)

@app.route('/api/client/auth/login', methods=['POST'])
def client_login():
    data = request.get_json()
    identifier = data.get('phone', '').strip()  # Can be phone or email
    password = data.get('password', '').strip()
    
    if not identifier or not password:
        return jsonify({
            'success': False,
            'error': 'Phone/email and password are required'
        }), 400
    
    # Find customer by phone OR email
    if is_email(identifier):
        # Login with email
        customer = Customer.query.filter_by(email=identifier).first()
    else:
        # Login with phone - normalize it first
        normalized_phone = normalize_phone(identifier)
        customer = Customer.query.filter(
            db.func.replace(db.func.replace(db.func.replace(
                Customer.phone, ' ', ''), '-', ''), '+', ''
            ) == normalized_phone
        ).first()
    
    if not customer:
        return jsonify({
            'success': False,
            'error': 'Invalid phone or password'
        }), 401
    
    # Verify password (existing logic)
    if not check_password_hash(customer.password_hash, password):
        return jsonify({
            'success': False,
            'error': 'Invalid phone or password'
        }), 401
    
    # Check if customer is active
    if not customer.is_active:
        return jsonify({
            'success': False,
            'error': 'Your account is inactive. Please contact reception.',
            'error_code': 'ACCOUNT_INACTIVE'
        }), 403
    
    # Generate JWT token
    access_token = create_access_token(
        identity=customer.id,
        additional_claims={'type': 'client', 'customer_id': customer.id},
        expires_delta=timedelta(days=7)  # 7 days for client app
    )
    
    # Get active subscription
    active_sub = customer.subscriptions.filter_by(status='active').first()
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 604800,  # 7 days in seconds
            'password_changed': customer.password_changed,
            'customer': {
                'id': customer.id,
                'full_name': customer.full_name,
                'phone': customer.phone,
                'email': customer.email,
                'qr_code': customer.qr_code,
                'branch_id': customer.branch_id,
                'branch_name': customer.branch.name if customer.branch else None,
                'has_active_subscription': active_sub is not None
            }
        }
    }), 200
```

---

## Testing After Update

### Test 1: Login with Phone
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"01234567890","password":"ABC123"}'
```

**Expected:** 
- ✅ 200 OK with access token (if credentials are valid)
- ✅ 401 with error message (if credentials are invalid)

### Test 2: Login with Email
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"customer@example.com","password":"ABC123"}'
```

**Expected:** 
- ✅ 200 OK with access token (if credentials are valid)
- ✅ 401 with error message (if credentials are invalid)

### Test 3: Login with Phone (Different Formats)
```bash
# With spaces
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"012 345 678 90","password":"ABC123"}'

# With dashes
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"012-345-678-90","password":"ABC123"}'

# With country code
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"+20 123 456 7890","password":"ABC123"}'
```

**Expected:** All should work (normalized to same phone number)

---

## Database Requirements

Make sure your Customer model has these fields:

```python
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    temporary_password = db.Column(db.String(20), nullable=True)  # For first-time login
    password_changed = db.Column(db.Boolean, default=False)  # Track if temp password was changed
    is_active = db.Column(db.Boolean, default=True)
    qr_code = db.Column(db.String(50), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    # ... other fields
```

### Migration Script (if fields are missing):

```python
from flask_migrate import upgrade

# Add to your migration file:
def upgrade():
    # Add new columns if they don't exist
    op.add_column('customers', sa.Column('temporary_password', sa.String(20), nullable=True))
    op.add_column('customers', sa.Column('password_changed', sa.Boolean(), default=False))
    op.add_column('customers', sa.Column('is_active', sa.Boolean(), default=True))
```

---

## Summary of Changes

### ✅ What This Fix Does:

1. **Accepts phone OR email** in the `phone` field
2. **Auto-detects** if input is email or phone
3. **Normalizes phone numbers** (removes spaces, dashes, +)
4. **Searches database** by email if it's an email, by normalized phone if it's a phone
5. **Returns proper errors** for invalid credentials
6. **Generates JWT token** valid for 7 days
7. **Returns customer data** including subscription status

### 📱 Frontend Impact:

**Frontend is already fixed!** The client app now:
- ✅ Sends requests to `/api/client/auth/login` (correct endpoint)
- ✅ Sends `phone` field (what backend expects)
- ✅ Works with both phone and email input
- ✅ Normalizes phone numbers before sending

---

## Checklist

After implementing this fix:

- [ ] Update the `client_login()` function in backend
- [ ] Add `is_email()` helper function
- [ ] Add `normalize_phone()` helper function
- [ ] Test login with phone number
- [ ] Test login with email address
- [ ] Test login with formatted phone (spaces/dashes)
- [ ] Deploy to production server
- [ ] Test from Flutter app

---

**Backend Developer:** Copy the "Updated Code" section above into your Flask app and test!

