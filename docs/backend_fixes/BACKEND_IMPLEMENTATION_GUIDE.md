# 🔧 BACKEND IMPLEMENTATION REQUIRED

**For:** Backend Developer  
**Priority:** High  
**Status:** Missing Endpoint  

---

## 🎯 WHAT'S NEEDED

The Flutter app is trying to activate subscriptions, but the backend endpoint doesn't exist.

**Missing Endpoint:** `POST /api/subscriptions/activate`

**Current Response:**
```json
{
  "error": "Resource not found",
  "success": false
}
HTTP 404 NOT FOUND
```

---

## 📝 IMPLEMENTATION REQUIREMENTS

### Endpoint Details

**Method:** POST  
**URL:** `https://yamenmod91.pythonanywhere.com/api/subscriptions/activate`  
**Content-Type:** `application/json`  
**Authentication:** Required (Bearer token)

### Request Body

```json
{
  "customer_id": 1,
  "service_id": 1,
  "branch_id": 1,
  "amount": 100.00,
  "payment_method": "cash",
  "start_date": "2026-02-10",
  "duration_months": 1,
  "notes": "Optional notes here"
}
```

### Required Fields
- `customer_id` (integer) - Must exist in customers table
- `service_id` (integer) - Must exist in services table
- `branch_id` (integer) - Must exist in branches table
- `amount` (float) - Must be > 0
- `payment_method` (string) - One of: "cash", "card", "bank_transfer"

### Optional Fields
- `start_date` (date) - Default: today
- `duration_months` (integer) - Default: 1
- `notes` (string) - Any additional notes

---

## ✅ SUCCESS RESPONSE

**HTTP Status:** 200 or 201

```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 123,
    "customer_id": 1,
    "customer_name": "John Doe",
    "service_id": 1,
    "service_name": "Monthly Gym Membership",
    "branch_id": 1,
    "branch_name": "Main Branch",
    "amount": 100.00,
    "payment_method": "cash",
    "start_date": "2026-02-10",
    "end_date": "2026-03-10",
    "duration_months": 1,
    "status": "active",
    "notes": "Optional notes here",
    "created_at": "2026-02-10T10:30:00Z",
    "created_by": "receptionist_username"
  }
}
```

---

## ❌ ERROR RESPONSES

### 400 - Validation Error
```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "customer_id": ["Customer not found"],
    "amount": ["Amount must be greater than 0"],
    "service_id": ["Service not found"]
  }
}
```

### 401 - Unauthorized
```json
{
  "success": false,
  "message": "Authentication required"
}
```

### 403 - Forbidden
```json
{
  "success": false,
  "message": "You don't have permission to activate subscriptions"
}
```

### 500 - Server Error
```json
{
  "success": false,
  "message": "Failed to activate subscription",
  "error": "Detailed error message for debugging"
}
```

---

## 🔨 IMPLEMENTATION CHECKLIST

### Database Operations
- [ ] Validate customer exists and is active
- [ ] Validate service exists and is available
- [ ] Validate branch exists
- [ ] Check for existing active subscription (optional - business rule)
- [ ] Create subscription record
- [ ] Calculate end_date based on start_date + duration_months
- [ ] Set status to "active"
- [ ] Record payment transaction
- [ ] Update customer's last_activity
- [ ] Log the action for audit trail

### Validation Rules
- [ ] customer_id must be a valid integer and exist
- [ ] service_id must be a valid integer and exist
- [ ] branch_id must be a valid integer and exist
- [ ] amount must be a positive number
- [ ] payment_method must be one of: "cash", "card", "bank_transfer"
- [ ] start_date must be a valid date (default: today)
- [ ] duration_months must be a positive integer (default: 1)
- [ ] User must be authenticated
- [ ] User must have "activate_subscription" permission

### Response Requirements
- [ ] Return HTTP 200 or 201 on success
- [ ] Include all subscription details in response
- [ ] Return HTTP 400 for validation errors with details
- [ ] Return HTTP 401 for authentication errors
- [ ] Return HTTP 500 for server errors with message

---

## 🧪 TESTING

### Test 1: Valid Request
```bash
curl -X POST "https://yamenmod91.pythonanywhere.com/api/subscriptions/activate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_VALID_TOKEN" \
  -d '{
    "customer_id": 1,
    "service_id": 1,
    "branch_id": 1,
    "amount": 100,
    "payment_method": "cash"
  }'
```

**Expected:** HTTP 200/201 with subscription details

### Test 2: Invalid Customer
```bash
curl -X POST "https://yamenmod91.pythonanywhere.com/api/subscriptions/activate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_VALID_TOKEN" \
  -d '{
    "customer_id": 999999,
    "service_id": 1,
    "branch_id": 1,
    "amount": 100,
    "payment_method": "cash"
  }'
```

**Expected:** HTTP 400 with error message "Customer not found"

### Test 3: No Authentication
```bash
curl -X POST "https://yamenmod91.pythonanywhere.com/api/subscriptions/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "service_id": 1,
    "branch_id": 1,
    "amount": 100,
    "payment_method": "cash"
  }'
```

**Expected:** HTTP 401 with error message "Authentication required"

---

## 📊 DATABASE SCHEMA REFERENCE

### Subscriptions Table (Example)
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    customer_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    duration_months INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### Payment Transaction (Example)
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    subscription_id INTEGER,
    customer_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

---

## 🔍 BUSINESS LOGIC

### On Successful Activation:

1. **Create Subscription Record**
   - Set status to "active"
   - Calculate end_date = start_date + duration_months
   - Store all subscription details

2. **Record Payment**
   - Create payment transaction record
   - Link to subscription
   - Set payment status to "completed"

3. **Update Customer**
   - Update last_activity timestamp
   - Optionally update customer status to "active"

4. **Audit Log** (Recommended)
   - Log who activated the subscription
   - Log when it was activated
   - Log what data was used

---

## 📞 VERIFICATION

After implementing, use this tool to test:

**Windows:**
```bash
test_subscription_backend.bat
```

**Linux/Mac:**
```bash
curl -X POST "https://yamenmod91.pythonanywhere.com/api/subscriptions/activate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"customer_id":1,"service_id":1,"branch_id":1,"amount":100,"payment_method":"cash"}'
```

**Expected Result:**
- HTTP Status: 200 or 201 (NOT 404!)
- Response: JSON with success: true
- Database: New subscription record created
- Database: Payment transaction recorded

---

## ⏱️ PRIORITY

**Impact:** High - Core feature blocked  
**Users Affected:** All receptionists  
**Frontend Status:** Complete and waiting  
**Estimated Backend Work:** 2-4 hours  

---

## 📁 RELATED FILES

**Frontend (No changes needed):**
- `lib/features/reception/providers/reception_provider.dart` - API call implementation
- `lib/core/api/api_endpoints.dart` - Endpoint definition

**Backend (Needs implementation):**
- Route handler for POST `/api/subscriptions/activate`
- Subscription activation business logic
- Payment recording logic

---

## 💬 QUESTIONS?

If you need clarification on:
- Request/response format
- Business logic requirements
- Database schema
- Validation rules

Contact the frontend developer who prepared this document.

---

**Status:** ⏳ Awaiting Implementation  
**Priority:** 🔴 High  
**Estimated Time:** 2-4 hours  

**🎯 Once implemented, test with `test_subscription_backend.bat` to verify!**

