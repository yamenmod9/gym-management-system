# 🎯 BACKEND PROMPT FOR CLAUDE SONNET 4.5

## CRITICAL ISSUE TO FIX

The Flutter app is ready but the backend API is missing ONE CRITICAL FIELD that breaks the reception workflow.

---

## ISSUE: Temporary Password Not Visible to Reception

### Current Problem:
Reception staff registers a new customer, but cannot see the temporary password to give to the customer.

### Root Cause:
The backend endpoint `/api/customers` does NOT return the `temporary_password` field.

### Required Fix:

#### 1. Add Fields to Customer Model
```python
class Customer(db.Model):
    # ...existing fields...
    temporary_password = db.Column(db.String(6), nullable=False)  # Format: AB12CD
    password_changed = db.Column(db.Boolean, default=False)
```

#### 2. Update Customer API Response
```python
# In customers.py or wherever customer routes are defined

@app.route('/api/customers', methods=['GET'])
@jwt_required()
def get_customers():
    current_user = get_jwt_identity()
    is_staff = current_user.get('role') in ['owner', 'manager', 'reception', 'accountant']
    
    customers = Customer.query.all()
    customer_list = []
    
    for customer in customers:
        customer_dict = customer.to_dict()
        
        # ⭐ CRITICAL: Include temp password for staff when password not changed
        if is_staff and not customer.password_changed:
            customer_dict['temporary_password'] = customer.temporary_password
        
        customer_dict['password_changed'] = customer.password_changed
        customer_list.append(customer_dict)
    
    return jsonify({'data': {'items': customer_list}})


@app.route('/api/customers', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.json
    
    # Generate temporary password
    import random, string
    letters1 = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    temp_password = f"{letters1}{numbers}{letters2}"  # e.g., "RX04AF"
    
    customer = Customer(
        full_name=data['full_name'],
        phone=data['phone'],
        email=data.get('email'),
        temporary_password=temp_password,  # ⭐ SAVE THIS
        password_changed=False,            # ⭐ INITIALLY FALSE
        # ...other fields...
    )
    
    # Set hashed password to temp_password initially
    customer.set_password(temp_password)
    
    db.session.add(customer)
    db.session.commit()
    
    # ⭐ CRITICAL: Return temp password in response
    return jsonify({
        'data': {
            **customer.to_dict(),
            'temporary_password': temp_password  # ⭐ MUST RETURN THIS
        }
    }), 201
```

#### 3. Update seed.py
```python
def generate_temp_password():
    import random, string
    letters1 = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{letters1}{numbers}{letters2}"

# Create 150 customers with temp passwords
for i in range(1, 151):
    branch_id = ((i - 1) // 50) + 1
    temp_pass = generate_temp_password()
    
    customer = Customer(
        full_name=f"Customer {i}",
        phone=f"010{str(i).zfill(8)}",
        email=f"customer{i}@example.com",
        temporary_password=temp_pass,   # ⭐ MUST SET THIS
        password_changed=False,          # ⭐ MUST SET THIS
        branch_id=branch_id,
        # ...other fields...
    )
    customer.set_password(temp_pass)  # Hash the temp password
    db.session.add(customer)

# Add specific test customers for easy testing
test_customers = [
    {
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "email": "mohamed@example.com",
        "temporary_password": "RX04AF",
        "password_changed": False,
        "branch_id": 1
    },
    {
        "full_name": "Layla Rashad",
        "phone": "01022981052",
        "email": "layla@example.com",
        "temporary_password": "SI19IC",
        "password_changed": False,
        "branch_id": 1
    }
]

for customer_data in test_customers:
    customer = Customer(**customer_data)
    customer.set_password(customer_data['temporary_password'])
    db.session.add(customer)

db.session.commit()
```

---

## ADDITIONAL REQUIRED ENDPOINTS

### 1. Owner Should See ALL Data (No Branch Filter)

```python
@app.route('/api/customers', methods=['GET'])
def get_customers():
    # Owner should see ALL customers across ALL branches
    # Don't filter by branch_id for owner role
    
    current_user = get_jwt_identity()
    if current_user['role'] == 'owner':
        customers = Customer.query.all()  # ⭐ NO FILTER
    else:
        # Manager/Reception see only their branch
        branch_id = current_user.get('branch_id')
        customers = Customer.query.filter_by(branch_id=branch_id).all()
    
    # ...rest of the code
```

