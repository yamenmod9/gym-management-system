# 🔧 BACKEND FIX: Customer Registration Branch Validation

**Date:** February 16, 2026  
**Priority:** CRITICAL  
**Issue:** Receptionists cannot register customers even for their own branch

---

## 🚨 PROBLEM

The backend is **incorrectly rejecting** customer registration requests with error:
```json
{
  "error": "Cannot register customer for another branch",
  "success": false
}
```

**What's happening:**
- Receptionist at Branch 1 tries to register customer for Branch 1
- Flutter app correctly sends `branch_id: 1`
- Receptionist's JWT token has `branch_id: 1`
- Backend incorrectly thinks this is "another branch"

**Root Cause:**
Backend validation logic has incorrect comparison or strict equality check that fails even when branch IDs match.

---

## ✅ REQUIRED FIX

### Current Request from Flutter (CORRECT)

```json
POST /api/customers/register
Authorization: Bearer {receptionist_token_with_branch_id_1}

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
  "bmr": 1750.0,
  "daily_calories": 2450.0,
  "branch_id": 1  ← This matches the receptionist's branch!
}
```

### Fix the Backend Validation

**File:** `app.py` or `routes/customer_routes.py`

**BEFORE (WRONG):**
```python
@app.route('/api/customers/register', methods=['POST'])
@jwt_required()
def register_customer():
    current_user = get_jwt_identity()
    data = request.json
    
    staff_role = current_user.get('role', '').lower()
    staff_branch_id = current_user.get('branch_id')
    requested_branch_id = data.get('branch_id')
    
    # ❌ THIS IS TOO STRICT - BLOCKS EVEN SAME BRANCH
    if staff_role in ['receptionist', 'manager']:
        if staff_branch_id != requested_branch_id:
            return jsonify({
                'success': False,
                'error': 'Cannot register customer for another branch'
            }), 403
```

**AFTER (CORRECT):**
```python
@app.route('/api/customers/register', methods=['POST'])
@jwt_required()
def register_customer():
    current_user = get_jwt_identity()
    data = request.json
    
    staff_role = current_user.get('role', '').lower()
    staff_branch_id = current_user.get('branch_id')
    requested_branch_id = data.get('branch_id')
    
    # ✅ FIX: Ensure proper type comparison
    # Convert both to int for comparison
    staff_branch_id = int(staff_branch_id) if staff_branch_id is not None else None
    requested_branch_id = int(requested_branch_id) if requested_branch_id is not None else None
    
    # Only non-owners must register for their own branch
    if staff_role in ['receptionist', 'manager', 'accountant']:
        if staff_branch_id is None or requested_branch_id is None:
            return jsonify({
                'success': False,
                'error': 'Branch ID is required'
            }), 400
        
        # ✅ FIX: Allow same-branch registration
        if staff_branch_id != requested_branch_id:
            return jsonify({
                'success': False,
                'error': f'You can only register customers for your own branch (Branch {staff_branch_id})'
            }), 403
        # ✅ If branch IDs match, continue with registration below
    
    # Owners can register for any branch
    elif staff_role == 'owner':
        if requested_branch_id is None:
            return jsonify({
                'success': False,
                'error': 'Branch ID is required'
            }), 400
    
    # Check if phone already exists
    existing_customer = Customer.query.filter_by(phone=data.get('phone')).first()
    if existing_customer:
        return jsonify({
            'success': False,
            'error': 'A customer with this phone number already exists'
        }), 400
    
    # Generate temporary password
    temp_password = generate_temp_password()  # e.g., "AB12CD" format
    
    # Calculate birth date from age
    from datetime import datetime, timedelta
    birth_year = datetime.now().year - int(data.get('age', 25))
    date_of_birth = datetime(birth_year, 1, 1).date()
    
    # Create customer
    new_customer = Customer(
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        email=data.get('email'),
        branch_id=requested_branch_id,
        gender=data.get('gender'),
        date_of_birth=date_of_birth,
        weight=float(data.get('weight', 0)),
        height=float(data.get('height', 0)),
        bmi=float(data.get('bmi', 0)),
        bmi_category=data.get('bmi_category', 'Normal'),
        bmr=float(data.get('bmr', 0)),
        daily_calories=float(data.get('daily_calories', 0)),
        password_hash=bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()),
        temp_password=temp_password,
        password_changed=False,
        is_active=True
    )
    
    db.session.add(new_customer)
    db.session.flush()  # Get the customer ID
    
    # Generate QR code
    new_customer.qr_code = f"customer_id:{new_customer.id}"
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Customer registered successfully',
        'data': {
            'customer': {
                'id': new_customer.id,
                'full_name': new_customer.full_name,
                'phone': new_customer.phone,
                'email': new_customer.email,
                'branch_id': new_customer.branch_id,
                'qr_code': new_customer.qr_code,
                'temp_password': temp_password,
                'password_changed': False,
                'is_active': True
            }
        }
    }), 201
```

