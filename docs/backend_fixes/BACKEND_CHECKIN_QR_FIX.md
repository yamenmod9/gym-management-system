# BACKEND FIX - CHECK-IN & QR CODE ENDPOINTS

## Date: February 15, 2026

## 🚨 CRITICAL ISSUES TO FIX

### Issue 1: Check-In Fails After QR Scan
**Symptom:** "Failed to check in" error after scanning customer QR code

**Root Cause:** Missing or incorrect attendance/check-in endpoints

---

## 📋 REQUIRED BACKEND ENDPOINTS

### 1. SESSION DEDUCTION ENDPOINT ⚠️ MISSING

**Endpoint:** `POST /api/subscriptions/{subscription_id}/deduct-session`

**Purpose:** Deduct one session from a subscription

**Request Body:**
```json
{
  "customer_id": 115,
  "amount": 1
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Session deducted successfully",
  "subscription": {
    "id": 45,
    "customer_id": 115,
    "type": "monthly",
    "remaining_sessions": 11,
    "status": "active"
  }
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "error": "No sessions remaining"
}
```

**Business Logic:**
- Verify subscription exists and is active
- Check remaining_sessions > 0
- Deduct 1 from remaining_sessions
- Return updated subscription data
- Log the deduction with timestamp

---

### 2. COINS USAGE ENDPOINT ⚠️ MISSING

**Endpoint:** `POST /api/subscriptions/{subscription_id}/use-coins`

**Purpose:** Deduct coins from a coins-based subscription

**Request Body:**
```json
{
  "customer_id": 115,
  "amount": 1
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "1 coin(s) used successfully",
  "subscription": {
    "id": 46,
    "customer_id": 115,
    "type": "coins",
    "coins": 19,
    "status": "active"
  }
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "error": "Insufficient coins"
}
```

**Business Logic:**
- Verify subscription type is "coins"
- Check coins >= amount requested
- Deduct amount from coins
- If coins == 0, set status to "expired"
- Return updated subscription data

---

### 3. ATTENDANCE/CHECK-IN ENDPOINT ✅ UPDATE REQUIRED

**Endpoint:** `POST /api/attendance`

**Purpose:** Record customer check-in (with or without session deduction)

**Request Body (Check-in Only):**
```json
{
  "customer_id": 115,
  "check_in_time": "2026-02-15T14:30:00Z",
  "action": "check_in_only"
}
```

**Request Body (With Deduction):**
```json
{
  "customer_id": 115,
  "subscription_id": 45,
  "check_in_time": "2026-02-15T14:30:00Z",
  "action": "check_in_with_deduction"
}
```

**Response (Success - 200 or 201):**
```json
{
  "success": true,
  "message": "Check-in recorded successfully",
  "attendance": {
    "id": 1234,
    "customer_id": 115,
    "customer_name": "Adel Saad",
    "check_in_time": "2026-02-15T14:30:00Z",
    "branch_id": 1
  }
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "error": "Customer not found"
}
```

**Business Logic:**
- Verify customer exists and is_active = true
- Create attendance record with timestamp
- Store branch_id from staff's branch
- Store subscription_id if provided
- Return success confirmation

---

### 4. GET CUSTOMER BY ID ✅ EXISTING (VERIFY)

**Endpoint:** `GET /api/customers/{customer_id}`

**Purpose:** Fetch customer details for check-in dialog

**Response (200):**
```json
{
  "success": true,
  "customer": {
    "id": 115,
    "full_name": "Adel Saad",
    "phone": "01025867870",
    "email": "customer115@example.com",
    "branch_id": 2,
    "branch_name": "Dragon Club",
    "is_active": true,
    "qr_code": "customer_id:115",
    "temp_password": "AB12CD",
    "password_changed": false,
    "height": 172.0,
    "weight": 92.0,
    "bmi": 31.1,
    "bmi_category": "Obese"
  }
}
```

**Required Fields:**
- `id` (integer)
- `full_name` (string)
- `phone` (string)
- `branch_id` (integer)
- `is_active` (boolean)
- `qr_code` (string) - Should be in format "customer_id:{id}"

---

### 5. GET ACTIVE SUBSCRIPTIONS ✅ EXISTING (VERIFY)

**Endpoint:** `GET /api/subscriptions?customer_id={id}&status=active`

