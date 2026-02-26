# 🔧 BACKEND FIXES REQUIRED - COMPLETE LIST

**Date:** February 17, 2026  
**Repository:** https://github.com/yamenmod9/gym-management-system.git

---

## 📋 TABLE OF CONTENTS

1. [Customer Registration Branch Restriction](#1-customer-registration-branch-restriction)
2. [Subscription Status Display](#2-subscription-status-display)
3. [Customer Health Metrics API](#3-customer-health-metrics-api)
4. [Subscription Display Metrics](#4-subscription-display-metrics)
5. [Check-in Branch ID Handling](#5-check-in-branch-id-handling)
6. [Deployment Instructions](#6-deployment-instructions)

---

## 1. CUSTOMER REGISTRATION BRANCH RESTRICTION

### Issue
Receptionists cannot register customers for their own branch. The API returns:
```json
{
  "error": "Cannot register customer for another branch",
  "success": false
}
```

### Root Cause
The backend is incorrectly validating branch permissions. It should allow receptionists to register customers ONLY for their own branch, not reject them.

### Fix Required

**File:** `Gym_backend/backend/app/routes/customers_routes.py`

**Location:** Around line 160-175

**Current Code (WRONG):**
```python
# ❌ This logic is incorrect
branch_id = data.get('branch_id', current_user.branch_id)

# If user explicitly provides branch_id, check if it's their branch
if data.get('branch_id') and data['branch_id'] != current_user.branch_id:
    return error_response("Cannot register customer for another branch", 403)
```

**Corrected Code:**
```python
# ✅ Receptionist can ONLY register for their own branch
# Always use the receptionist's branch_id, ignore any provided branch_id
branch_id = current_user.branch_id

# Create customer
customer = Customer(
    full_name=data['full_name'],
    phone=data['phone'],
    email=data.get('email'),
    gender=Gender(data['gender'].lower()),
    date_of_birth=date_of_birth,
    address=data.get('address'),
    height=data.get('height'),
    weight=data.get('weight'),
    branch_id=branch_id,  # ✅ Always use current_user.branch_id
    health_notes=data.get('notes'),
    is_active=True
)
```

**Explanation:**
- Remove the branch_id validation check entirely
- Always force `branch_id = current_user.branch_id`
- This ensures receptionists can only register customers for their own branch
- No need to allow them to specify a different branch

---

## 2. SUBSCRIPTION STATUS DISPLAY

### Issue
In the "All Customers" screen (`customers_list_screen.dart`), all customers show "No Subscription" even when they have active subscriptions.

### Root Cause
The backend API `/api/customers` does not include the `has_active_subscription` field in the response.

### Fix Required

**File:** `Gym_backend/backend/app/routes/customers_routes.py`

**Endpoint:** `GET /api/customers`

**Add this field to the response:**

```python
@customers_bp.route('', methods=['GET'])
@token_required
def get_customers():
    """Get all customers for staff user's branch"""
    try:
        # ... existing code ...
        
        customers_data = []
        for customer in customers:
            # ✅ ADD: Check if customer has active subscription
            has_active_sub = db.session.query(Subscription).filter(
                Subscription.customer_id == customer.id,
                Subscription.status == 'active',
                or_(
                    Subscription.end_date >= datetime.utcnow().date(),
                    Subscription.subscription_type == 'coins'
                )
            ).first() is not None
            
            customer_dict = customer.to_dict()
            customer_dict['has_active_subscription'] = has_active_sub  # ✅ ADD THIS
            customers_data.append(customer_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'items': customers_data,
                'pagination': {
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'per_page': per_page
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Import required:**
```python
from sqlalchemy import or_
```

---

## 3. CUSTOMER HEALTH METRICS API

### Issue
In the recent customers display on the reception home screen:
- BMI values are incorrect
- Age values are wrong
- Registration time ("X days ago") is incorrect

### Root Cause
The backend is not correctly calculating these values OR the API response is not including proper timestamps.

### Fix Required

**File:** `Gym_backend/backend/app/models/customer.py`

**Ensure the `to_dict()` method includes:**

```python
def to_dict(self):
    """Convert customer to dictionary"""
    return {
        'id': self.id,
        'full_name': self.full_name,
        'phone': self.phone,
        'email': self.email,
        'branch_id': self.branch_id,
        'gender': self.gender.value if self.gender else None,
        'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
        'age': self.age,  # ✅ Calculated property
        'weight': float(self.weight) if self.weight else None,
        'height': float(self.height) if self.height else None,
        'bmi': float(self.bmi) if self.bmi else None,
        'bmi_category': self.bmi_category,
        'bmr': float(self.bmr) if self.bmr else None,
        'ideal_weight': float(self.ideal_weight) if self.ideal_weight else None,
        'daily_calories': float(self.daily_calories) if self.daily_calories else None,
        'qr_code': self.qr_code,
        'temp_password': self.temp_password,
        'password_changed': self.password_changed,
        'is_active': self.is_active,
        'created_at': self.created_at.isoformat() if self.created_at else None,  # ✅ ISO format
        'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        'address': self.address,
        'national_id': self.national_id,
        'health_notes': self.health_notes
    }
```

**Verify BMI calculation is correct:**

```python
def calculate_health_metrics(self):
    """Calculate BMI, BMI category, BMR, ideal weight, and daily calories"""
    if self.height and self.weight:
        # BMI = weight(kg) / (height(m))^2
        height_m = self.height / 100  # ✅ Convert cm to m
        self.bmi = round(self.weight / (height_m ** 2), 2)
        
        # BMI Category
        if self.bmi < 18.5:
            self.bmi_category = "Underweight"
        elif 18.5 <= self.bmi < 25:
            self.bmi_category = "Normal"
        elif 25 <= self.bmi < 30:
            self.bmi_category = "Overweight"
        else:
            self.bmi_category = "Obese"
        
        # ... rest of calculations ...
```

---

## 4. SUBSCRIPTION DISPLAY METRICS

### Issue
In the client app:
- Time remaining shows even for coin-based subscriptions
- Plan screen shows start date, end date, and time remaining for coin subscriptions
- Display should be dynamic based on subscription type

### Fix Required

**File:** `Gym_backend/backend/app/routes/subscriptions_routes.py`

**Endpoint:** `GET /api/client/subscription` (or wherever client subscription is retrieved)

**Add dynamic display logic:**

```python
def calculate_display_metrics(subscription):
    """Calculate dynamic display metrics based on subscription type"""
    service = subscription.service
    
    if not service:
        return {
            'display_metric': 'time',
            'display_value': 0,
            'display_label': '0 days'
        }
    
    # Get subscription type from service
    sub_type = (service.subscription_type or '').lower()
    service_name = (service.name or '').lower()
    
    # Check if coin-based
    is_coins = (
        sub_type == 'coins' or 
        'coin' in service_name or 
        'قطعة' in service_name
    )
    
    if is_coins:
        remaining_coins = subscription.remaining_coins or 0
        return {
            'display_metric': 'coins',
            'display_value': remaining_coins,
            'display_label': f'{remaining_coins} Coins',
            'remaining_coins': remaining_coins,
            # Coins validity: >= 30 coins = unlimited, < 30 = 1 year
            'validity_type': 'unlimited' if remaining_coins >= 30 else '1_year'
        }
    
    # Check if session-based
    is_sessions = sub_type in ['sessions', 'personal_training']
    
    if is_sessions:
        remaining_sessions = subscription.remaining_sessions or 0
        return {
            'display_metric': 'sessions',
            'display_value': remaining_sessions,
            'display_label': f'{remaining_sessions} Sessions',
            'remaining_sessions': remaining_sessions
        }
    
    # Default: time-based
    if subscription.end_date:
        days_remaining = (subscription.end_date - datetime.utcnow().date()).days
        days_remaining = max(0, days_remaining)
        months = days_remaining // 30
        days = days_remaining % 30
        
        if months > 0:
            label = f'{months}m {days}d'
        else:
            label = f'{days_remaining} days'
        
        return {
            'display_metric': 'time',
            'display_value': days_remaining,
            'display_label': label,
            'days_remaining': days_remaining,
            'months_remaining': months
        }
    
    return {
        'display_metric': 'time',
        'display_value': 0,
        'display_label': '0 days'
    }

# Use in subscription endpoint:
@subscriptions_bp.route('/customer/<int:customer_id>', methods=['GET'])
@token_required
def get_customer_subscription(customer_id):
    """Get active subscription for a customer"""
    try:
        # ... existing code to get subscription ...
        
        # ✅ ADD: Calculate display metrics
        display_metrics = calculate_display_metrics(subscription)
        
        subscription_data = {
            'id': subscription.id,
            'subscription_type': subscription.subscription_type,
            'service_name': subscription.service.name if subscription.service else None,
            'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            'status': subscription.status,
            # ✅ ADD: Include display metrics
            **display_metrics
        }
        
        return jsonify({
            'success': True,
            'data': subscription_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Also update:** `GET /api/client/me` (client profile endpoint) to include the same display metrics.

---

## 5. CHECK-IN BRANCH ID HANDLING

### Issue
When scanning QR code and checking in, the API returns:
```json
{
  "error": "branch_id is required",
  "success": false
}
```

### Root Cause
The check-in endpoint expects `branch_id` in the request body, but the Flutter app is not sending it.

### Fix Required

**File:** `Gym_backend/backend/app/routes/checkins_routes.py`

**Endpoint:** `POST /api/checkins/check-in`

**Update to automatically use the staff member's branch:**

```python
@checkins_bp.route('/check-in', methods=['POST'])
@token_required
def check_in_customer():
    """Record customer check-in"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        qr_code = data.get('qr_code')
        
        # ✅ Use the staff member's branch_id automatically
        branch_id = current_user.branch_id
        
        # Validate customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        # Check if customer belongs to this branch
        if customer.branch_id != branch_id:
            return jsonify({
                'success': False,
                'error': 'Customer belongs to a different branch'
            }), 403
        
        # Get active subscription
        subscription = Subscription.query.filter_by(
            customer_id=customer_id,
            status='active'
        ).filter(
            or_(
                Subscription.end_date >= datetime.utcnow().date(),
                Subscription.subscription_type == 'coins'
            )
        ).first()
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': 'No active subscription found'
            }), 403
        
        # Check subscription type and deduct accordingly
        if subscription.subscription_type == 'coins':
            if not subscription.remaining_coins or subscription.remaining_coins <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient coins'
                }), 403
            subscription.remaining_coins -= 1
        elif subscription.subscription_type in ['sessions', 'personal_training']:
            if not subscription.remaining_sessions or subscription.remaining_sessions <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient sessions'
                }), 403
            subscription.remaining_sessions -= 1
        
        # Create check-in record
        checkin = CheckIn(
            customer_id=customer_id,
            branch_id=branch_id,  # ✅ Use staff's branch
            checked_in_by=current_user.id,
            check_in_time=datetime.utcnow()
        )
        
        db.session.add(checkin)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Check-in successful',
            'data': {
                'check_in_id': checkin.id,
                'customer_name': customer.full_name,
                'remaining_coins': subscription.remaining_coins if subscription.subscription_type == 'coins' else None,
                'remaining_sessions': subscription.remaining_sessions if subscription.subscription_type in ['sessions', 'personal_training'] else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## 6. DEPLOYMENT INSTRUCTIONS

### Step 1: Update Code on GitHub

```bash
cd ~/gym-management-system
git add .
git commit -m "Fix: customer registration, subscription display, and check-in branch handling"
git push origin main
```

### Step 2: Deploy to PythonAnywhere

1. **Login to PythonAnywhere:** https://www.pythonanywhere.com

2. **Open Bash Console**

3. **Pull Latest Code:**
```bash
cd ~/gym-management-system
git pull origin main
```

4. **Reload Web App:**
   - Go to "Web" tab
   - Click the green "Reload" button for your web app

5. **Verify Deployment:**
```bash
curl https://yourusername.pythonanywhere.com/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"phone":"01511111111","password":"reception123"}'
```

If you get a token in the response, the deployment was successful!

---

## 📊 SUMMARY OF CHANGES

### Backend Files to Modify:

1. **`app/routes/customers_routes.py`**
   - Fix branch restriction logic
   - Add `has_active_subscription` field to customer list response

2. **`app/models/customer.py`**
   - Verify `to_dict()` includes all required fields
   - Verify BMI calculation is correct
   - Ensure `created_at` is in ISO format

3. **`app/routes/subscriptions_routes.py`**
   - Add `calculate_display_metrics()` function
   - Update subscription endpoints to include display metrics
   - Handle coin-based vs time-based vs session-based subscriptions

4. **`app/routes/checkins_routes.py`**
   - Auto-populate `branch_id` from `current_user.branch_id`
   - Remove requirement for client to send `branch_id`
   - Add coin/session deduction logic

### Expected Results After Fixes:

✅ Receptionists can register customers for their own branch  
✅ Customer list shows correct subscription status  
✅ Recent customers show correct BMI, age, and registration time  
✅ Client app shows dynamic subscription info (coins/time/sessions)  
✅ QR code check-in works without branch_id error  
✅ Coins/sessions are deducted on each check-in  

---

**END OF DOCUMENT**