### 2. Get All Branches Endpoint
```python
@app.route('/api/branches', methods=['GET'])
@jwt_required()
def get_branches():
    branches = Branch.query.all()
    return jsonify({
        'data': [branch.to_dict() for branch in branches]
    })
```

### 3. Get All Staff Endpoint
```python
@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    role = request.args.get('role')
    
    if role == 'staff':
        # Return managers, receptionists, accountants
        users = User.query.filter(
            User.role.in_(['manager', 'reception', 'accountant'])
        ).all()
    else:
        users = User.query.all()
    
    return jsonify({
        'data': [user.to_dict() for user in users]
    })
```

---

## SEED DATA REQUIREMENTS

### Minimum Required Data:

1. **1 Owner**
   - Username: `owner1`
   - Password: `owner123`
   - Role: `owner`
   - Branch: NULL (access to all)

2. **3 Branches**
   - Dragon Club (Nasr City, Cairo)
   - Monster Fitness (Maadi, Cairo)
   - Beast Gym (6th October City)

3. **3 Managers** (1 per branch)
   - `manager_dragon_1` / `manager123` → Branch 1
   - `manager_monster_1` / `manager123` → Branch 2
   - `manager_beast_1` / `manager123` → Branch 3

4. **3 Receptionists** (1 per branch)
   - `reception_dragon_1` / `reception123` → Branch 1
   - `reception_monster_1` / `reception123` → Branch 2
   - `reception_beast_1` / `reception123` → Branch 3

5. **3 Accountants** (1 per branch)
   - `accountant_dragon_1` / `accountant123` → Branch 1
   - `accountant_monster_1` / `accountant123` → Branch 2
   - `accountant_beast_1` / `accountant123` → Branch 3

6. **150 Customers** (50 per branch)
   - ⭐ Each MUST have `temporary_password` (format: AB12CD)
   - ⭐ Each MUST have `password_changed = False`
   - Distributed: 50 → Branch 1, 50 → Branch 2, 50 → Branch 3

7. **45 Active Subscriptions**
   - 15 per branch
   - Mix of Monthly, 3-Month, Session-based, Coin-based
   - Status: `active`

8. **36 Payments**
   - Random amounts (1000-3000 EGP)
   - Various payment methods (cash, card, bank_transfer)
   - Dates within last 14 days

9. **12 Expenses**
   - Categories: Equipment, Maintenance, Utilities, Salaries
   - Amounts: 500-5000 EGP
   - Distributed across 3 branches

---

## TESTING

### Test 1: Verify Temp Password in API
```bash
# Login as reception
TOKEN=$(curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"reception_dragon_1","password":"reception123"}' \
  | jq -r '.token')

# Get customers
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/customers \
  | jq '.data.items[0] | {full_name, phone, temporary_password, password_changed}'

# Expected output:
{
  "full_name": "Mohamed Salem",
  "phone": "01077827638",
  "temporary_password": "RX04AF",
  "password_changed": false
}
```

### Test 2: Verify Owner Sees All Data
```bash
# Login as owner
TOKEN=$(curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"owner1","password":"owner123"}' \
  | jq -r '.token')

# Get customers
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/customers \
  | jq '.data.items | length'

# Expected: 150 (all customers across all branches)

# Get branches
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/branches \
  | jq '.data | length'

# Expected: 3

# Get staff
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/users?role=staff \
  | jq '.data | length'

# Expected: 9 (3 managers + 3 receptionists + 3 accountants)
```

---

## SUMMARY

### ⭐ CRITICAL:
1. Add `temporary_password` field to Customer model
2. Add `password_changed` field to Customer model
3. Return these fields in API responses (for staff only)
4. Update seed.py to generate temp passwords for all customers

### Important:
1. Owner should see ALL data (no branch filtering)
2. Create 150 customers with temp passwords
3. Create 45 active subscriptions
4. Create 3 branches, 9 staff members

---

## Expected Result After Fix

**In Flutter App:**
1. Reception registers customer → sees temp password
2. Owner logs in → sees 150 customers, 45 subscriptions, revenue data
3. Owner views Branches → sees 3 branches
4. Owner views Staff → sees 9 staff members
5. Reception views customer → sees temp password with copy button

**Customer Login Flow:**
1. Customer receives: Phone (01077827638) + Password (RX04AF)
2. Customer logs into client app
3. App forces password change
4. Backend sets `password_changed = True`
5. Reception can no longer see password (shows ••••••••)

---

*This is the ONLY backend work needed to make the app fully functional.*

