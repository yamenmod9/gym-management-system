# 🚨 BACKEND FIX - QR CHECK-IN & SUBSCRIPTION DISPLAY - February 16, 2026

## CRITICAL ISSUES TO FIX

---

## 🎯 ISSUE 1: QR Code Check-In Returns "Resource Not Found" (404)

### Problem
When receptionists scan a customer's QR code and try to check them in, the backend returns **404 Not Found** for the attendance endpoint.

### Flutter App Calls
```
POST /api/attendance
Content-Type: application/json
Authorization: Bearer {staff_token}

{
  "customer_id": 115,
  "check_in_time": "2026-02-16T10:30:00Z",
  "action": "check_in_only"
}
```

### Required Backend Fix

#### Step 1: Create Attendance Model (if not exists)
```python
from datetime import datetime
from extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    action = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='attendance_records')
    branch = db.relationship('Branch', backref='attendance_records')
    subscription = db.relationship('Subscription', backref='attendance_records')
```

#### Step 2: Create Attendance Endpoints
File: `routes/attendance.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer, Attendance, Subscription, User
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/api/attendance', methods=['POST'])
@jwt_required()
def record_attendance():
    """Record customer check-in"""
    try:
        staff_id = get_jwt_identity()
        staff = User.query.get(staff_id)
        
        if not staff:
            return jsonify({'success': False, 'error': 'Staff not found'}), 401
        
        data = request.get_json()
        customer_id = data.get('customer_id')
        check_in_time_str = data.get('check_in_time')
        action = data.get('action', 'check_in_only')
        subscription_id = data.get('subscription_id')
        
        if not customer_id:
            return jsonify({'success': False, 'error': 'customer_id is required'}), 400
        
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        if not customer.is_active:
            return jsonify({'success': False, 'error': 'Customer account is inactive'}), 400
        
        if check_in_time_str:
            try:
                check_in_time = datetime.fromisoformat(check_in_time_str.replace('Z', '+00:00'))
            except:
                check_in_time = datetime.utcnow()
        else:
            check_in_time = datetime.utcnow()
        
        attendance = Attendance(
            customer_id=customer_id,
            branch_id=staff.branch_id,
            subscription_id=subscription_id,
            check_in_time=check_in_time,
            action=action
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Check-in recorded successfully',
            'data': {
                'attendance': {
                    'id': attendance.id,
                    'customer_id': customer_id,
                    'customer_name': customer.full_name,
                    'check_in_time': attendance.check_in_time.isoformat(),
                    'branch_id': staff.branch_id,
                    'action': action
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@attendance_bp.route('/api/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    """Get attendance records"""
    try:
        customer_id = request.args.get('customer_id', type=int)
        branch_id = request.args.get('branch_id', type=int)
        
        query = Attendance.query
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        if branch_id:
            query = query.filter_by(branch_id=branch_id)
        
        query = query.order_by(Attendance.check_in_time.desc())
        attendances = query.all()
        
        result = []
        for att in attendances:
            result.append({
                'id': att.id,
                'customer_id': att.customer_id,
                'customer_name': att.customer.full_name,
                'check_in_time': att.check_in_time.isoformat(),
                'check_out_time': att.check_out_time.isoformat() if att.check_out_time else None,
                'branch_id': att.branch_id,
                'action': att.action
            })
        
        return jsonify({
            'success': True,
            'data': {'items': result, 'total': len(result)}
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500
```

#### Step 3: Register Blueprint
In your main app file (`app.py` or `__init__.py`):
```python
from routes.attendance import attendance_bp
app.register_blueprint(attendance_bp)
```

#### Step 4: Create Database Table
```sql
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    branch_id INT NOT NULL,
    subscription_id INT,
    check_in_time DATETIME NOT NULL,
    check_out_time DATETIME,
    action VARCHAR(50),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id),
    INDEX idx_customer (customer_id),
    INDEX idx_branch (branch_id),
    INDEX idx_check_in_time (check_in_time)
);
```

---

## 🎯 ISSUE 2: Subscription Display - Wrong Metric Shown

### Problem
The client dashboard always shows "Days Remaining" even for:
- Coin-based subscriptions (should show "Remaining Coins")
- Session-based subscriptions (should show "Sessions Remaining")
- Personal training (should show "Training Sessions")

### Required Backend Changes

#### Step 1: Add Subscription Type Fields to Model
```python
class Subscription(db.Model):
    # ...existing fields...
    
    subscription_type = db.Column(db.String(50))  # 'coins', 'time_based', 'sessions', 'personal_training'
    
    # For coins-based
    coins = db.Column(db.Integer, nullable=True)
    remaining_coins = db.Column(db.Integer, nullable=True)
    
    # For time-based
    validity_months = db.Column(db.Integer, nullable=True)
    
    # For sessions-based
    sessions = db.Column(db.Integer, nullable=True)
    remaining_sessions = db.Column(db.Integer, nullable=True)
    
    # Common
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')
```

