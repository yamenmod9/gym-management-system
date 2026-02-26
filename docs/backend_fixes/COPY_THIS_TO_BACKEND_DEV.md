# 🎯 URGENT: Backend API Requirements for Gym App

## ⚡ TL;DR
Your gym Flutter app is complete and working, but **subscription activation is failing**. I need you to implement the backend API endpoints.

**Critical Issue:** `POST /api/subscriptions/activate` endpoint is not working.

---

## 🚨 IMMEDIATE ACTION REQUIRED

### Fix Subscription Activation Endpoint

**What the Flutter app is sending:**
```bash
POST /api/subscriptions/activate
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 123,
  "service_id": 1,
  "branch_id": 1,
  "amount": 500.00,
  "payment_method": "cash"
}
```

**What you need to return:**
```json
{
  "success": true,
  "message": "Subscription activated successfully",
  "data": {
    "subscription_id": 456,
    "customer_id": 123,
    "service_id": 1,
    "service_name": "Monthly Gym",
    "start_date": "2026-02-11",
    "end_date": "2026-03-11",
    "status": "active",
    "amount": 500.0,
    "payment_method": "cash",
    "receipt_number": "RCP-20260211-001",
    "created_at": "2026-02-11T10:30:00Z"
  }
}
```

### Implementation Steps:

1. **Validate the request:**
   - Check token is valid
   - Verify customer_id exists
   - Verify service_id exists
   - Check no active subscription exists for this customer

2. **Calculate subscription dates:**
   - start_date = today
   - Get service.duration_days from services table (e.g., 30 days for monthly)
   - end_date = start_date + service.duration_days

3. **Create database records:**
   - Insert into `subscriptions` table
   - Insert into `payments` table
   - Generate receipt_number: `RCP-YYYYMMDD-###`

4. **Return success response** as shown above

### Test Your Implementation:

```bash
# Step 1: Login (this should already work)
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"reception1","password":"reception123"}'

# Copy the access_token from response

# Step 2: Test subscription activation
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/activate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "customer_id": 1,
    "service_id": 1,
    "branch_id": 1,
    "amount": 500.00,
    "payment_method": "cash"
  }'
```

**Expected:** Status 201 with success response like the example above.

---

## 📋 ALL REQUIRED ENDPOINTS (43 Total)

I've created a **complete specification document** with all endpoints: `COMPLETE_BACKEND_REQUIREMENTS_PROMPT.md`

### Quick Overview:

**Phase 1: Critical (10 endpoints) - Need these for basic app usage**
1. ✅ POST /api/auth/login - **WORKING**
2. ❌ POST /api/subscriptions/activate - **FAILING - FIX FIRST**
3. POST /api/customers/register
4. GET /api/customers
5. GET /api/customers/{id}
6. GET /api/services
7. GET /api/subscriptions
8. POST /api/subscriptions/renew
9. POST /api/payments/record
10. POST /api/payments/daily-closing

**Phase 2: Core Features (11 endpoints) - For full reception workflow**
11. GET /api/subscriptions/{id}
12. GET /api/payments
13. POST /api/subscriptions/freeze
14. POST /api/subscriptions/stop
15. GET /api/branches
16. GET /api/branches/{id}
17. GET /api/services/{id}
18. GET /api/complaints
19. POST /api/complaints/submit
20. GET /api/reports/daily
21. GET /api/reports/revenue

**Phase 3: Management (11 endpoints) - For managers and accountants**
22. GET /api/reports/weekly
23. GET /api/reports/monthly
24. GET /api/reports/branch-comparison
25. GET /api/reports/employee-performance
26. GET /api/branches/{id}/performance
27. GET /api/finance/daily-sales
28. GET /api/finance/expenses
29. GET /api/finance/cash-differences
30. GET /api/attendance
31. GET /api/attendance/by-branch
32. GET /api/alerts

**Phase 4: Client Mobile App (8 endpoints) - Separate app for gym members**
33. POST /api/client/auth/login
34. POST /api/client/change-password
35. GET /api/client/me
36. GET /api/client/qr
37. POST /api/client/qr/refresh
38. GET /api/client/entry-history
39. GET /api/client/subscription
40. GET /api/client/subscriptions/history

**Phase 5: Advanced Features (3 endpoints)**
41. GET /api/alerts/smart
42. POST /api/auth/logout
43. GET /api/auth/profile

---

## 📖 Complete Documentation

Open the file: **`COMPLETE_BACKEND_REQUIREMENTS_PROMPT.md`**

This file contains:
- ✅ Complete request/response examples for ALL 43 endpoints
- ✅ Error handling specifications
- ✅ Database schema
- ✅ Authentication & security requirements
- ✅ Role-based access control rules
- ✅ Test commands for each endpoint
- ✅ Implementation priority order
- ✅ Python/Flask code examples

---

## 🎯 What Success Looks Like

### After Phase 1 (10 endpoints):
- ✅ Users can login
- ✅ Users can register customers
- ✅ Users can activate subscriptions (CRITICAL!)
- ✅ Users can process payments
- ✅ Users can do daily cash closing
- ✅ Basic reception workflow complete

### After Phase 2 (21 endpoints):
- ✅ Full customer management
- ✅ Complete subscription lifecycle
- ✅ Payment tracking
- ✅ Branch information
- ✅ Basic reports

