# 🚨 CRITICAL BACKEND FIXES REQUIRED - February 16, 2026

**Priority:** HIGH  
**Status:** ❌ REQUIRES IMMEDIATE BACKEND IMPLEMENTATION

---

## 📋 TABLE OF CONTENTS

1. [Issue 1: Customer Registration Branch Restriction](#issue-1-customer-registration-branch-restriction)
2. [Issue 2: Subscription Display Metrics](#issue-2-subscription-display-metrics)
3. [Issue 3: Check-in Branch Validation](#issue-3-check-in-branch-validation)
4. [Complete Implementation Guide](#complete-implementation-guide)
5. [Testing Checklist](#testing-checklist)

---

## ISSUE 1: Customer Registration Branch Restriction ❌

### Problem
When a receptionist tries to register a new customer, the backend returns:
```json
{
  "error": "Cannot register customer for another branch",
  "success": false
}
```

**Error Details:**
- Receptionist is logged in at Branch 1
- Tries to register customer for Branch 1 (their own branch)
- Backend incorrectly blocks the registration

### Root Cause
Backend is incorrectly validating branch_id against the receptionist's branch. The validation logic is too strict or incorrectly implemented.

### Current Flutter Implementation (CORRECT)
```dart
// In register_customer_dialog.dart
Future<void> _handleSubmit() async {
  final provider = context.read<ReceptionProvider>();
  
  // Always use the receptionist's own branch_id
  final customer = provider.calculateHealthMetrics(
    fullName: _nameController.text.trim(),
    weight: double.parse(_weightController.text),
    height: heightInMeters,
    age: int.parse(_ageController.text),
    gender: _gender,
    phone: _phoneController.text.trim(),
    email: _emailController.text.trim(),
    qrCode: null,
  );
  
  final result = await provider.registerCustomer(customer);
}

// In reception_provider.dart
Future<Map<String, dynamic>> registerCustomer(CustomerModel customer) async {
  final customerData = customer.toJson();
  customerData['branch_id'] = branchId; // ✅ Uses receptionist's branch_id
  
  final response = await _apiService.post(
    ApiEndpoints.registerCustomer,
    data: customerData,
  );
}
```

### Required Backend Fix

**Endpoint:** `POST /api/customers/register`

**Current (WRONG) Implementation:**
```python
@app.route('/api/customers/register', methods=['POST'])
@jwt_required()
def register_customer():
    current_user = get_jwt_identity()
    data = request.json
    
    # ❌ WRONG: This blocks valid registrations
    if current_user['branch_id'] != data['branch_id']:
        return jsonify({
            'success': False,
            'error': 'Cannot register customer for another branch'
        }), 403
```

**Required (CORRECT) Implementation:**
```python
@app.route('/api/customers/register', methods=['POST'])
@jwt_required()
def register_customer():
    """Register a new customer"""
    current_user = get_jwt_identity()
    data = request.json
    
    # Extract staff role and branch
    staff_role = current_user.get('role', '').lower()
    staff_branch_id = current_user.get('branch_id')
    requested_branch_id = data.get('branch_id')
    
    # ✅ CORRECT: Validate based on role
    if staff_role in ['receptionist', 'manager']:
        # Receptionists and managers can ONLY register for their own branch
        if staff_branch_id != requested_branch_id:
            return jsonify({
                'success': False,
                'error': 'You can only register customers for your own branch'
            }), 403
    elif staff_role == 'owner':
        # Owners can register for ANY branch
        pass
    else:
        # Other roles cannot register customers
        return jsonify({
            'success': False,
            'error': 'You do not have permission to register customers'
        }), 403
    
    # Validate required fields
    required_fields = ['full_name', 'phone', 'branch_id', 'gender', 'age', 'weight', 'height']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {", ".join(missing)}'
        }), 400
    
    # Check if phone number already exists
    existing = Customer.query.filter_by(phone=data['phone']).first()
    if existing:
        return jsonify({
            'success': False,
            'error': 'A customer with this phone number already exists'
        }), 400
    
    try:
        # Generate temporary password
        temp_password = generate_temp_password()  # e.g., "AB12CD"
        hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
        
        # Create customer
        customer = Customer(
            full_name=data['full_name'],
            phone=data['phone'],
            email=data.get('email'),
            branch_id=requested_branch_id,
            gender=data['gender'],
            date_of_birth=calculate_birthdate(data['age']),
            weight=float(data['weight']),
            height=float(data['height']),
            bmi=float(data.get('bmi', 0)),
            bmi_category=data.get('bmi_category', 'Normal'),
            bmr=float(data.get('bmr', 0)),
            daily_calories=float(data.get('daily_calories', 0)),
            password_hash=hashed_password,
            temp_password=temp_password,
            password_changed=False,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(customer)
        db.session.flush()  # Get customer ID
        
        # Generate QR code
        customer.qr_code = f"customer_id:{customer.id}"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer registered successfully',
            'data': {
                'customer': {
                    'id': customer.id,
                    'full_name': customer.full_name,
                    'phone': customer.phone,
                    'email': customer.email,
                    'branch_id': customer.branch_id,
                    'qr_code': customer.qr_code,
                    'temp_password': temp_password,
                    'password_changed': False
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }), 500
```

**Helper Function:**
```python
def generate_temp_password(length=6):
    """Generate a temporary password like 'AB12CD'"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def calculate_birthdate(age):
    """Calculate approximate birthdate from age"""
    from datetime import datetime
    current_year = datetime.utcnow().year
    birth_year = current_year - age
    return datetime(birth_year, 1, 1)
```

---

## ISSUE 2: Subscription Display Metrics ❌

### Problem
The client dashboard and plan screen always show "Time Remaining" even for coin-based subscriptions. The display should adapt based on subscription type.

### Requirements

#### For COIN-BASED Subscriptions:
- **Container Title:** "Coins Remaining"
- **Display Value:** Number of coins (e.g., "50")
- **Validity:** 
  - If coins >= 30: "Unlimited"
  - If coins < 30: "1 Year"
- **Coins decrease by 1 on each QR code scan**

#### For TIME-BASED Subscriptions:
- **Container Title:** "Time Remaining"
- **Display Value:** Days or months (e.g., "45 days" or "2 months 15 days")
- **Expiry Date:** Show end_date
- **No coin deduction**

#### For PERSONAL TRAINING Subscriptions:
- **Container Title:** "Sessions Remaining"
- **Display Value:** Number of sessions (e.g., "8 sessions")
- **Sessions decrease by 1 on each use**

### Required Backend Response Format

**Endpoint:** `GET /api/subscriptions/customer/{customer_id}`

**Required Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 124,
        "customer_id": 115,
        "service_id": 1,
        "service_name": "50 Coins Bundle",
        "subscription_type": "coins",
        "branch_id": 2,
        "status": "active",
        "start_date": "2026-02-16",
        "end_date": "2027-02-16",
        
        // ✅ REQUIRED: Dynamic display fields
        "display_metric": "coins",
        "display_value": 50,
        "display_label": "50 Coins",
        "remaining_coins": 50,
        "initial_coins": 50,
        "validity_type": "unlimited",
        
        // Standard fields
        "amount": 1000.00,
        "created_at": "2026-02-16T10:00:00Z",
        "can_access": true,
        "is_expired": false
      }
    ]
  }
}
```

**For Time-Based Subscription:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 125,
        "customer_id": 115,
        "service_name": "3 Month Membership",
        "subscription_type": "time_based",
        
        // ✅ REQUIRED: Dynamic display fields
        "display_metric": "time",
        "display_value": 45,
        "display_label": "45 days",
        "days_remaining": 45,
        "months_remaining": 1,
        "end_date": "2026-04-02",
        "validity_type": "expiry_date",
        
        "status": "active",
        "start_date": "2026-02-16",
        "can_access": true,
        "is_expired": false
      }
    ]
  }
}
```

**For Personal Training:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 126,
        "service_name": "Personal Training Package",
        "subscription_type": "personal_training",
        
        // ✅ REQUIRED: Dynamic display fields
        "display_metric": "sessions",
        "display_value": 8,
        "display_label": "8 Sessions",
        "remaining_sessions": 8,
        "initial_sessions": 12,
        "validity_type": "sessions",
        
        "status": "active",
        "can_access": true
      }
    ]
  }
}
```

### Backend Implementation

```python
@app.route('/api/subscriptions/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_subscriptions(customer_id):
    """Get customer subscriptions with dynamic display metrics"""
    
    subscriptions = Subscription.query.filter_by(
        customer_id=customer_id,
        status='active'
    ).all()
    
    result = []
    for sub in subscriptions:
        service = Service.query.get(sub.service_id)
        
        # Calculate dynamic display values based on subscription type
        display_data = calculate_display_metrics(sub, service)
        
        result.append({
            'id': sub.id,
            'customer_id': sub.customer_id,
            'service_id': sub.service_id,
            'service_name': service.name if service else 'Unknown',
            'subscription_type': service.subscription_type if service else 'time_based',
            'branch_id': sub.branch_id,
            'status': sub.status,
            'start_date': sub.start_date.isoformat(),
            'end_date': sub.end_date.isoformat() if sub.end_date else None,
            'amount': float(sub.amount),
            'created_at': sub.created_at.isoformat(),
            'can_access': not sub.is_expired and sub.status == 'active',
            'is_expired': sub.is_expired,
            
            # Dynamic display fields
            **display_data
        })
    
    return jsonify({
        'success': True,
        'data': {
            'items': result,
            'pagination': {
                'total': len(result),
                'current_page': 1,
                'pages': 1,
                'per_page': len(result)
            }
        }
    }), 200


def calculate_display_metrics(subscription, service):
    """Calculate dynamic display metrics based on subscription type"""
    
    if not service:
        return {
            'display_metric': 'time',
            'display_value': 0,
            'display_label': '0 days',
            'days_remaining': 0
        }
    
    sub_type = service.subscription_type.lower()
    
    if sub_type == 'coins' or 'coin' in service.name.lower():
        # Coin-based subscription
        coins = subscription.coins or subscription.remaining_coins or 0
        validity = 'unlimited' if coins >= 30 else '1_year'
        
        return {
            'display_metric': 'coins',
            'display_value': coins,
            'display_label': f'{coins} Coins',
            'remaining_coins': coins,
            'initial_coins': subscription.initial_coins or coins,
            'validity_type': validity
        }
    
    elif sub_type == 'personal_training' or 'training' in service.name.lower():
        # Personal training subscription
        sessions = subscription.remaining_sessions or 0
        
        return {
            'display_metric': 'sessions',
            'display_value': sessions,
            'display_label': f'{sessions} Sessions',
            'remaining_sessions': sessions,
            'initial_sessions': subscription.initial_sessions or sessions,
            'validity_type': 'sessions'
        }
    
    else:
        # Time-based subscription
        from datetime import datetime
        
        if subscription.end_date:
            days_remaining = (subscription.end_date - datetime.utcnow().date()).days
            days_remaining = max(0, days_remaining)
            
            months_remaining = days_remaining // 30
            days_in_month = days_remaining % 30
            
            if months_remaining > 0:
                label = f'{months_remaining} month{"s" if months_remaining > 1 else ""}'
                if days_in_month > 0:
                    label += f' {days_in_month} days'
            else:
                label = f'{days_remaining} days'
        else:
            days_remaining = 0
            months_remaining = 0
            label = '0 days'
        
        return {
            'display_metric': 'time',
            'display_value': days_remaining,
            'display_label': label,
            'days_remaining': days_remaining,
            'months_remaining': months_remaining,
            'validity_type': 'expiry_date'
        }
```

---

## ISSUE 3: Check-in Branch Validation ❌

### Problem
Check-in endpoint returns "branch_id is required" error even though Flutter app sends it.

### Current Flutter Implementation (CORRECT)
```dart
// In qr_scanner_screen.dart
Future<void> _recordCheckIn(int customerId, String name) async {
  final apiService = context.read<ApiService>();
  final authProvider = context.read<AuthProvider>();
  final branchId = int.tryParse(authProvider.branchId ?? '1') ?? 1;

  // Record attendance WITH branch_id
  final response = await apiService.post(
    ApiEndpoints.attendance,
    data: {
      'customer_id': customerId,
      'branch_id': branchId,  // ✅ Sending branch_id
      'qr_code': 'customer_id:$customerId',
      'check_in_time': DateTime.now().toIso8601String(),
      'action': 'check_in_only',
    },
  );
}
```

### Required Backend Fix

**Endpoint:** `POST /api/attendance`

**Correct Implementation:**
```python
@app.route('/api/attendance', methods=['POST'])
@jwt_required()
def create_attendance():
    """Record customer check-in"""
    current_user = get_jwt_identity()
    data = request.json
    
    customer_id = data.get('customer_id')
    branch_id = data.get('branch_id')  # ✅ Accept from request
    qr_code = data.get('qr_code')
    check_in_time = data.get('check_in_time')
    action = data.get('action', 'check_in_only')
    subscription_id = data.get('subscription_id')
    
    # Validate required fields
    if not customer_id:
        return jsonify({
            'success': False,
            'error': 'customer_id is required'
        }), 400
    
    if not branch_id:
        return jsonify({
            'success': False,
            'error': 'branch_id is required'
        }), 400
    
    # Validate customer exists
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({
            'success': False,
            'error': 'Customer not found'
        }), 404
    
    if not customer.is_active:
        return jsonify({
            'success': False,
            'error': 'Customer account is inactive'
        }), 400
    
    # Parse check_in_time
    if check_in_time:
        try:
            check_in_dt = datetime.fromisoformat(check_in_time.replace('Z', '+00:00'))
        except:
            check_in_dt = datetime.utcnow()
    else:
        check_in_dt = datetime.utcnow()
    
    # Get active subscription
    if not subscription_id:
        subscription = Subscription.query.filter_by(
            customer_id=customer_id,
            status='active'
        ).first()
        subscription_id = subscription.id if subscription else None
    
    # Create attendance record
    attendance = Attendance(
        customer_id=customer_id,
        branch_id=branch_id,  # ✅ Use from request
        subscription_id=subscription_id,
        check_in_time=check_in_dt,
        action=action,
        created_at=datetime.utcnow()
    )
    
    db.session.add(attendance)
    
    # If action includes coin/session deduction
    if action in ['check_in_and_deduct', 'deduct_coin', 'deduct_session']:
        if subscription_id:
            subscription = Subscription.query.get(subscription_id)
            if subscription:
                service = Service.query.get(subscription.service_id)
                
                if service and 'coin' in service.subscription_type.lower():
                    # Deduct coin
                    if subscription.coins and subscription.coins > 0:
                        subscription.coins -= 1
                        if subscription.coins == 0:
                            subscription.status = 'expired'
                            subscription.is_expired = True
                elif service and 'training' in service.subscription_type.lower():
                    # Deduct session
                    if subscription.remaining_sessions and subscription.remaining_sessions > 0:
                        subscription.remaining_sessions -= 1
                        if subscription.remaining_sessions == 0:
                            subscription.status = 'expired'
                            subscription.is_expired = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Check-in recorded successfully',
        'data': {
            'id': attendance.id,
            'customer_id': customer_id,
            'customer_name': customer.full_name,
            'check_in_time': attendance.check_in_time.isoformat(),
            'branch_id': branch_id
        }
    }), 201