#### Step 2: Update Client Subscription Endpoint

File: `routes/clients.py` or similar

```python
@clients_bp.route('/api/client/subscription', methods=['GET'])
@jwt_required()
def get_client_subscription():
    """Get client's active subscription with type-based display data"""
    try:
        customer_id = get_jwt_identity()
        
        subscription = Subscription.query.filter_by(
            customer_id=customer_id,
            status='active'
        ).first()
        
        if not subscription:
            return jsonify({
                'status': 'success',
                'data': None,
                'message': 'No active subscription found'
            }), 200
        
        # Calculate days remaining
        days_remaining = 0
        months_remaining = 0
        if subscription.end_date:
            delta = subscription.end_date - datetime.now().date()
            days_remaining = max(0, delta.days)
            months_remaining = days_remaining // 30
        
        # Build base response
        response_data = {
            'id': subscription.id,
            'service_id': subscription.service_id,
            'service_name': subscription.service.name if subscription.service else None,
            'subscription_type': subscription.subscription_type,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            'status': subscription.status,
            'branch_id': subscription.branch_id,
            'branch_name': subscription.branch.name if subscription.branch else None,
        }
        
        # Add type-specific fields for display
        if subscription.subscription_type == 'coins':
            response_data['remaining_coins'] = subscription.remaining_coins or 0
            response_data['total_coins'] = subscription.coins or 0
            response_data['display_metric'] = 'coins'
            response_data['display_value'] = subscription.remaining_coins or 0
            response_data['display_label'] = f'{subscription.remaining_coins or 0} Coins'
            
        elif subscription.subscription_type == 'time_based':
            response_data['days_remaining'] = days_remaining
            response_data['months_remaining'] = months_remaining
            response_data['validity_months'] = subscription.validity_months
            response_data['display_metric'] = 'time'
            response_data['display_value'] = days_remaining
            if months_remaining > 0:
                days_in_month = days_remaining % 30
                response_data['display_label'] = f'{months_remaining} month{"s" if months_remaining > 1 else ""}, {days_in_month} day{"s" if days_in_month != 1 else ""}'
            else:
                response_data['display_label'] = f'{days_remaining} day{"s" if days_remaining != 1 else ""}'
            
        elif subscription.subscription_type == 'sessions':
            response_data['remaining_sessions'] = subscription.remaining_sessions or 0
            response_data['total_sessions'] = subscription.sessions or 0
            response_data['display_metric'] = 'sessions'
            response_data['display_value'] = subscription.remaining_sessions or 0
            response_data['display_label'] = f'{subscription.remaining_sessions or 0} Sessions'
            
        elif subscription.subscription_type == 'personal_training':
            response_data['remaining_sessions'] = subscription.remaining_sessions or 0
            response_data['total_sessions'] = subscription.sessions or 0
            response_data['display_metric'] = 'training'
            response_data['display_value'] = subscription.remaining_sessions or 0
            response_data['display_label'] = f'{subscription.remaining_sessions or 0} Training Sessions'
        else:
            # Default to time-based display
            response_data['days_remaining'] = days_remaining
            response_data['display_metric'] = 'time'
            response_data['display_value'] = days_remaining
            response_data['display_label'] = f'{days_remaining} days'
        
        # Common flags
        response_data['is_expired'] = days_remaining <= 0
        response_data['is_expiring_soon'] = 0 < days_remaining <= 7
        
        return jsonify({
            'status': 'success',
            'data': response_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500
```

#### Step 3: Update Login Endpoint

```python
@clients_bp.route('/api/client/auth/login', methods=['POST'])
def client_login():
    """Client login with subscription type data"""
    # ...existing login logic...
    
    # Get active subscription
    subscription = Subscription.query.filter_by(
        customer_id=customer.id,
        status='active'
    ).first()
    
    subscription_data = None
    if subscription:
        days_remaining = (subscription.end_date - datetime.now().date()).days if subscription.end_date else 0
        
        subscription_data = {
            'id': subscription.id,
            'service_name': subscription.service.name if subscription.service else None,
            'subscription_type': subscription.subscription_type,
            'status': subscription.status,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
        }
        
        # Add type-specific data
        if subscription.subscription_type == 'coins':
            subscription_data['remaining_coins'] = subscription.remaining_coins or 0
            subscription_data['display_metric'] = 'coins'
            subscription_data['display_value'] = subscription.remaining_coins or 0
            subscription_data['display_label'] = f'{subscription.remaining_coins or 0} Coins'
        elif subscription.subscription_type == 'time_based':
            months = days_remaining // 30
            subscription_data['days_remaining'] = days_remaining
            subscription_data['months_remaining'] = months
            subscription_data['display_metric'] = 'time'
            subscription_data['display_value'] = days_remaining
            if months > 0:
                subscription_data['display_label'] = f'{months}m {days_remaining % 30}d'
            else:
                subscription_data['display_label'] = f'{days_remaining} days'
        elif subscription.subscription_type in ['sessions', 'personal_training']:
            subscription_data['remaining_sessions'] = subscription.remaining_sessions or 0
            subscription_data['display_metric'] = 'sessions'
            subscription_data['display_value'] = subscription.remaining_sessions or 0
            subscription_data['display_label'] = f'{subscription.remaining_sessions or 0} Sessions'
        else:
            subscription_data['display_metric'] = 'time'
            subscription_data['display_value'] = days_remaining
            subscription_data['display_label'] = f'{days_remaining} days'
    
    return jsonify({
        'status': 'success',
        'token': access_token,
        'customer': {
            # ...customer data...
        },
        'subscription': subscription_data
    }), 200
```

