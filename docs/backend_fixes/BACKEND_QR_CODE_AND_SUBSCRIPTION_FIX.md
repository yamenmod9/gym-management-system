# BACKEND FIX: QR CODE AND SUBSCRIPTION STATUS ISSUES

## Problem Summary

When clients try to scan QR codes in the gym, they encounter two critical issues:

1. **QR Code is null or empty** - The backend is not generating/storing QR codes for customers
2. **Subscription status shows "inactive"** - The login response does not include proper subscription status

## Required Backend Changes

### 1. Customer QR Code Generation

#### A. Database Migration (if not already done)

```sql
-- Ensure qr_code column exists
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS qr_code VARCHAR(255) UNIQUE;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_customers_qr_code ON customers(qr_code);

-- Generate QR codes for existing customers without them
UPDATE customers 
SET qr_code = CONCAT('customer_id:', id)
WHERE qr_code IS NULL OR qr_code = '';
```

#### B. Customer Registration - Auto-generate QR Code

When a new customer is created, automatically generate their QR code:

```python
# In customer registration endpoint
@app.route('/api/customers/register', methods=['POST'])
def register_customer():
    data = request.json
    
    # Create customer
    customer = Customer(
        full_name=data['full_name'],
        phone=data['phone'],
        # ... other fields ...
    )
    
    db.session.add(customer)
    db.session.flush()  # Get the customer ID
    
    # Generate QR code BEFORE commit
    customer.qr_code = f"customer_id:{customer.id}"
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'customer': customer.to_dict()
    }), 201
```

#### C. QR Code Regeneration Endpoint

```python
@app.route('/api/customers/<int:customer_id>/regenerate-qr', methods=['POST'])
@jwt_required()
def regenerate_qr_code(customer_id):
    """Regenerate QR code for a customer"""
    
    # Verify staff authentication
    current_user = get_jwt_identity()
    staff = Staff.query.filter_by(id=current_user['id']).first()
    
    if not staff:
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401
    
    # Get customer
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'success': False,
            'error': 'Customer not found'
        }), 404
    
    # Generate new QR code
    # Format: customer_id:{id}
    new_qr_code = f"customer_id:{customer_id}"
    
    # Update customer record
    customer.qr_code = new_qr_code
    customer.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'QR code regenerated successfully',
        'qr_code': new_qr_code,
        'data': {
            'customer_id': customer_id,
            'qr_code': new_qr_code,
            'generated_at': datetime.utcnow().isoformat()
        }
    }), 200
```

### 2. Client Login - Include Subscription Status

#### Current Problem

The client login endpoint returns customer data, but does NOT include active subscription status. This causes the app to show "inactive" even when the customer has an active subscription.

#### Solution: Update Login Response

```python
@app.route('/api/client/auth/login', methods=['POST'])
def client_login():
    """Client/Customer login endpoint"""
    
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    # Find customer
    customer = Customer.query.filter_by(phone=phone).first()
    
    if not customer:
        return jsonify({
            'success': False,
            'error': 'Invalid credentials'
        }), 401
    
    # Verify password
    if not customer.verify_password(password):
        return jsonify({
            'success': False,
            'error': 'Invalid credentials'
        }), 401
    
    # Check if customer is active
    if not customer.is_active:
        return jsonify({
            'success': False,
            'error': 'Account is inactive. Please contact reception.'
        }), 403
    
    # Generate QR code if missing
    if not customer.qr_code:
        customer.qr_code = f"customer_id:{customer.id}"
        db.session.commit()
    
    # Find ACTIVE subscription
    active_subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status='active'
    ).first()
    
    # Determine subscription status
    subscription_status = 'inactive'
    subscription_data = None
    
    if active_subscription:
        subscription_status = active_subscription.status
        subscription_data = {
            'id': active_subscription.id,
            'type': active_subscription.type,
            'status': active_subscription.status,
            'start_date': active_subscription.start_date.isoformat() if active_subscription.start_date else None,
            'end_date': active_subscription.end_date.isoformat() if active_subscription.end_date else None,
            'remaining_sessions': active_subscription.remaining_sessions,
            'service_name': active_subscription.service.name if active_subscription.service else None
        }
    
    # Generate JWT token
    access_token = create_access_token(
        identity={
            'id': customer.id,
            'type': 'customer',
            'branch_id': customer.branch_id
        },
        expires_delta=timedelta(days=30)
    )
    
    # Return response with ALL required fields
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': access_token,
        'password_changed': customer.password_changed,
        'customer': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,  # ← CRITICAL: Include QR code
            'branch_id': customer.branch_id,
            'branch_name': customer.branch.name if customer.branch else None,
            'is_active': customer.is_active,
            'subscription_status': subscription_status,  # ← CRITICAL: Include status
            'created_at': customer.created_at.isoformat() if customer.created_at else None,
            
            # Health metrics
            'height': customer.height,
            'weight': customer.weight,
            'bmi': customer.bmi,
            'bmi_category': customer.bmi_category,
            'bmr': customer.bmr,
            'daily_calories': customer.daily_calories,
        },
        'active_subscription': subscription_data  # ← CRITICAL: Include subscription details
    }), 200
```

