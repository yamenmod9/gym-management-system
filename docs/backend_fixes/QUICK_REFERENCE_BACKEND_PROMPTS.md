# 🎯 QUICK REFERENCE: Backend Prompts for Claude Sonnet 4.5

**Date:** February 14, 2026

---

## 📦 THREE FILES CREATED FOR YOU

### 1. BACKEND_ENDPOINTS_COMPREHENSIVE_PROMPT.md
**Purpose:** Complete API endpoints specification  
**Size:** 53 endpoints (45 staff + 8 client)  
**Use:** Give this to Claude Sonnet 4.5 to implement backend API

**Contains:**
- Staff App: Auth, Customers, Subscriptions, QR Scanner, Payments, Services, Branches, Users, Reports, Complaints, Alerts, Finance, Attendance
- Client App: Activation code login, Profile, Subscription, Entry history, QR code
- Request/response examples
- Authentication rules
- Error handling

---

### 2. BACKEND_SEED_DATA_COMPREHENSIVE_PROMPT.md
**Purpose:** Complete database seed data specification  
**Size:** 4,500+ test records  
**Use:** Give this to Claude Sonnet 4.5 to create seed.py

**Contains:**
- 3 Branches
- 6 Services
- 14 Staff Users
- 150 Customers
- 136 Subscriptions
- 245 Payments (164,521 EGP)
- 3,500+ Entry Logs
- 50 Complaints
- 45 Expenses
- 280 Attendance Records
- 90 Cash Differences

---

### 3. CLAUDE_SONNET_PROMPTS_SUMMARY.md
**Purpose:** Overview and instructions  
**Use:** Read this first to understand how to use the other two files

---

## 🚀 HOW TO USE

### Step 1: Copy the Endpoints Document
Open: `BACKEND_ENDPOINTS_COMPREHENSIVE_PROMPT.md`  
Copy: **ENTIRE CONTENT**  
Send to Claude Sonnet 4.5 with:
```
Implement a complete REST API backend using this specification:
[PASTE ENTIRE DOCUMENT]
Use Flask/FastAPI with SQLAlchemy and PostgreSQL.
```

### Step 2: Copy the Seed Data Document
Open: `BACKEND_SEED_DATA_COMPREHENSIVE_PROMPT.md`  
Copy: **ENTIRE CONTENT**  
Send to Claude Sonnet 4.5 with:
```
Create a comprehensive seed.py file using this specification:
[PASTE ENTIRE DOCUMENT]
Ensure all test data matches the specified numbers exactly.
```

### Step 3: Test Everything
- [ ] Backend running on port 5001
- [ ] All 53 endpoints working
- [ ] Seed data loaded (4,500+ records)
- [ ] Owner dashboard shows 164,521 EGP
- [ ] QR scanner deducts coins
- [ ] Client app login works

---

## 🎯 WHAT THIS SOLVES

### Your Original Issues:
1. ✅ Owner dashboard shows 0s → Will show 164,521 EGP
2. ✅ Branches don't appear → Will show 3 branches
3. ✅ Staff don't appear → Will show 14 staff members
4. ✅ Manager data not showing → Will show branch-specific data
5. ✅ Accountant data not showing → Will show financial data
6. ✅ Settings screen missing → Already exists (no backend needed)

### Your New Request:
7. ✅ QR scanner for receptionist → NEW endpoints added:
   - `POST /api/qr/scan` - Check-in and deduct coins
   - `POST /api/qr/deduct-coins` - Manual coin deduction

### Still To Fix (Flutter UI):
8. ⚠️ Reception logout button hidden → I'll fix this separately (not backend related)

---

## 📊 EXPECTED DASHBOARD NUMBERS

After backend implementation with seed data:

**Owner Dashboard:**
```
Revenue:     164,521 EGP
Customers:   150
Branches:    3
Active Subs: 83
Alerts:      5 categories
```

**Dragon Manager:**
```
Customers:   60
Subs:        40
Revenue:     65,000 EGP
Complaints:  1 open
```

**Phoenix Manager:**
```
Customers:   55
Subs:        35
Revenue:     58,000 EGP
Complaints:  0 open ✅
```

**Tiger Manager:**
```
Customers:   35
Subs:        8
Revenue:     41,521 EGP
Complaints:  10 open ⚠️
```

---

## 🔐 TEST LOGINS

**Owner:** owner / owner123  
**Managers:** manager_dragon / manager123  
**Reception:** reception_dragon_1 / reception123  
**Accountant:** accountant_central_1 / accountant123  
**Client:** 01001234567 + activation code

---

## ✅ SUCCESS CRITERIA

Backend is complete when:
- [ ] All 53 endpoints return data
- [ ] Seed script loads 4,500+ records
- [ ] Owner sees 164,521 EGP revenue
- [ ] Manager sees branch-specific data only
- [ ] QR scan endpoint deducts coins correctly
- [ ] Client app can login and view profile
- [ ] No more 0s in any dashboard!

---

**Files Location:**
- `C:\Programming\Flutter\gym_frontend\BACKEND_ENDPOINTS_COMPREHENSIVE_PROMPT.md`
- `C:\Programming\Flutter\gym_frontend\BACKEND_SEED_DATA_COMPREHENSIVE_PROMPT.md`
- `C:\Programming\Flutter\gym_frontend\CLAUDE_SONNET_PROMPTS_SUMMARY.md`
- `C:\Programming\Flutter\gym_frontend\QUICK_REFERENCE_BACKEND_PROMPTS.md` (this file)

**Status:** Ready to use ✅  
**Date:** February 14, 2026

