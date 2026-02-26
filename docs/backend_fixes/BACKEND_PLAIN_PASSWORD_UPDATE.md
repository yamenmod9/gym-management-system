# 🔑 CRITICAL UPDATE: PLAIN TEMPORARY PASSWORDS IN SEED DATA

**Date:** February 14, 2026  
**Priority:** CRITICAL  
**Issue:** Seed data must include `plain_temporary_password` field for staff to view

---

## 🚨 THE PROBLEM

The current seed data does NOT include the `plain_temporary_password` field, which means staff members (receptionists, managers) cannot see the temporary passwords to give to customers.

**Current Seed Data (WRONG):**
```python
customer = Customer(
    full_name='Ahmed Hassan',
    phone='01001234567',
    email='ahmed@example.com',
    temporary_password=generate_password_hash('AB12CD'),  # ✅ Hashed
    password_changed=False,
    # ❌ MISSING: plain_temporary_password field
)
```

**Fixed Seed Data (CORRECT):**
```python
plain_password = 'AB12CD'
customer = Customer(
    full_name='Ahmed Hassan',
    phone='01001234567',
    email='ahmed@example.com',
    temporary_password=generate_password_hash(plain_password),  # ✅ Hashed for security
    plain_temporary_password=plain_password,  # ✅ Plain for staff viewing
    password_changed=False,
)
```

---

## ✅ REQUIRED MODEL UPDATE

First, ensure the Customer model has the `plain_temporary_password` column:

```python
# models/customer.py
class Customer(db.Model):
    __tablename__ = 'customers'
    
    # ...existing fields...
    
    # Password fields
    temporary_password = db.Column(db.String(255))  # Hashed password (for authentication)
    plain_temporary_password = db.Column(db.String(10))  # Plain password (for staff viewing)
    password_changed = db.Column(db.Boolean, default=False)
```

**Database Migration:**
```sql
ALTER TABLE customers ADD COLUMN plain_temporary_password VARCHAR(10);
```

---

## 🌱 UPDATED SEED.PY

### Complete Customer Seeding with Plain Passwords

```python
import string
import random
from werkzeug.security import generate_password_hash
from datetime import datetime

def generate_temp_password(length=6):
    """Generate 6-character temporary password (uppercase + digits)"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def seed_customers():
    """Seed 50 customers across 3 branches"""
    
    print("\n" + "="*70)
    print("👤 CREATING CUSTOMERS WITH TEMPORARY PASSWORDS")
    print("="*70)
    print("\n📋 FIRST-TIME LOGIN CREDENTIALS (password_changed=False):")
    print("-" * 70)
    
    customers = []
    
    # Branch 1: Dragon Club (20 customers)
    for i in range(1, 21):
        plain_password = generate_temp_password()
        password_changed = i > 10  # First 10: not changed, last 10: changed
        
        customer = Customer(
            full_name=f'Dragon Customer {i}',
            phone=f'0100{i:07d}',  # 01000000001, 01000000002, etc.
            email=f'dragon{i}@example.com',
            qr_code=f'GYM-{i:06d}',  # GYM-000001, GYM-000002, etc.
            branch_id=1,
            gender=random.choice(['male', 'female']),
            date_of_birth=f'{random.randint(1990, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            weight=round(random.uniform(55.0, 100.0), 1),
            height=round(random.uniform(1.60, 1.95), 2),
            temporary_password=generate_password_hash(plain_password),  # Hashed
            plain_temporary_password=plain_password if not password_changed else None,  # Plain (only if not changed)
            password_changed=password_changed,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.session.add(customer)
        customers.append(customer)
        
        # Print credentials for first-time users only
        if not password_changed:
            print(f"  Phone: {customer.phone} | Password: {plain_password} | QR: {customer.qr_code}")
    
    # Branch 2: Phoenix Fitness (18 customers)
    for i in range(21, 39):
        plain_password = generate_temp_password()
        password_changed = i > 29
        
        customer = Customer(
            full_name=f'Phoenix Customer {i}',
            phone=f'0100{i:07d}',
            email=f'phoenix{i}@example.com',
            qr_code=f'GYM-{i:06d}',
            branch_id=2,
            gender=random.choice(['male', 'female']),
            date_of_birth=f'{random.randint(1990, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            weight=round(random.uniform(55.0, 100.0), 1),
            height=round(random.uniform(1.60, 1.95), 2),
            temporary_password=generate_password_hash(plain_password),
            plain_temporary_password=plain_password if not password_changed else None,
            password_changed=password_changed,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.session.add(customer)
        customers.append(customer)
        
        if not password_changed:
            print(f"  Phone: {customer.phone} | Password: {plain_password} | QR: {customer.qr_code}")
    
    # Branch 3: Tiger Gym (12 customers)
    for i in range(39, 51):
        plain_password = generate_temp_password()
        password_changed = i > 44
        
        customer = Customer(
            full_name=f'Tiger Customer {i}',
            phone=f'0100{i:07d}',
            email=f'tiger{i}@example.com',
            qr_code=f'GYM-{i:06d}',
            branch_id=3,
            gender=random.choice(['male', 'female']),
            date_of_birth=f'{random.randint(1990, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            weight=round(random.uniform(55.0, 100.0), 1),
            height=round(random.uniform(1.60, 1.95), 2),
            temporary_password=generate_password_hash(plain_password),
            plain_temporary_password=plain_password if not password_changed else None,
            password_changed=password_changed,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.session.add(customer)
        customers.append(customer)
        
        if not password_changed:
            print(f"  Phone: {customer.phone} | Password: {plain_password} | QR: {customer.qr_code}")
    
    db.session.commit()
    
    print("-" * 70)
    print(f"\n✅ Created {len(customers)} customers")
    print(f"   - First-time users (password_changed=False): {sum(1 for c in customers if not c.password_changed)}")
    print(f"   - Password changed (password_changed=True): {sum(1 for c in customers if c.password_changed)}")
    print("="*70 + "\n")
    
    return customers
```

