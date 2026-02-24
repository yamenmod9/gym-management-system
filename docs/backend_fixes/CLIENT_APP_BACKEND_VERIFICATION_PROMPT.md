# 🔍 CLIENT APP BACKEND VERIFICATION PROMPT

**Date:** February 14, 2026

## 🎯 Objective

Verify and implement all required backend API endpoints for the gym client mobile app to ensure full functionality, especially for:
1. ✅ QR Code generation and display
2. ✅ Subscription details retrieval
3. ✅ Entry history tracking
4. ✅ Profile data with active subscription

---

## 📱 CLIENT APP REQUIRED ENDPOINTS

### ✅ 1. Client Authentication

#### POST `/api/client/auth/login`
**Request Body:**
```json
{
  "phone": "01210801216",  // Can be phone or email
  "password": "password123"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "token_type": "Bearer"
  }
}
```

**Status:** ✅ Working

---

### ✅ 2. Client Profile with Active Subscription

#### GET `/api/client/me`
**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Yamen Mahmoud",
    "phone": "01210801216",
    "email": "yamen.mahmoud912@gmail.com",
    "qr_code": "GYM-151",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "subscription_status": "active",
    "created_at": "2026-02-10T12:25:15.514866",
    "active_subscription": {
      "id": 127,
      "subscription_type": "coins",
      "service_name": "Monthly Gym Membership",
      "service_type": "gym",
      "service_id": 1,
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "customer_id": 151,
      "customer_name": "Yamen Mahmoud",
      "customer_phone": "01210801216",
      "status": "active",
      "start_date": "2026-02-13",
      "end_date": "2026-03-15",
      "remaining_coins": 20,
      "coins": 20,
      "can_access": true,
      "is_expired": false,
      "freeze_count": 0,
      "total_frozen_days": 0,
      "classes_attended": 0,
      "created_at": "2026-02-13T22:33:40.936511",
      "freeze_history": []
    }
  }
}
```

**Important Fields:**
- `qr_code`: Used to generate QR code visual
- `active_subscription`: Contains all subscription details
- `active_subscription.remaining_coins` or `active_subscription.coins`: Number of remaining entry coins
- `active_subscription.start_date` and `active_subscription.end_date`: Subscription validity period
- `active_subscription.freeze_history`: Array of freeze periods (if any)

**Status:** ✅ Working (verified in logs)

---

### ❓ 3. QR Code Generation (Optional Enhancement)

#### GET `/api/client/qr`
**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "qr_code": "GYM-151",
    "qr_image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "customer_name": "Yamen Mahmoud",
    "has_active_subscription": true,
    "expires_at": "2026-02-14T23:59:59Z"
  }
}
```

**Current Implementation:**
- Frontend generates QR code from `qr_code` field in profile
- QR code data is the customer's QR code string (e.g., "GYM-151")
- Uses `qr_flutter` package to render QR code visually

**Status:** ⚠️ Not required (frontend handles it), but backend can optionally provide pre-generated QR images

---

### ❌ 4. Subscription Details Endpoint

#### GET `/api/client/subscription`
**Headers:**
```
Authorization: Bearer {access_token}
```

**Current Status:** 🔴 Returns 404 Error

**Solution:** This endpoint is not needed if the profile endpoint (`/api/client/me`) already includes `active_subscription` data (which it does). The frontend has been updated to use the profile endpoint instead.

**Alternative:** If you want to keep this endpoint, it should return:

```json
{
  "success": true,
  "data": {
    "subscription_type": "coins",
    "service_name": "Monthly Gym Membership",
    "service_type": "gym",
    "status": "active",
    "start_date": "2026-02-13",
    "end_date": "2026-03-15",
    "expiry_date": "2026-03-15",
    "remaining_coins": 20,
    "coins": 20,
    "allowed_services": ["Gym Access", "Pool"],
    "freeze_history": []
  }
}
```

**Frontend Fix:** ✅ Updated to use `/api/client/me` instead

---

### ❌ 5. Entry History Endpoint

#### GET `/api/client/entry-history`
**Headers:**
```
Authorization: Bearer {access_token}
```

**Current Status:** 🔴 Returns 404 Error

**Required Implementation:**

