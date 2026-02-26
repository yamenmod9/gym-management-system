# ✅ Backend Endpoints Checklist

## 🔴 Critical - Must Fix Immediately

- [ ] **POST /api/subscriptions/activate** ⚠️ FAILING - User can't activate subscriptions

## 🟡 High Priority - Core Features

### Authentication (Working ✅)
- [x] POST /api/auth/login
- [ ] POST /api/auth/logout
- [ ] GET /api/auth/profile

### Customer Management
- [ ] POST /api/customers/register (Check QR code generation)
- [ ] GET /api/customers
- [ ] GET /api/customers/{id}

### Services
- [ ] GET /api/services (Required for subscription activation)

### Subscriptions
- [ ] GET /api/subscriptions
- [ ] GET /api/subscriptions/{id}
- [ ] POST /api/subscriptions/renew
- [ ] POST /api/subscriptions/freeze
- [ ] POST /api/subscriptions/stop

### Payments
- [ ] GET /api/payments
- [ ] POST /api/payments/record
- [ ] POST /api/payments/daily-closing

## 🟢 Medium Priority - Management Features

### Branch Management
- [ ] GET /api/branches
- [ ] GET /api/branches/{id}
- [ ] GET /api/branches/{id}/performance

### Complaints
- [ ] GET /api/complaints
- [ ] POST /api/complaints/submit

### Reports
- [ ] GET /api/reports/revenue
- [ ] GET /api/reports/daily
- [ ] GET /api/reports/weekly
- [ ] GET /api/reports/monthly
- [ ] GET /api/reports/branch-comparison
- [ ] GET /api/reports/employee-performance

## 🔵 Lower Priority - Advanced Features

### Finance (Accountant Features)
- [ ] GET /api/finance/daily-sales
- [ ] GET /api/finance/expenses
- [ ] GET /api/finance/cash-differences

### Attendance (Manager Features)
- [ ] GET /api/attendance
- [ ] GET /api/attendance/by-branch

### Alerts (Owner Features)
- [ ] GET /api/alerts
- [ ] GET /api/alerts/smart

### Client Mobile App
- [ ] POST /api/clients/request-activation
- [ ] POST /api/clients/verify-activation
- [ ] GET /api/clients/profile
- [ ] GET /api/clients/subscription
- [ ] GET /api/clients/entry-history
- [ ] POST /api/clients/refresh-qr

---

## 📝 Testing Priority

### Test in This Order:

1. **Login** (Already working ✅)
   ```bash
   curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"reception1","password":"reception123"}'
   ```

2. **Get Services** (Need this first)
   ```bash
   curl -X GET https://yamenmod91.pythonanywhere.com/api/services \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Register Customer**
   ```bash
   curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "full_name": "Test Customer",
       "phone": "01234567890",
       "gender": "male",
       "age": 25,
       "weight": 75.0,
       "height": 1.75,
       "bmi": 24.5,
       "bmi_category": "Normal",
       "bmr": 1750.0,
       "daily_calories": 2450.0,
       "branch_id": 1
     }'
   ```

4. **Activate Subscription** ⚠️ CRITICAL
   ```bash
   curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/activate \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "customer_id": 1,
       "service_id": 1,
       "branch_id": 1,
       "amount": 500.00,
       "payment_method": "cash"
     }'
   ```

5. **Record Payment**
   ```bash
   curl -X POST https://yamenmod91.pythonanywhere.com/api/payments/record \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "customer_id": 1,
       "amount": 500.00,
       "payment_method": "cash",
       "branch_id": 1,
       "subscription_id": 1
     }'
   ```

---

## 🎯 Minimum Viable Backend

To get the app working, you MUST implement at least these:

### Essential Endpoints (10 total):
1. ✅ POST /api/auth/login (Working)
2. GET /api/services
3. POST /api/customers/register
4. GET /api/customers
5. **POST /api/subscriptions/activate** ⚠️ MOST CRITICAL
6. GET /api/subscriptions
7. POST /api/subscriptions/renew
8. POST /api/payments/record
9. POST /api/payments/daily-closing
10. GET /api/branches

With just these 10 endpoints, the reception staff can:
- Login ✅
- View services
- Register new customers
- Activate subscriptions ⚠️
- Record payments
- Do daily closing
- View customers

---

## 📊 Feature Completion by Role

### Reception (10 endpoints needed)
- [x] Login
- [ ] Register customers
- [ ] Activate subscriptions ⚠️
- [ ] Renew subscriptions
- [ ] Record payments
- [ ] Daily closing
- [ ] View customers
- [ ] View services
- [ ] Submit complaints
- [ ] View branches

**Status:** 1/10 (10%) - Blocked by subscription activation

---

### Manager (15 endpoints needed)
All reception features plus:
- [ ] Branch performance
- [ ] Staff attendance
- [ ] Daily reports
- [ ] View complaints
- [ ] Revenue by service

**Status:** 1/15 (7%) - Depends on reception features

---

### Accountant (12 endpoints needed)
- [x] Login
- [ ] Daily sales reports
- [ ] Expense management
- [ ] Cash differences
- [ ] Weekly reports
- [ ] Monthly reports
- [ ] Revenue reports
- [ ] Branch comparison
- [ ] View all payments

**Status:** 1/12 (8%) - Finance features not implemented

---

### Owner (20+ endpoints needed)
All features plus:
- [ ] Smart alerts
- [ ] Multi-branch comparison
- [ ] Employee performance
- [ ] System-wide reports

**Status:** 1/20+ (5%) - Advanced features not implemented

---

## 🚨 Current Blocker

**The subscription activation endpoint is blocking the entire app!**

Users can login and see the interface, but they **cannot activate any subscriptions**, which is the core feature of the gym management system.

### Impact:
- ❌ Can't activate new subscriptions
- ❌ Can't record payments (needs subscription first)
- ❌ Can't test renewal features
- ❌ App appears "broken" to users

### Solution:
Implement `/api/subscriptions/activate` endpoint immediately.

See: **QUICK_BACKEND_FIX_PROMPT.md** for detailed implementation guide.

---

## 📚 Documentation Files

1. **BACKEND_API_REQUIREMENTS.md** - Complete API documentation (all 38 endpoints)
2. **QUICK_BACKEND_FIX_PROMPT.md** - Urgent fix for subscription activation
3. **BACKEND_ENDPOINTS_CHECKLIST.md** (this file) - Quick reference checklist

---

## ✅ How to Use This Checklist

1. Start with the **Critical** section
2. Test each endpoint with curl
3. Check off when working
4. Move to next priority level
5. Update status after each implementation

---

## 🎯 Success Criteria

### Minimum Success (MVP):
- [ ] Users can activate subscriptions ⚠️
- [ ] Users can register customers
- [ ] Users can record payments
- [ ] Users can do daily closing

### Full Success:
- [ ] All reception features working (10/10)
- [ ] All manager features working (15/15)
- [ ] All accountant features working (12/12)
- [ ] All owner features working (20/20)

---

## 📞 Need Help?

Base URL: `https://yamenmod91.pythonanywhere.com`

Test Credentials:
- reception1 / reception123
- manager1 / manager123
- accountant1 / accountant123
- owner / owner123

Check server logs if endpoints return 500 errors!