---

## 📊 EXPECTED OUTPUT

When running `python seed.py`, you should see:

```
======================================================================
👤 CREATING CUSTOMERS WITH TEMPORARY PASSWORDS
======================================================================

📋 FIRST-TIME LOGIN CREDENTIALS (password_changed=False):
----------------------------------------------------------------------
  Phone: 01000000001 | Password: AB12CD | QR: GYM-000001
  Phone: 01000000002 | Password: XY34ZF | QR: GYM-000002
  Phone: 01000000003 | Password: PQ78MN | QR: GYM-000003
  Phone: 01000000004 | Password: KL90RS | QR: GYM-000004
  Phone: 01000000005 | Password: TU56VW | QR: GYM-000005
  Phone: 01000000006 | Password: CD23EF | QR: GYM-000006
  Phone: 01000000007 | Password: GH67IJ | QR: GYM-000007
  Phone: 01000000008 | Password: MN89OP | QR: GYM-000008
  Phone: 01000000009 | Password: QR12ST | QR: GYM-000009
  Phone: 01000000010 | Password: UV45WX | QR: GYM-000010
  Phone: 01000000021 | Password: YZ78AB | QR: GYM-000021
  Phone: 01000000022 | Password: CD01EF | QR: GYM-000022
  ... (25 total)
----------------------------------------------------------------------

✅ Created 50 customers
   - First-time users (password_changed=False): 25
   - Password changed (password_changed=True): 25
======================================================================
```

---

## 🔄 UPDATE CUSTOMER REGISTRATION ENDPOINT

When receptionists register new customers, make sure to set both fields:

```python
@customers_bp.route('/register', methods=['POST'])
@jwt_required()
def register_customer():
    """Register new customer"""
    data = request.get_json()
    
    # Generate temporary password
    plain_password = Customer.generate_temp_password()
    
    # Create customer
    customer = Customer(
        full_name=data['full_name'],
        phone=data['phone'],
        email=data.get('email'),
        branch_id=data['branch_id'],
        qr_code=f"GYM-{str(uuid.uuid4())[:8].upper()}",
        temporary_password=generate_password_hash(plain_password),  # Hashed
        plain_temporary_password=plain_password,  # Plain
        password_changed=False,
        # ...other fields...
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': customer.id,
            'temporary_password': plain_password,  # Return to receptionist
            'password_changed': False,
            'note': 'Give these credentials to the customer'
        }
    }), 201
```