```

---

## COMPLETE IMPLEMENTATION GUIDE

### Database Schema Verification

#### Customers Table
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(255),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    gender VARCHAR(10) NOT NULL,
    date_of_birth DATE,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    bmi DECIMAL(5,2),
    bmi_category VARCHAR(50),
    bmr DECIMAL(7,2),
    daily_calories DECIMAL(7,2),
    password_hash VARCHAR(255) NOT NULL,
    temp_password VARCHAR(10),
    password_changed BOOLEAN DEFAULT FALSE,
    qr_code VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Subscriptions Table
```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    service_id INTEGER NOT NULL REFERENCES services(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    amount DECIMAL(10,2) NOT NULL,
    
    -- Coin-based fields
    coins INTEGER DEFAULT 0,
    initial_coins INTEGER DEFAULT 0,
    
    -- Session-based fields
    remaining_sessions INTEGER DEFAULT 0,
    initial_sessions INTEGER DEFAULT 0,
    
    -- Status fields
    is_expired BOOLEAN DEFAULT FALSE,
    can_access BOOLEAN DEFAULT TRUE,
    
    -- Freeze tracking
    freeze_count INTEGER DEFAULT 0,
    total_frozen_days INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Attendance Table
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    subscription_id INTEGER REFERENCES subscriptions(id),
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP,
    action VARCHAR(50) DEFAULT 'check_in_only',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_customer_id (customer_id),
    INDEX idx_branch_id (branch_id),
    INDEX idx_check_in_time (check_in_time)
);
```

---

## TESTING CHECKLIST

### Test 1: Customer Registration ✅
1. Login as receptionist (branch 1)
2. Open "Add New Customer" dialog
3. Fill in customer details:
   - Name: "Test Customer"
   - Phone: "01234567890"
   - Age: 25
   - Weight: 75
   - Height: 175
   - Gender: Male
4. Click "Register"
5. **Expected:**
   - ✅ Success message: "Customer registered successfully"
   - ✅ Customer ID shown
   - ✅ Temp password shown
   - ✅ Customer appears in recent customers list
   - ✅ NO "Cannot register customer for another branch" error

### Test 2: Coin Subscription Display ✅
1. Login to client app (use customer with coin subscription)
2. View dashboard
3. **Expected:**
   - ✅ Container shows "Coins Remaining"
   - ✅ Shows coin count (e.g., "50")
   - ✅ Shows validity: "Unlimited" or "1 Year"
   - ✅ NO time remaining display
4. Go to Plan screen
5. **Expected:**
   - ✅ Shows coin information
   - ✅ Shows validity period
   - ✅ NO expiry date shown

### Test 3: Time-Based Subscription Display ✅
1. Login to client app (use customer with time-based subscription)
2. View dashboard
3. **Expected:**
   - ✅ Container shows "Time Remaining"
   - ✅ Shows days/months remaining
   - ✅ Shows expiry date
   - ✅ NO coins display
4. Go to Plan screen
5. **Expected:**
   - ✅ Shows expiry date
   - ✅ Shows time remaining
   - ✅ NO coins information

### Test 4: QR Code Check-in ✅
1. Login as receptionist
2. Open QR scanner
3. Scan customer QR code
4. Click "Check-In Only"
5. **Expected:**
   - ✅ Success message: "Customer checked in successfully"
   - ✅ NO "branch_id is required" error
   - ✅ Attendance record created in database

### Test 5: Coin Deduction on Scan ✅
1. Login as receptionist
2. Scan QR code of customer with coin subscription
3. Click "Check-In and Deduct"
4. **Expected:**
   - ✅ Coins decrease by 1
   - ✅ Customer can still access if coins > 0
   - ✅ When coins = 0, subscription expires
5. Check client app dashboard
6. **Expected:**
   - ✅ Updated coin count shown
   - ✅ If coins = 0, shows "Expired"

---

## 📊 SUMMARY OF REQUIRED CHANGES

### Backend Changes:
1. ✅ Fix customer registration branch validation (allow same-branch registration)
2. ✅ Add dynamic display metrics to subscription responses
3. ✅ Accept branch_id in check-in endpoint
4. ✅ Implement coin/session deduction logic
5. ✅ Ensure all database operations commit properly

### No Frontend Changes Required:
- ✅ Flutter app already sends correct data
- ✅ Flutter app already handles dynamic displays
- ✅ All UI components ready

---

## 🎯 PRIORITY ORDER

1. **CRITICAL:** Fix customer registration (blocking receptionist workflow)
2. **HIGH:** Add display metrics to subscriptions (UX issue)
3. **HIGH:** Fix check-in branch validation (blocking check-in workflow)
4. **MEDIUM:** Implement coin deduction (feature completion)

---

**END OF DOCUMENT**