**Purpose:** Get customer's active subscriptions for check-in

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 45,
      "customer_id": 115,
      "service_id": 1,
      "type": "monthly",
      "status": "active",
      "remaining_sessions": 12,
      "start_date": "2026-02-01",
      "end_date": "2026-03-01",
      "branch_id": 1
    }
  ]
}
```

**Alternative Response Format (also acceptable):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 46,
        "customer_id": 115,
        "type": "coins",
        "coins": 20,
        "status": "active",
        "validity_months": 12,
        "branch_id": 1
      }
    ]
  }
}
```

**Required Fields:**
- `id` (integer)
- `customer_id` (integer)
- `type` (string: "monthly", "coins", "annual")
- `status` (string: "active", "expired", "frozen")
- `remaining_sessions` (integer) - for session-based
- `coins` (integer) - for coin-based
- `end_date` (string) - for time-based

---

## 🔧 IMPLEMENTATION CHECKLIST

### Backend Python/Django Implementation

#### 1. Create Session Deduction Endpoint
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deduct_session(request, subscription_id):
    """Deduct one session from subscription"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        
        # Verify customer matches (optional security check)
        customer_id = request.data.get('customer_id')
        if subscription.customer_id != customer_id:
            return Response({
                'success': False,
                'error': 'Customer ID mismatch'
            }, status=400)
        
        # Check if active
        if subscription.status != 'active':
            return Response({
                'success': False,
                'error': 'Subscription is not active'
            }, status=400)
        
        # Check remaining sessions
        if subscription.remaining_sessions <= 0:
            return Response({
                'success': False,
                'error': 'No sessions remaining'
            }, status=400)
        
        # Deduct session
        subscription.remaining_sessions -= 1
        
        # If no sessions left, mark as expired
        if subscription.remaining_sessions == 0:
            subscription.status = 'expired'
        
        subscription.save()
        
        # Log the deduction (optional but recommended)
        # SessionLog.objects.create(
        #     subscription=subscription,
        #     action='deduct',
        #     amount=1,
        #     timestamp=timezone.now()
        # )
        
        return Response({
            'success': True,
            'message': 'Session deducted successfully',
            'subscription': {
                'id': subscription.id,
                'customer_id': subscription.customer_id,
                'type': subscription.type,
                'remaining_sessions': subscription.remaining_sessions,
                'status': subscription.status
            }
        }, status=200)
        
    except Subscription.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Subscription not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
```

#### 2. Create Coins Usage Endpoint
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_coins(request, subscription_id):
    """Use coins from subscription"""
    try:
        subscription = Subscription.objects.get(id=subscription_id)
        amount = request.data.get('amount', 1)
        
        # Verify subscription type
        if subscription.type != 'coins':
            return Response({
                'success': False,
                'error': 'Not a coins-based subscription'
            }, status=400)
        
        # Check if active
        if subscription.status != 'active':
            return Response({
                'success': False,
                'error': 'Subscription is not active'
            }, status=400)
        
        # Check sufficient coins
        if subscription.coins < amount:
            return Response({
                'success': False,
                'error': 'Insufficient coins'
            }, status=400)
        
        # Deduct coins
        subscription.coins -= amount
        
        # If no coins left, mark as expired
        if subscription.coins == 0:
            subscription.status = 'expired'
        
        subscription.save()
        
        return Response({
            'success': True,
            'message': f'{amount} coin(s) used successfully',
            'subscription': {
                'id': subscription.id,
                'customer_id': subscription.customer_id,
                'type': subscription.type,
                'coins': subscription.coins,
                'status': subscription.status
            }
        }, status=200)
        
    except Subscription.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Subscription not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
```

#### 3. Update Attendance Endpoint
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_attendance(request):
    """Record customer check-in"""
    try:
        customer_id = request.data.get('customer_id')
        check_in_time = request.data.get('check_in_time')
        subscription_id = request.data.get('subscription_id')
        action = request.data.get('action', 'check_in_only')
        
        # Verify customer exists
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Customer not found'
            }, status=404)
        
        # Check if customer is active
        if not customer.is_active:
            return Response({
                'success': False,
                'error': 'Customer account is inactive'
            }, status=400)
        
        # Get staff's branch from token
        staff_branch_id = request.user.branch_id
        
        # Create attendance record
        attendance = Attendance.objects.create(
            customer_id=customer_id,
            subscription_id=subscription_id,
            check_in_time=check_in_time or timezone.now(),
            branch_id=staff_branch_id,
            action=action
        )
        
        return Response({
            'success': True,
            'message': 'Check-in recorded successfully',
            'attendance': {
                'id': attendance.id,
                'customer_id': customer_id,
                'customer_name': customer.full_name,
                'check_in_time': attendance.check_in_time.isoformat(),
                'branch_id': staff_branch_id
            }
        }, status=201)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
```

#### 4. Add URL Routes
```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... existing routes ...
    
    # Subscription deduction
    path('subscriptions/<int:subscription_id>/deduct-session', 
         views.deduct_session, 
         name='deduct_session'),
    path('subscriptions/<int:subscription_id>/use-coins', 
         views.use_coins, 
         name='use_coins'),
    
    # Attendance
    path('attendance', 
         views.record_attendance, 
         name='record_attendance'),
]
```

---

## 🧪 TESTING THE FIX

### Test 1: Session Deduction
```bash
# Test deducting a session
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/45/deduct-session \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 115, "amount": 1}'

# Expected: 200, remaining_sessions decremented
```

### Test 2: Coins Usage
```bash
# Test using coins
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/46/use-coins \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 115, "amount": 1}'

# Expected: 200, coins decremented
```

### Test 3: Check-In
```bash
# Test check-in
curl -X POST https://yamenmod91.pythonanywhere.com/api/attendance \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 115,
    "check_in_time": "2026-02-15T14:30:00Z",
    "action": "check_in_only"
  }'

# Expected: 201, attendance record created
```

---

## 📊 DATABASE SCHEMA UPDATES

### Attendance Table (if doesn't exist)
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    subscription_id INTEGER REFERENCES subscriptions(id),
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP,
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    action VARCHAR(50) DEFAULT 'check_in_only',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

CREATE INDEX idx_attendance_customer ON attendance(customer_id);
CREATE INDEX idx_attendance_date ON attendance(check_in_time);
CREATE INDEX idx_attendance_branch ON attendance(branch_id);
```

### Session Log Table (optional, for auditing)
```sql
CREATE TABLE session_log (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id),
    action VARCHAR(20) NOT NULL, -- 'deduct', 'add', 'reset'
    amount INTEGER NOT NULL,
    previous_value INTEGER,
    new_value INTEGER,
    staff_id INTEGER REFERENCES staff(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);
```

---

## 🔍 DEBUGGING CHECKLIST

If check-in still fails after backend updates:

### 1. Check Backend Logs
```python
# Add debug logging in Django
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Check-in request for customer: {customer_id}")
logger.debug(f"Request data: {request.data}")
logger.debug(f"Staff branch: {request.user.branch_id}")
```

### 2. Verify Permissions
- Ensure staff user has permission to create attendance records
- Check `IsAuthenticated` permission is working
- Verify JWT token is valid

### 3. Check CORS Settings
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-flutter-app.com",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    # ... other headers
]
```

### 4. Verify Customer Data
```sql
-- Check customer exists and is active
SELECT id, full_name, is_active, branch_id 
FROM customers 
WHERE id = 115;

-- Check active subscriptions
SELECT id, customer_id, type, status, remaining_sessions, coins
FROM subscriptions
WHERE customer_id = 115 AND status = 'active';
```

---

## ✅ SUCCESS CRITERIA

After implementing these fixes, verify:

1. **QR Code Scan** → Customer dialog appears ✅
2. **Click "Check-In Only"** → Success message appears ✅
3. **Click "Deduct 1 Session"** → Session count decreases ✅
4. **Remaining sessions** → Updates in real-time ✅
5. **Attendance record** → Created in database ✅
6. **No errors** → Check both app and backend logs ✅

---

## 📝 SUMMARY

**3 New Endpoints Required:**
1. `POST /api/subscriptions/{id}/deduct-session`
2. `POST /api/subscriptions/{id}/use-coins`
3. `POST /api/attendance` (update existing or create new)

**1 Database Table Required:**
- `attendance` table with proper foreign keys

**Estimated Implementation Time:** 2-3 hours

**Priority:** 🔥 CRITICAL - Core functionality blocked

---

**Last Updated:** February 15, 2026  
**Status:** ⚠️ Awaiting Backend Implementation