---

## 🎯 ISSUE 3: Automatic Subscription Expiration

### Problem
Subscriptions don't automatically expire when:
- Time-based: `end_date` passes
- Coin-based: `remaining_coins` reaches 0
- Session-based: `remaining_sessions` reaches 0

### Solution: Add Expiration Check Function

```python
def check_and_expire_subscription(subscription):
    """Check if subscription should be expired and update status"""
    if subscription.status != 'active':
        return False
    
    should_expire = False
    
    # Check time-based expiration
    if subscription.end_date and datetime.now().date() > subscription.end_date:
        should_expire = True
    
    # Check coin-based expiration
    if subscription.subscription_type == 'coins' and (subscription.remaining_coins is None or subscription.remaining_coins <= 0):
        should_expire = True
    
    # Check session-based expiration
    if subscription.subscription_type in ['sessions', 'personal_training'] and (subscription.remaining_sessions is None or subscription.remaining_sessions <= 0):
        should_expire = True
    
    if should_expire:
        subscription.status = 'expired'
        db.session.commit()
        return True
    
    return False
```

Apply this check in:
1. `get_client_subscription` endpoint
2. `client_login` endpoint
3. Before allowing check-in

### Cron Job Endpoint (Optional)
```python
@subscriptions_bp.route('/api/subscriptions/expire-old', methods=['POST'])
def expire_old_subscriptions():
    """Background job to expire old subscriptions - call daily via cron"""
    try:
        today = datetime.now().date()
        
        # Expire time-based
        time_expired = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.end_date < today
        ).update({'status': 'expired'})
        
        # Expire coin-based with 0 coins
        coin_expired = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.subscription_type == 'coins',
            Subscription.remaining_coins <= 0
        ).update({'status': 'expired'})
        
        # Expire session-based with 0 sessions
        session_expired = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.subscription_type.in_(['sessions', 'personal_training']),
            Subscription.remaining_sessions <= 0
        ).update({'status': 'expired'})
        
        db.session.commit()
        
        total = time_expired + coin_expired + session_expired
        
        return jsonify({
            'success': True,
            'message': f'Expired {total} subscriptions',
            'details': {
                'time_based': time_expired,
                'coin_based': coin_expired,
                'session_based': session_expired
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## 🎯 IMPLEMENTATION CHECKLIST

### Database
- [ ] Create `attendance` table
- [ ] Add `subscription_type` column to subscriptions (VARCHAR(50))
- [ ] Add `coins`, `remaining_coins`, `sessions`, `remaining_sessions`, `validity_months` columns

### Endpoints
- [ ] ✅ Create `POST /api/attendance`
- [ ] ✅ Create `GET /api/attendance`
- [ ] ✅ Update `GET /api/client/subscription` with display logic
- [ ] ✅ Update `POST /api/client/auth/login` with subscription display data
- [ ] ✅ Create `POST /api/subscriptions/expire-old` (cron job)

### Testing
- [ ] Test QR scan → check-in flow (should return 201, not 404)
- [ ] Test coin-based subscription shows "X Coins" not "X days"
- [ ] Test time-based shows "2 months, 15 days"
- [ ] Test session-based shows "10 Sessions"
- [ ] Test subscription expires when coins/sessions = 0
- [ ] Test subscription expires when end_date passes

---

## 🚀 EXPECTED RESULTS

### Check-In Success
```
✅ Check-in recorded successfully
Customer: Adel Saad
Time: 2026-02-16 10:30:00
```

### Client Dashboard - Coins Subscription
```
Remaining: 25 Coins
Status: Active
```

### Client Dashboard - Time-Based Subscription
```
Remaining: 2 months, 15 days
Status: Active
```

### Client Dashboard - Sessions Subscription
```
Remaining: 10 Sessions
Status: Active
```

---

**Priority:** CRITICAL  
**Estimated Time:** 2-3 hours  
**Files to Create/Update:**
- `routes/attendance.py` (new)
- `routes/clients.py` (update)
- `models/attendance.py` (new)
- `models/subscription.py` (update)
- `app.py` (register blueprint)