### After Phase 3 (32 endpoints):
- ✅ Manager dashboards
- ✅ Accountant reports
- ✅ Financial tracking
- ✅ Employee performance
- ✅ Analytics

### After Phase 4 (40 endpoints):
- ✅ Client mobile app works
- ✅ Customers can login with phone
- ✅ Customers can view their subscription
- ✅ Customers can access QR code for gym entry
- ✅ Complete system operational

---

## 🔑 Important Standards

### All responses must follow this format:

**Success:**
```json
{
  "success": true,
  "message": "Descriptive message",
  "data": { /* actual data here */ }
}
```

**Error:**
```json
{
  "success": false,
  "message": "Error description",
  "error_code": "MACHINE_READABLE_CODE"
}
```

### Authentication:
- All endpoints (except login) require: `Authorization: Bearer {token}`
- Use JWT tokens
- Staff tokens: 1 day expiry
- Client tokens: 7 days expiry

### Date Format:
- Use ISO 8601: `YYYY-MM-DD` for dates
- Use ISO 8601: `YYYY-MM-DDTHH:MM:SSZ` for timestamps

### Payment Methods:
- Valid values: `"cash"`, `"card"`, `"transfer"`

### Subscription Status:
- Valid values: `"active"`, `"expired"`, `"frozen"`, `"stopped"`

---

## 🔒 Role-Based Access

| Role | Access |
|------|--------|
| **reception** | Own branch only (CRUD customers, subscriptions, payments) |
| **manager** | Own branch only (All reception + reports) |
| **accountant** | All branches (Read-only + financial reports) |
| **owner** | All branches (Full access to everything) |

---

## 🗄️ Database Tables (Minimum Required)

### customers
- id, full_name, phone (unique), email, national_id, birthdate, gender
- qr_code (unique), branch_id, weight, height
- password_hash (for client app), password_changed (boolean)
- created_at

### subscriptions
- id, customer_id, service_id, branch_id
- start_date, end_date, status
- amount, payment_method
- created_at

### payments
- id, customer_id, subscription_id (nullable)
- amount, payment_method, branch_id
- payment_date, receipt_number (unique)
- created_at

### services
- id, name, description
- duration_days, price, service_type
- is_active

### branches
- id, name, address, phone, email
- is_active

### users (staff)
- id, username (unique), password_hash
- full_name, role, branch_id
- is_active

---

## ⚙️ Setup Checklist

- [ ] Read `COMPLETE_BACKEND_REQUIREMENTS_PROMPT.md`
- [ ] Set up database tables
- [ ] Implement JWT authentication
- [ ] **Implement subscription activation endpoint (CRITICAL)**
- [ ] Test with provided curl commands
- [ ] Deploy to https://yamenmod91.pythonanywhere.com
- [ ] Verify in Flutter app
- [ ] Continue with remaining endpoints

---

## 🧪 Testing Credentials

**Base URL:** `https://yamenmod91.pythonanywhere.com/api`

**Staff Accounts:**
- reception1 / reception123
- manager1 / manager123
- accountant1 / accountant123
- owner / owner123

---

## ❓ Common Questions

**Q: Why is subscription activation failing?**
A: The endpoint either doesn't exist, returns wrong format, or has a server error. Check the logs.

**Q: What if customer already has active subscription?**
A: Return 409 error with message "Customer already has an active subscription"

**Q: How to generate receipt numbers?**
A: Format: `RCP-YYYYMMDD-XXX` where XXX is a sequence number for that day (001, 002, etc.)

**Q: What about CORS errors?**
A: Add these headers to all responses:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Q: How to calculate subscription end date?**
A: Get `duration_days` from the service record. Add it to start_date.

---

## 📞 Need Help?

Everything you need is in: **`COMPLETE_BACKEND_REQUIREMENTS_PROMPT.md`**

That file has:
- Complete specs for all 43 endpoints
- Request/response examples
- Error handling
- Code examples
- Database schema
- Test commands

---

## 🚀 Let's Get Started!

1. **Read the complete requirements:** Open `COMPLETE_BACKEND_REQUIREMENTS_PROMPT.md`
2. **Fix critical issue:** Implement `POST /api/subscriptions/activate`
3. **Test it:** Use the curl commands above
4. **Deploy:** Push to production
5. **Verify:** Test in Flutter app
6. **Continue:** Implement remaining endpoints in priority order

**The Flutter app is ready. We just need the backend endpoints!** 🎉

---

## 📊 Progress Tracking

Create a checklist as you implement:

```
Phase 1 (Critical):
☐ POST /api/subscriptions/activate ⚠️ URGENT
☐ POST /api/customers/register
☐ GET /api/customers
☐ GET /api/customers/{id}
☐ GET /api/services
☐ GET /api/subscriptions
☐ POST /api/subscriptions/renew
☐ POST /api/payments/record
☐ POST /api/payments/daily-closing
☐ GET /api/branches

Phase 2 (Core):
☐ [See full list in main document]

Phase 3 (Management):
☐ [See full list in main document]

Phase 4 (Client App):
☐ [See full list in main document]
```

---

**Questions? Check `COMPLETE_BACKEND_REQUIREMENTS_PROMPT.md` - it has everything!**

Good luck! 🚀