---

## 🔍 DEBUGGING TIPS

Add these debug prints to help identify the issue:

```python
@app.route('/api/customers/register', methods=['POST'])
@jwt_required()
def register_customer():
    current_user = get_jwt_identity()
    data = request.json
    
    # DEBUG: Print what we're comparing
    print("=== REGISTRATION DEBUG ===")
    print(f"Current User: {current_user}")
    print(f"Staff Role: {current_user.get('role')}")
    print(f"Staff Branch ID (raw): {current_user.get('branch_id')} (type: {type(current_user.get('branch_id'))})")
    print(f"Requested Branch ID (raw): {data.get('branch_id')} (type: {type(data.get('branch_id'))})")
    
    staff_branch_id = int(current_user.get('branch_id')) if current_user.get('branch_id') is not None else None
    requested_branch_id = int(data.get('branch_id')) if data.get('branch_id') is not None else None
    
    print(f"Staff Branch ID (converted): {staff_branch_id} (type: {type(staff_branch_id)})")
    print(f"Requested Branch ID (converted): {requested_branch_id} (type: {type(requested_branch_id)})")
    print(f"Are they equal? {staff_branch_id == requested_branch_id}")
    print("========================")
    
    # Continue with validation...
```

---

## 🧪 TESTING

### Test 1: Receptionist Registration (Should SUCCEED)

```bash
# Login as receptionist at Branch 1
curl -X POST http://localhost:5000/api/staff/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "receptionist1@dragonclub.com",
    "password": "password123"
  }'

# Save the token, then register customer
curl -X POST http://localhost:5000/api/customers/register \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01999999999",
    "email": "testcustomer@example.com",
    "gender": "male",
    "age": 25,
    "weight": 75.0,
    "height": 1.75,
    "bmi": 24.5,
    "branch_id": 1
  }'
```

**Expected Response (201):**
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "customer": {
      "id": 151,
      "full_name": "Test Customer",
      "phone": "01999999999",
      "qr_code": "customer_id:151",
      "temp_password": "AB12CD",
      "branch_id": 1
    }
  }
}
```

### Test 2: Receptionist Cross-Branch (Should FAIL)

```bash
curl -X POST http://localhost:5000/api/customers/register \
  -H "Authorization: Bearer {branch_1_receptionist_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01888888888",
    "branch_id": 2
  }'
```

**Expected Response (403):**
```json
{
  "success": false,
  "error": "You can only register customers for your own branch (Branch 1)"
}
```

### Test 3: Owner Any Branch (Should SUCCEED)

```bash
curl -X POST http://localhost:5000/api/customers/register \
  -H "Authorization: Bearer {owner_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01777777777",
    "branch_id": 3
  }'
```

**Expected Response (201):** Success

---

## 📝 COMMON ISSUES

### Issue 1: Type Mismatch
```python
# ❌ WRONG: Comparing int to string
if 1 != "1":  # This is TRUE (different types)

# ✅ CORRECT: Convert both to same type
if int(1) != int("1"):  # This is FALSE (same value)
```

### Issue 2: None Comparison
```python
# ❌ WRONG: None causes comparison issues
if None != 1:  # This is always TRUE

# ✅ CORRECT: Check for None first
if branch_id is None or branch_id != 1:
```

### Issue 3: JWT Identity Format
The JWT token might return branch_id as:
- Integer: `{'branch_id': 1}`
- String: `{'branch_id': "1"}`
- None: `{'branch_id': None}`

**Solution:** Always convert to int before comparison.

---

## ✅ VERIFICATION CHECKLIST

- [ ] Backend accepts same-branch registration
- [ ] Backend rejects cross-branch registration (non-owners)
- [ ] Backend allows owner to register for any branch
- [ ] Temporary password is generated correctly
- [ ] QR code is generated in format `customer_id:{id}`
- [ ] Response includes `temp_password` field
- [ ] Customer is added to database
- [ ] No type comparison errors in logs

---

## 📌 SUMMARY

**The Fix:**
1. Convert both branch IDs to integers before comparison
2. Check for None values explicitly
3. Allow registration when branch IDs match
4. Only block when branch IDs are different (for non-owners)

**Expected Behavior:**
- ✅ Receptionist at Branch 1 → Register for Branch 1: SUCCESS
- ❌ Receptionist at Branch 1 → Register for Branch 2: BLOCKED
- ✅ Owner → Register for any branch: SUCCESS

---

**END OF FIX INSTRUCTIONS**

