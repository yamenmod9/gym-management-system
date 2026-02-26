# 🔧 BACKEND FIX REQUIRED - Customer First-Time Password Display

## Problem
Reception staff cannot see customer's first-time password in the customers list, even though:
- Backend has seeded customers with temporary passwords (format: AB12CD)
- Frontend is ready to display them
- Field shows "Not available" or "Not Set"

## Root Cause
The backend API endpoint `/api/customers` or `/api/staff/{branch_id}/customers` is NOT returning the `temporary_password` or `temp_password` field in the response.

## Current Frontend Code (Already Implemented)
File: `lib/features/reception/screens/customers_list_screen.dart`

```dart
// Line 179-180: Frontend correctly tries to extract temp password
final tempPassword = customer['temporary_password'] ?? 
                    customer['temp_password'] ?? 
                    'Not available';
final passwordChanged = customer['password_changed'] ?? false;

// Lines 270-274: Display logic
_buildCredentialRow(
  'Password',
  passwordChanged ? '••••••••' : tempPassword,  // Show temp password if not changed
  Icons.password,
  isPassword: true,
  showCopy: !passwordChanged,  // Allow copying if not changed
),
```

## Required Backend Fix

### API Endpoint to Modify:
- `GET /api/customers`
- `GET /api/staff/{branch_id}/customers`
- `GET /api/customers/{customer_id}`

### Required Changes:

#### 1. Add Field to Response
When a STAFF member (reception, manager, owner, accountant) requests customer data, include:

```json
{
  "id": 115,
  "full_name": "Mohamed Salem",
  "phone": "01077827638",
  "email": "customer1@example.com",
  "temporary_password": "RX04AF",  // ← ADD THIS FIELD
  "password_changed": false,       // ← ENSURE THIS IS INCLUDED
  "qr_code": "CUST-00115-002-ABC123",
  "branch_id": 1,
  ...other fields
}
```

#### 2. Security Rules
**IMPORTANT:** Only include `temporary_password` when:
- Requestor is a staff member (role: reception, manager, owner, accountant)
- Customer's `password_changed == false`
- If `password_changed == true`, omit the field or return `null`

#### 3. Database Schema (Verify These Fields Exist)
```sql
customers table:
  - temporary_password VARCHAR(6)  -- Format: AB12CD
  - password_changed BOOLEAN DEFAULT FALSE
```

### Example Backend Response (Python/Flask)

**Before Fix:**
```python
@app.route('/api/customers', methods=['GET'])
@jwt_required()
def get_customers():
    customers = Customer.query.all()
    return jsonify({
        'data': {
            'items': [customer.to_dict() for customer in customers]
        }
    })
```

**After Fix:**
```python
@app.route('/api/customers', methods=['GET'])
@jwt_required()
def get_customers():
    current_user = get_jwt_identity()
    is_staff = current_user.get('role') in ['owner', 'manager', 'reception', 'accountant']
    
    customers = Customer.query.all()
    customer_list = []
    
    for customer in customers:
        customer_dict = customer.to_dict()
        
        # Only include temp password for staff when password not changed
        if is_staff and not customer.password_changed:
            customer_dict['temporary_password'] = customer.temporary_password
        
        customer_list.append(customer_dict)
    
    return jsonify({
        'data': {
            'items': customer_list
        }
    })
```

## How to Verify Fix

### Step 1: Test API Response
```bash
# Login as reception
TOKEN="your_jwt_token_here"

# Check customer API includes temp password
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/customers | jq '.data.items[0] | {full_name, temporary_password, password_changed}'
```

**Expected Output:**
```json
{
  "full_name": "Mohamed Salem",
  "temporary_password": "RX04AF",
  "password_changed": false
}
```

### Step 2: Test in Frontend
1. Run staff app: `flutter run -t lib/main.dart`
2. Login as reception: `reception1` / `reception123`
3. Navigate to "All Customers"
4. Expand a customer card
5. Check "Client App Credentials" section

**Expected Display:**
```
🔒 Client App Credentials
Login: 01077827638
Password: RX04AF [Copy]
⚠️ First-time login - password not changed yet
```

### Step 3: Test After Customer Changes Password
After customer logs in and changes password:

**API Response Should Show:**
```json
{
  "full_name": "Mohamed Salem",
  "temporary_password": null,  // or field omitted entirely
  "password_changed": true
}
```

**Frontend Should Display:**
```
🔒 Client App Credentials
Login: 01077827638
Password: ••••••••
✅ Password has been changed by user
```

## Seed Data Verification

Ensure your `seed.py` includes:

```python
# Create customer with temporary password
customer = Customer(
    full_name="Mohamed Salem",
    phone="01077827638",
    email="customer1@example.com",
    temporary_password="RX04AF",  # Generate 6-char random: AB12CD format
    password_changed=False,  # Initially False
    ...other fields
)
```

### Password Generation Function:
```python
import random
import string

def generate_temp_password():
    """Generate 6-character temporary password: AB12CD format"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{letters}{numbers}{letters2}"
```

## Security Considerations

### ✅ DO:
- Return temp password only to staff members
- Only return when `password_changed == false`
- Log access to temporary passwords for audit
- Clear/null temp password after first login

### ❌ DON'T:
- Return temp password to the customer themselves via their API
- Include temp password in public endpoints
- Store passwords in plain text (use hashing for actual password)
- Keep temp password after it's been changed

## Alternative: Use QR Code Encoding

If you don't want to expose temp passwords via API, you can:

1. **Encode credentials in QR code:**
```python
qr_data = {
    'customer_id': customer.id,
    'temp_password': customer.temporary_password,
    'expires': datetime.now() + timedelta(days=30)
}
customer.qr_code = encrypt_json(qr_data)  # Encrypt and encode
```

2. **Reception scans QR to see credentials:**
- Scan QR code
- Decrypt to get temp password
- Display to reception
- Never transmitted over API

## Status

- ✅ Frontend implementation: **COMPLETE**
- ❌ Backend API response: **MISSING FIELD**
- ⏳ Action required: **Backend team to add `temporary_password` field to customer API response**

---

*Document Created: February 14, 2026*
*Status: Awaiting Backend Fix*

