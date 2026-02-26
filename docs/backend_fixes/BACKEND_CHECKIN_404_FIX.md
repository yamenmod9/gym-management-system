# 🚨 CRITICAL FIX: 404 Error on Check-In Endpoint

**Date:** February 15, 2026  
**Priority:** CRITICAL  
**Issue:** "Resource not found" error when trying to check in customers via QR code scan

---

## 🔍 THE PROBLEM

When receptionists scan a customer's QR code and try to check them in, the app shows:
- **Error:** "Failed to check in"
- **Backend Response:** 404 Not Found
- **Missing Endpoint:** `POST /api/attendance`

### Error Flow:
```
1. Receptionist scans QR code ✅
2. App extracts customer ID ✅
3. App fetches customer details ✅
4. App shows check-in dialog ✅
5. Receptionist clicks "Check-In Only" or "Deduct Session" ✅
6. App calls: POST /api/attendance ❌ 404 ERROR
```

---

## ✅ REQUIRED BACKEND FIX

### 1. Create Attendance Endpoint

**File:** `routes/attendance.py` (or wherever your routes are)

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer, Attendance, Subscription
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/api/attendance', methods=['POST'])
@jwt_required()
def record_attendance():
    """
    Record customer check-in (with or without session deduction)
    
    Request Body:
    {
        "customer_id": 115,
        "check_in_time": "2026-02-15T14:30:00Z",
        "action": "check_in_only" | "check_in_with_deduction",
        "subscription_id": 45  // Optional, only if action is check_in_with_deduction
    }
    """
    try:
        # Get request data
        data = request.get_json()
        customer_id = data.get('customer_id')
        check_in_time = data.get('check_in_time')
        action = data.get('action', 'check_in_only')
        subscription_id = data.get('subscription_id')
        
        # Validate required fields
        if not customer_id:
            return jsonify({
                'success': False,
                'error': 'customer_id is required'
            }), 400
        
        # Verify customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        # Check if customer is active
        if not customer.is_active:
            return jsonify({
                'success': False,
                'error': 'Customer account is inactive'
            }), 400
        
        # Get staff's branch from JWT token
        current_user_id = get_jwt_identity()
        # Assuming you have a way to get the staff's branch_id
        # You might need to query the User/Staff table
        from models import User
        staff = User.query.get(current_user_id)
        staff_branch_id = staff.branch_id if staff else customer.branch_id
        
        # Parse check_in_time or use current time
        if check_in_time:
            try:
                check_in_dt = datetime.fromisoformat(check_in_time.replace('Z', '+00:00'))
            except ValueError:
                check_in_dt = datetime.utcnow()
        else:
            check_in_dt = datetime.utcnow()
        
        # Create attendance record
        attendance = Attendance(
            customer_id=customer_id,
            subscription_id=subscription_id,
            check_in_time=check_in_dt,
            branch_id=staff_branch_id,
            action=action,
            created_at=datetime.utcnow()
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
                    'branch_id': staff_branch_id,
                    'action': action
                }
            }
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@attendance_bp.route('/api/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    """
    Get attendance records (filtered by branch, customer, or date)
    
    Query Parameters:
    - customer_id: int (optional)
    - branch_id: int (optional)
    - date: YYYY-MM-DD (optional)
    - start_date: YYYY-MM-DD (optional)
    - end_date: YYYY-MM-DD (optional)
    """
    try:
        # Get query parameters
        customer_id = request.args.get('customer_id', type=int)
        branch_id = request.args.get('branch_id', type=int)
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Attendance.query
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if branch_id:
            query = query.filter_by(branch_id=branch_id)
        
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                query = query.filter(
                    db.func.date(Attendance.check_in_time) == date_obj
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(
                    Attendance.check_in_time >= start,
                    Attendance.check_in_time <= end
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # Order by most recent first
        query = query.order_by(Attendance.check_in_time.desc())
        
        # Execute query
        attendances = query.all()
        
        # Format response
        result = []
        for att in attendances:
            customer = Customer.query.get(att.customer_id)
            result.append({
                'id': att.id,
                'customer_id': att.customer_id,
                'customer_name': customer.full_name if customer else 'Unknown',
                'check_in_time': att.check_in_time.isoformat(),
                'check_out_time': att.check_out_time.isoformat() if att.check_out_time else None,
                'branch_id': att.branch_id,
                'action': att.action,
                'subscription_id': att.subscription_id
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': result,
                'total': len(result)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
```

---

### 2. Create/Update Attendance Model

**File:** `models/attendance.py` (or in your models file)

```python
from datetime import datetime
from extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    action = db.Column(db.String(50), default='check_in_only')  # check_in_only, check_in_with_deduction
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='attendances', lazy=True)
    subscription = db.relationship('Subscription', backref='attendances', lazy=True)
    branch = db.relationship('Branch', backref='attendances', lazy=True)
    
    def __repr__(self):
        return f'<Attendance {self.id}: Customer {self.customer_id} at {self.check_in_time}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'subscription_id': self.subscription_id,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'branch_id': self.branch_id,
            'action': self.action,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
```

---

### 3. Database Migration

**SQL to create table:**

```sql
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE SET NULL,
    check_in_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    check_out_time TIMESTAMP,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    action VARCHAR(50) DEFAULT 'check_in_only',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_attendance_customer ON attendance(customer_id);
CREATE INDEX idx_attendance_branch ON attendance(branch_id);
CREATE INDEX idx_attendance_date ON attendance(check_in_time);
CREATE INDEX idx_attendance_subscription ON attendance(subscription_id);
```

**Or using Flask-Migrate:**

```bash
flask db migrate -m "Add attendance table"
flask db upgrade
```

---

### 4. Register the Blueprint

**File:** `app.py` or `__init__.py`

```python
from routes.attendance import attendance_bp

# Register blueprint
app.register_blueprint(attendance_bp)
```

---

## 🧪 TESTING THE FIX

### Test 1: Check-In Only (No Deduction)

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/attendance \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 115,
    "check_in_time": "2026-02-15T14:30:00Z",
    "action": "check_in_only"
  }'
```

**Expected Response (201):**
```json
{
  "success": true,
  "message": "Check-in recorded successfully",
  "data": {
    "attendance": {
      "id": 1,
      "customer_id": 115,
      "customer_name": "Adel Saad",
      "check_in_time": "2026-02-15T14:30:00",
      "branch_id": 1,
      "action": "check_in_only"
    }
  }
}
```

---

### Test 2: Check-In with Session Deduction

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/attendance \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 115,
    "subscription_id": 45,
    "check_in_time": "2026-02-15T14:30:00Z",
    "action": "check_in_with_deduction"
  }'
```

**Expected Response (201):**
```json
{
  "success": true,
  "message": "Check-in recorded successfully",
  "data": {
    "attendance": {
      "id": 2,
      "customer_id": 115,
      "customer_name": "Adel Saad",
      "check_in_time": "2026-02-15T14:30:00",
      "branch_id": 1,
      "action": "check_in_with_deduction"
    }
  }
}
```

---

### Test 3: Get Attendance Records

```bash
# Get all attendance for a customer
curl -X GET "https://yamenmod91.pythonanywhere.com/api/attendance?customer_id=115" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get attendance for a specific date
curl -X GET "https://yamenmod91.pythonanywhere.com/api/attendance?date=2026-02-15" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get attendance for a branch
curl -X GET "https://yamenmod91.pythonanywhere.com/api/attendance?branch_id=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## ✅ VERIFICATION CHECKLIST

After implementing these fixes, verify:

1. **Endpoint exists:**
   ```bash
   curl -X OPTIONS https://yamenmod91.pythonanywhere.com/api/attendance
   # Should return 200 with CORS headers
   ```

2. **Database table created:**
   ```sql
   SELECT * FROM attendance LIMIT 1;
   # Should not error
   ```

3. **Blueprint registered:**
   ```python
   # In Flask shell
   from app import app
   print(app.url_map)
   # Should see /api/attendance routes
   ```

4. **Test from Flutter app:**
   - Login as receptionist
   - Go to QR Scanner
   - Scan a customer QR code
   - Click "Check-In Only"
   - Should see: ✅ "Customer checked in successfully!"
   - Should NOT see: ❌ "Failed to check in" or "Resource not found"

5. **Check logs:**
   ```bash
   # On PythonAnywhere
   tail -f /var/log/yamenmod91.pythonanywhere.com.error.log
   # Should see successful POST requests to /api/attendance
   ```

---

## 🔄 ALTERNATIVE: If Using Django

```python
# views/attendance.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Attendance, Customer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_attendance(request):
    """Record customer check-in"""
    customer_id = request.data.get('customer_id')
    check_in_time = request.data.get('check_in_time')
    action = request.data.get('action', 'check_in_only')
    subscription_id = request.data.get('subscription_id')
    
    if not customer_id:
        return Response({
            'success': False,
            'error': 'customer_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if not customer.is_active:
        return Response({
            'success': False,
            'error': 'Customer account is inactive'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create attendance
    attendance = Attendance.objects.create(
        customer_id=customer_id,
        subscription_id=subscription_id,
        check_in_time=check_in_time or timezone.now(),
        branch_id=request.user.branch_id,
        action=action
    )
    
    return Response({
        'success': True,
        'message': 'Check-in recorded successfully',
        'data': {
            'attendance': {
                'id': attendance.id,
                'customer_id': customer_id,
                'customer_name': customer.full_name,
                'check_in_time': attendance.check_in_time.isoformat(),
                'branch_id': attendance.branch_id,
                'action': action
            }
        }
    }, status=status.HTTP_201_CREATED)

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/attendance', views.record_attendance, name='record_attendance'),
]
```

---

## 📊 EXPECTED BEHAVIOR AFTER FIX

### Before Fix:
```
Receptionist scans QR → Customer dialog shows → Click "Check-In" → ❌ ERROR: "Resource not found"
```

### After Fix:
```
Receptionist scans QR → Customer dialog shows → Click "Check-In" → ✅ SUCCESS: "Customer checked in successfully!"
```

---

## 🚨 IMPORTANT NOTES

1. **CORS Headers:** Make sure your backend has CORS enabled for POST requests to `/api/attendance`

2. **JWT Token:** The endpoint requires authentication. Make sure the receptionist is logged in.

3. **Branch Validation:** You may want to add logic to verify the customer belongs to the same branch as the receptionist.

4. **Subscription Deduction:** The attendance endpoint only RECORDS the check-in. Session/coin deduction should be handled separately via the `/api/subscriptions/{id}/deduct-session` endpoint (which the Flutter app already calls).

5. **Database Permissions:** Make sure your database user has CREATE and INSERT permissions on the attendance table.

---

**END OF FIX DOCUMENT**

**Action Required:** Implement this backend endpoint immediately  
**Estimated Time:** 30-45 minutes  
**Priority:** CRITICAL - App is currently unusable for receptionists