---

## 🔄 UPDATE PASSWORD CHANGE ENDPOINT

When customers change their password, clear the plain password:

```python
@clients_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change customer password"""
    customer_id = get_jwt_identity()
    data = request.get_json()
    
    customer = Customer.query.get(customer_id)
    
    # Verify current password
    if not check_password_hash(customer.temporary_password, data['current_password']):
        return jsonify({'status': 'error', 'message': 'Invalid current password'}), 401
    
    # Update password
    customer.temporary_password = generate_password_hash(data['new_password'])
    customer.plain_temporary_password = None  # ✅ CLEAR PLAIN PASSWORD
    customer.password_changed = True
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Password changed'}), 200
```

---

## 🔍 UPDATE GET CUSTOMERS ENDPOINT

Return plain password only for staff and only if password not changed:

```python
@customers_bp.route('/', methods=['GET'])
@jwt_required()
def get_customers():
    """Get customers list (staff only)"""
    branch_id = request.args.get('branch_id', type=int)
    
    query = Customer.query
    if branch_id:
        query = query.filter_by(branch_id=branch_id)
    
    customers = query.all()
    
    result = []
    for customer in customers:
        data = {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email,
            'qr_code': customer.qr_code,
            'branch_id': customer.branch_id,
            'password_changed': customer.password_changed,
            'has_active_subscription': customer.has_active_subscription(),
        }
        
        # ✅ Return plain password ONLY if not changed
        if not customer.password_changed and customer.plain_temporary_password:
            data['temporary_password'] = customer.plain_temporary_password
        
        result.append(data)
    
    return jsonify({
        'status': 'success',
        'data': {'items': result, 'total': len(result)}
    }), 200
```

---

## ✅ TESTING CHECKLIST

After implementing this fix:

1. **Run Database Migration:**
   ```sql
   ALTER TABLE customers ADD COLUMN plain_temporary_password VARCHAR(10);
   ```

2. **Run Seed Script:**
   ```bash
   python seed.py
   ```
   - Should see 25 temporary passwords printed

3. **Test Staff App - Customers List:**
   - Login as receptionist: `reception_dragon_1` / `reception123`
   - Go to "All Customers" screen
   - Find customer with phone `01000000001`
   - Should see: `Password: AB12CD` (with copy icon)
   - Should see: `⚠️ First-time login - password not changed yet`

4. **Test Client App - First Login:**
   - Logout from staff app
   - Open client app
   - Login with phone `01000000001` and password `AB12CD`
   - Should be forced to change password

5. **Test After Password Change:**
   - Customer changes password to `mynewpass123`
   - Logout and login as receptionist again
   - View customer `01000000001`
   - Should see: `Password: ••••••••` (no plain password)
   - Should see: `✅ Password has been changed by user`

---

## 🚨 SECURITY NOTES

1. **Plain passwords are ONLY for staff viewing**
   - Never return to client app
   - Never include in client profile endpoint

2. **Plain passwords are ONLY for first-time users**
   - When `password_changed = False`
   - Cleared when customer changes password

3. **Both fields are needed:**
   - `temporary_password`: Hashed for authentication
   - `plain_temporary_password`: Plain for staff viewing

4. **This is acceptable because:**
   - Staff need to give credentials to customers
   - Passwords are temporary (6 characters, simple)
   - Users are forced to change on first login
   - After change, plain password is deleted

---

**END OF CRITICAL UPDATE**

**Action Required:** Update backend immediately  
**Files to Modify:**
1. `models/customer.py` - Add `plain_temporary_password` column
2. `seed.py` - Update customer seeding to include plain passwords
3. `routes/customers.py` - Update registration and get endpoints
4. `routes/clients.py` - Update password change endpoint

**Estimated Time:** 30 minutes