### 3. Customer Detail Endpoint - Include QR Code

```python
@app.route('/api/customers/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Get customer details by ID"""
    
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'success': False,
            'error': 'Customer not found'
        }), 404
    
    # Generate QR code if missing
    if not customer.qr_code:
        customer.qr_code = f"customer_id:{customer.id}"
        db.session.commit()
    
    # Get active subscription
    active_subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status='active'
    ).first()
    
    return jsonify({
        'success': True,
        'customer': {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,  # ← Must include
            'branch_id': customer.branch_id,
            'is_active': customer.is_active,
            'subscription_status': active_subscription.status if active_subscription else 'inactive',
            # ... other fields ...
        }
    }), 200
```

### 4. QR Code Refresh Endpoint (for Client App)

```python
@app.route('/api/client/qr-code/refresh', methods=['POST'])
@jwt_required()
def refresh_qr_code():
    """Refresh QR code expiry time (frontend handles expiry)"""
    
    current_user = get_jwt_identity()
    customer_id = current_user['id']
    
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({
            'status': 'error',
            'message': 'Customer not found'
        }), 404
    
    # Ensure QR code exists
    if not customer.qr_code:
        customer.qr_code = f"customer_id:{customer_id}"
        db.session.commit()
    
    return jsonify({
        'status': 'success',
        'data': {
            'qr_code': customer.qr_code,
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
    }), 200
```

## QR Code Format Specification

**Standard Format:** `customer_id:{id}`

### Examples:
- Customer ID 1 → QR: `customer_id:1`
- Customer ID 115 → QR: `customer_id:115`
- Customer ID 999 → QR: `customer_id:999`

### Why This Format?

1. ✅ Matches QR scanner parsing logic in Flutter app
2. ✅ Easy to validate and extract customer ID
3. ✅ Human-readable for debugging
4. ✅ Unique per customer
5. ✅ Scanner supports multiple formats (customer_id:X, GYM-X, CUST-X)

## Testing Checklist

After implementing these changes:

### Backend Tests

- [ ] Create new customer → Verify `qr_code` field is populated
- [ ] GET /api/customers/{id} → Verify `qr_code` is in response
- [ ] POST /api/customers/{id}/regenerate-qr → Verify new QR code is generated
- [ ] POST /api/client/auth/login → Verify response includes:
  - [ ] `customer.qr_code` field
  - [ ] `customer.subscription_status` field
  - [ ] `active_subscription` object (if exists)

### Flutter App Tests

- [ ] Login as client → QR code screen shows valid QR
- [ ] QR code format is `customer_id:123`
- [ ] Status shows "Active" if subscription exists
- [ ] Staff app can scan QR code successfully
- [ ] Scanner correctly extracts customer ID
- [ ] Check-in dialog shows customer name and subscription

## Database Verification Queries

```sql
-- Check QR codes
SELECT id, full_name, qr_code 
FROM customers 
LIMIT 10;

-- Find customers without QR codes
SELECT COUNT(*) as missing_qr_codes
FROM customers 
WHERE qr_code IS NULL OR qr_code = '';

-- Check subscriptions
SELECT 
    c.id,
    c.full_name,
    s.status,
    s.type,
    s.remaining_sessions
FROM customers c
LEFT JOIN subscriptions s ON c.id = s.customer_id AND s.status = 'active'
LIMIT 10;
```

## Expected API Responses

### Client Login Success

```json
{
  "success": true,
  "token": "eyJhbGc...",
  "password_changed": true,
  "customer": {
    "id": 115,
    "full_name": "Adel Saad",
    "phone": "01025867870",
    "email": "customer115@example.com",
    "qr_code": "customer_id:115",
    "branch_id": 2,
    "branch_name": "Dragon Club",
    "is_active": true,
    "subscription_status": "active",
    "height": 172.0,
    "weight": 92.0,
    "bmi": 31.1,
    "bmi_category": "Obese"
  },
  "active_subscription": {
    "id": 45,
    "type": "coins",
    "status": "active",
    "remaining_sessions": 15,
    "end_date": "2026-03-15T00:00:00"
  }
}
```

### QR Code Regeneration Success

```json
{
  "success": true,
  "message": "QR code regenerated successfully",
  "qr_code": "customer_id:115",
  "data": {
    "customer_id": 115,
    "qr_code": "customer_id:115",
    "generated_at": "2026-02-15T14:30:00"
  }
}
```

## Priority

🔴 **CRITICAL** - These fixes are required for the QR code scanning feature to work.

---

## Summary of Changes

1. ✅ Add `qr_code` column to customers table (if missing)
2. ✅ Auto-generate QR codes during customer registration
3. ✅ Add QR code regeneration endpoint
4. ✅ Update client login to include `qr_code` and `subscription_status`
5. ✅ Update customer detail endpoint to include `qr_code`
6. ✅ Add QR code refresh endpoint for client app
7. ✅ Backfill QR codes for existing customers

Implement these changes and the QR code scanning will work correctly!