**Expected Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "customer_id": 151,
      "subscription_id": 127,
      "branch": "Dragon Club",
      "branch_id": 1,
      "service": "Gym Access",
      "service_id": 1,
      "date": "2026-02-14",
      "time": "10:30:00",
      "datetime": "2026-02-14T10:30:00Z",
      "coins_used": 1,
      "entry_type": "scan",
      "created_at": "2026-02-14T10:30:00Z"
    },
    {
      "id": 2,
      "customer_id": 151,
      "subscription_id": 127,
      "branch": "Dragon Club",
      "branch_id": 1,
      "service": "Pool",
      "service_id": 2,
      "date": "2026-02-13",
      "time": "14:15:00",
      "datetime": "2026-02-13T14:15:00Z",
      "coins_used": 2,
      "entry_type": "scan",
      "created_at": "2026-02-13T14:15:00Z"
    }
  ]
}
```

**Database Schema Suggestion:**

```sql
CREATE TABLE entry_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    subscription_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    coins_used INTEGER DEFAULT 1,
    entry_type VARCHAR(50) DEFAULT 'scan',
    entry_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id),
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);
```

**Implementation Notes:**
1. This endpoint should be created to track when customers use their subscriptions
2. Each time a receptionist scans a customer's QR code, create an entry log
3. Deduct coins from the subscription's `remaining_coins` field
4. Return entries sorted by newest first (`ORDER BY entry_datetime DESC`)
5. Consider pagination for customers with many entries

**Python Backend Example:**

```python
@client_bp.route('/entry-history', methods=['GET'])
@jwt_required()
def get_entry_history():
    """Get customer's entry history"""
    customer_id = get_jwt_identity()
    
    # Query entry logs for this customer
    entries = db.session.query(
        EntryLog,
        Branch.name.label('branch_name'),
        Service.name.label('service_name')
    ).join(
        Branch, EntryLog.branch_id == Branch.id
    ).join(
        Service, EntryLog.service_id == Service.id
    ).filter(
        EntryLog.customer_id == customer_id
    ).order_by(
        EntryLog.entry_datetime.desc()
    ).limit(100).all()
    
    # Format response
    data = []
    for entry, branch_name, service_name in entries:
        data.append({
            'id': entry.id,
            'customer_id': entry.customer_id,
            'subscription_id': entry.subscription_id,
            'branch': branch_name,
            'branch_id': entry.branch_id,
            'service': service_name,
            'service_id': entry.service_id,
            'date': entry.entry_datetime.strftime('%Y-%m-%d'),
            'time': entry.entry_datetime.strftime('%H:%M:%S'),
            'datetime': entry.entry_datetime.isoformat(),
            'coins_used': entry.coins_used,
            'entry_type': entry.entry_type,
            'created_at': entry.created_at.isoformat()
        })
    
    return jsonify({
        'success': True,
        'data': data
    }), 200
```

**Status:** 🔴 Not Implemented - Frontend shows graceful error message

---

### ✅ 6. Change Password

#### POST `/api/client/change-password`
**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "current_password": "temp_password",
  "new_password": "MyNewSecurePass123!"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Status:** ✅ Assumed working (used after first login)

---

## 🔄 QR Code Scanning Workflow

### Current Staff App Implementation:
1. **Receptionist scans QR code** → Gets customer ID from QR (e.g., "GYM-151" → ID 151)
2. **Looks up customer** → Fetches customer details including active subscription
3. **Verifies access** → Checks if subscription is active and has remaining coins
4. **Grants entry** → Allows customer in

### What Should Happen (Backend Enhancement Needed):
1. Receptionist scans QR code → Gets customer ID
2. **Staff app calls** `POST /api/staff/qr-scan` with:
   ```json
   {
     "qr_code": "GYM-151",
     "branch_id": 1,
     "service_id": 1
   }
   ```
3. **Backend should:**
   - Verify customer exists and has active subscription
   - Check `remaining_coins > 0` (if coins-based)
   - Deduct 1 coin (or configured amount)
   - Create entry log record
   - Return success/failure

**Suggested Staff Endpoint:**

```python
@staff_bp.route('/qr-scan', methods=['POST'])
@jwt_required()
@role_required(['front_desk', 'reception', 'branch_manager'])
def scan_qr_code():
    """Process QR code scan and log entry"""
    data = request.get_json()
    qr_code = data.get('qr_code')
    branch_id = data.get('branch_id')
    service_id = data.get('service_id', 1)
    
    # Extract customer ID from QR code
    # Assuming format is "GYM-{id}"
    customer_id = int(qr_code.split('-')[1])
    
    # Get customer and active subscription
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({
            'success': False,
            'message': 'Customer not found'
        }), 404
    
    subscription = customer.get_active_subscription()
    if not subscription:
        return jsonify({
            'success': False,
            'message': 'No active subscription found'
        }), 403
    
    # Check if subscription can be used
    if subscription.subscription_type == 'coins':
        if subscription.remaining_coins <= 0:
            return jsonify({
                'success': False,
                'message': 'No coins remaining'
            }), 403
        
        # Deduct coin
        subscription.remaining_coins -= 1
    
    # Create entry log
    entry_log = EntryLog(
        customer_id=customer_id,
        subscription_id=subscription.id,
        branch_id=branch_id,
        service_id=service_id,
        coins_used=1,
        entry_type='scan',
        entry_datetime=datetime.now()
    )
    
    db.session.add(entry_log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Entry logged successfully',
        'data': {
            'customer_name': customer.full_name,
            'remaining_coins': subscription.remaining_coins,
            'subscription_status': subscription.status
        }
    }), 200
```

---

## 🎯 Priority Actions for Backend Team

### High Priority (Client App Won't Work Without These):
1. ✅ **Client Login** - Working
2. ✅ **Client Profile with Active Subscription** - Working
3. ✅ **QR Code in Profile** - Working (frontend generates visual)

### Medium Priority (Features Currently Broken):
4. ❌ **Entry History Endpoint** - Returns 404
   - Frontend shows graceful error message
   - Implement `/api/client/entry-history` endpoint
   - Return customer's gym visit history

5. ⚠️ **Subscription Details Endpoint** - Returns 404
   - Frontend now uses profile endpoint instead
   - Can remove this endpoint or implement it as alternative

### Low Priority (Nice to Have):
6. ❓ **QR Scan Logging** - Staff app doesn't log entries yet
   - Implement `/api/staff/qr-scan` endpoint
   - Automatically deduct coins and create entry logs
   - Improve tracking and analytics

7. ❓ **QR Code Refresh** - Not implemented yet
   - Optional: implement `/api/client/qr/refresh` for temporary QR codes
   - Current: QR code is permanent (customer ID based)

---

## 📊 Current Status Summary

| Feature | Backend Status | Frontend Status | Priority |
|---------|---------------|-----------------|----------|
| Login | ✅ Working | ✅ Working | High |
| Profile | ✅ Working | ✅ Working | High |
| QR Display | ✅ Working | ✅ Working | High |
| Subscription Details | ⚠️ Uses Profile | ✅ Fixed | Medium |
| Entry History | ❌ 404 Error | ✅ Graceful Error | Medium |
| QR Scan Logging | ❌ Not Implemented | ⚠️ No Backend | Low |
| Change Password | ✅ Assumed Working | ✅ Working | High |

---

## 🧪 Testing Checklist

### Backend Team Should Test:

1. **Client Profile Endpoint:**
   ```bash
   curl -X GET https://yamenmod91.pythonanywhere.com/api/client/me \
     -H "Authorization: Bearer {valid_client_token}"
   ```
   - ✅ Should return customer data
   - ✅ Should include `active_subscription` object
   - ✅ Should include `qr_code` field

2. **Entry History Endpoint (To Implement):**
   ```bash
   curl -X GET https://yamenmod91.pythonanywhere.com/api/client/entry-history \
     -H "Authorization: Bearer {valid_client_token}"
   ```
   - ❌ Currently returns 404
   - ✅ Should return array of entry logs

3. **QR Scan Endpoint (To Implement):**
   ```bash
   curl -X POST https://yamenmod91.pythonanywhere.com/api/staff/qr-scan \
     -H "Authorization: Bearer {valid_staff_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "qr_code": "GYM-151",
       "branch_id": 1,
       "service_id": 1
     }'
   ```
   - ❌ Currently not implemented
   - ✅ Should deduct coins and log entry

---

## 📝 Notes for Backend Implementation

### Important Considerations:

1. **QR Code Format:**
   - Current format: `GYM-{customer_id}` (e.g., "GYM-151")
   - Should be permanent (tied to customer ID)
   - No need for expiry unless you want temporary codes

2. **Subscription Data Structure:**
   - Make sure `active_subscription` is included in profile response
   - Include `remaining_coins` or `coins` field
   - Include `freeze_history` as empty array if no freezes

3. **Entry Logs:**
   - Each scan should create a record
   - Track: customer, subscription, branch, service, datetime, coins used
   - Enable history tracking for analytics

4. **Error Handling:**
   - Return proper HTTP status codes (404, 403, 401, etc.)
   - Include `success` boolean in all responses
   - Provide clear error messages

---

## ✅ Frontend Fixes Applied

1. ✅ **Back Button** - Fixed router redirect logic
2. ✅ **QR Code Display** - Shows QR code even if null, with fallback
3. ✅ **Subscription Screen** - Uses profile endpoint instead of subscription endpoint
4. ✅ **Entry History** - Shows graceful error message when endpoint not available
5. ✅ **Settings Screen** - Fixed null safety compilation errors

---

## 🚀 Next Steps

### For Backend Team:
1. Implement `/api/client/entry-history` endpoint
2. Implement `/api/staff/qr-scan` endpoint for logging entries
3. Test all client endpoints with actual mobile app
4. Verify `active_subscription` data structure in profile response

### For Frontend Team:
1. Test QR code scanning workflow with backend once entry logging is implemented
2. Add pull-to-refresh for subscription screen
3. Add local caching for better offline experience
4. Implement push notifications for subscription expiry warnings

---

**Generated:** February 14, 2026
**Client App Version:** Latest
**Backend Base URL:** https://yamenmod91.pythonanywhere.com/api

