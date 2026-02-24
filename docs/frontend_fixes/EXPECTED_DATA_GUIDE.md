# 📊 Expected Data in Flutter App - Production Dataset

## Overview

This document details what data the Flutter app should display after the backend database has been seeded with production-quality test data. Use this as a reference to verify the app is correctly fetching and displaying backend data.

---

## 🏢 Global System Statistics

These numbers should be visible in the **Owner Dashboard**:

### Revenue & Financial
- **Total Revenue:** ~164,521 EGP
- **Payment Distribution:**
  - Cash: 40% (~65,808 EGP)
  - Network: 40% (~65,808 EGP)
  - Transfer: 20% (~32,905 EGP)

### Customers & Subscriptions
- **Total Customers:** 150
  - Dragon Club: 60 (40%)
  - Phoenix Club: 55 (37%)
  - Tiger Club: 35 (23%)
- **Active Subscriptions:** 83
- **Frozen Subscriptions:** 4
- **Stopped Subscriptions:** 1
- **Expired Subscriptions:** 35

### Transactions
- **Total Transactions:** 472
  - Subscription Payments: 123
  - Renewal Transactions: 69
  - Freeze Payments: 37
  - Miscellaneous: 243

### Alerts & Issues
- **Open Complaints:** 11 (out of 50 total)
- **Pending Expenses:** 10 (3 marked urgent)
- **Expiring Subscriptions:**
  - In 48 hours: 2
  - In 7 days: 11

---

## 👔 Owner Dashboard Expected Data

### Login Credentials
```
Username: owner
Password: owner123
```

### Dashboard Overview Card
```
Total Revenue:          164,521 EGP
Active Subscriptions:   83
Total Customers:        150
Open Complaints:        11
```

### Smart Alerts Section (4 Alert Types)

#### 1. Expiring Subscriptions Alert
```
⚠️ 13 subscriptions expiring soon
- 2 expire in 48 hours (URGENT)
- 11 expire in 7 days
Action: Contact customers for renewal
```

#### 2. Open Complaints Alert
```
⚠️ 11 complaints require attention
Branch Breakdown:
- Dragon Club: 1 open
- Phoenix Club: 0 open
- Tiger Club: 10 open ⚠️
Action: Review and resolve, especially Tiger Club
```

#### 3. Pending Expenses Alert
```
⚠️ 10 expenses awaiting approval
- 3 urgent (pending over 7 days) 🔴
- Total pending amount: [varies]
Action: Review and approve/reject
```

#### 4. Cash Discrepancy Alert
```
⚠️ 5 daily closings with high-priority alerts
- Discrepancies of ±100-200 EGP
- Requires investigation
Action: Review cash reconciliation
```

### Branch Performance Comparison

#### Dragon Club (Best Performance)
```
Rank: #1 🥇
Customers: 60
Revenue: ~60,000-70,000 EGP (highest)
Active Subs: ~35-40
Open Complaints: 1 (excellent)
Status: ✅ Exceeding targets
```

#### Phoenix Club (Medium Performance)
```
Rank: #2 🥈
Customers: 55
Revenue: ~50,000-60,000 EGP
Active Subs: ~30-35
Open Complaints: 0 (all resolved)
Status: ✅ Meeting targets
```

#### Tiger Club (Growing)
```
Rank: #3 🥉
Customers: 35
Revenue: ~40,000-50,000 EGP
Active Subs: ~15-20
Open Complaints: 10 ⚠️ (needs attention)
Status: ⚠️ Growth opportunity
```

### Staff Leaderboard (14 Total Staff)
```
By Role:
- Branch Managers: 3 (1 per branch)
- Reception/Front Desk: 6 (2 per branch)
- Central Accountants: 2
- Branch Accountants: 2

Top Performers:
[Should show transaction counts and performance metrics]
```

### Operational Monitor
```
Daily Closings Overview:
- Total: 75 closings
- Normal (±30 EGP): 62
- Medium alerts (±50-100 EGP): 8
- High priority (±100-200 EGP): 5 🔴

Recent High-Priority Alerts:
[List of 5 discrepancies requiring investigation]
```

---

## 🏋️ Branch Manager Dashboard Expected Data

### Dragon Club Manager
**Login:** `manager_dragon` / `manager123`

```
Branch Performance Card:
- Branch: Dragon Club
- Customers: 60
- Active Subscriptions: ~35-40
- Monthly Revenue: ~60,000-70,000 EGP
- Open Complaints: 1

Staff Performance (2 Reception):
- reception_dragon_1: [transaction count]
- reception_dragon_2: [transaction count]

Recent Transactions:
[List of latest subscriptions, payments, renewals]

Complaint Management:
- Total: 12 complaints
- Open: 1
- Resolved: 11
- Resolution Rate: 92%

Revenue by Service:
- Subscriptions: ~70%
- Personal Training: ~15%
- Merchandise: ~10%
- Other: ~5%
```

### Phoenix Club Manager
**Login:** `manager_phoenix` / `manager123`

```
Branch Performance Card:
- Branch: Phoenix Club
- Customers: 55
- Active Subscriptions: ~30-35
- Monthly Revenue: ~50,000-60,000 EGP
- Open Complaints: 0 ✅

Staff Performance (2 Reception):
- reception_phoenix_1: [transaction count]
- reception_phoenix_2: [transaction count]

Recent Transactions:
[List of latest subscriptions, payments, renewals]

Complaint Management:
- Total: 16 complaints
- Open: 0 ✅
- Resolved: 16
- Resolution Rate: 100% (excellent!)

Revenue by Service:
- Subscriptions: ~70%
- Personal Training: ~15%
- Merchandise: ~10%
- Other: ~5%
```

### Tiger Club Manager
**Login:** `manager_tiger` / `manager123`

```
Branch Performance Card:
- Branch: Tiger Club
- Customers: 35
- Active Subscriptions: ~15-20
- Monthly Revenue: ~40,000-50,000 EGP
- Open Complaints: 10 ⚠️

⚠️ ALERT: High complaint volume requires attention!

Staff Performance (2 Reception):
- reception_tiger_1: [transaction count]
- reception_tiger_2: [transaction count]

Recent Transactions:
[List of latest subscriptions, payments, renewals]

Complaint Management:
- Total: 22 complaints
- Open: 10 ⚠️
- Resolved: 12
- Resolution Rate: 55% (needs improvement)

Priority Actions:
1. Resolve 10 open complaints
2. Improve customer satisfaction
3. Increase customer acquisition (currently lowest)
4. Enhance staff training

Revenue by Service:
- Subscriptions: ~65%
- Personal Training: ~15%
- Merchandise: ~12%
- Other: ~8%
```

---

## 🎫 Reception Dashboard Expected Data

### Any Reception Account
**Examples:**
- `reception_dragon_1` / `reception123`
- `reception_phoenix_1` / `reception123`
- `reception_tiger_1` / `reception123`

### Customer List View
```
Total Customers (filtered by branch):
- Dragon reception: 60 customers
- Phoenix reception: 55 customers
- Tiger reception: 35 customers

Customer Card Display:
┌────────────────────────────────────┐
│ Ahmed Mohamed                      │
│ ID: C001                           │
│ Subscription: Active ✅             │
│ Expires: 2026-03-15                │
│ Phone: +20 100 123 4567            │
└────────────────────────────────────┘
```

### Subscription Status Distribution
```
Active: 83 total across all branches
- Will show filtered by branch
- Color coded: Green = Active, Orange = Frozen, Red = Expired

Frozen: 4 total
Stopped: 1 total
Expired: 35 total (renewal opportunities!)
```

### Quick Actions Available
```
✅ Register New Customer
✅ Activate Subscription (30, 60, 90, 180, 365 days)
✅ Renew Subscription (35 expired available)
✅ Freeze Subscription (4 currently frozen)
✅ Stop Subscription (1 currently stopped)
✅ Record Payment (Cash, Network, Transfer)
✅ Submit Daily Closing
✅ File Complaint
```

### Payment Recording Options
```
Payment Methods:
- 💵 Cash (40% of transactions)
- 💳 Network (40% of transactions)
- 🏦 Transfer (20% of transactions)

Recent Payment Distribution:
[Should show ~189 cash, ~189 network, ~94 transfer]
```

### Daily Closing Feature
```
Daily Closing Stats:
- Total closings in system: 75
- Normal closings: 62
- Alert-worthy: 13

Expected Cash Balance:
[System calculates based on transactions]

Actual Cash Balance:
[Reception staff enters]

Discrepancy Alerts:
- ±30 EGP: Normal ✅
- ±50-100 EGP: Medium alert ⚠️
- ±100+ EGP: High priority 🔴
```

### Customer Registration Form
```
Required Fields:
- Name ✅
- Phone ✅
- Address
- Gender (Male/Female)
- Birth Date
- Height (cm)
- Weight (kg)
- Activity Level

Auto-Calculated (on save):
- BMI (Body Mass Index)
- BMR (Basal Metabolic Rate)
- Daily Calories Needed

Fingerprint: Optional text identifier
```

---

## 💰 Accountant Dashboard Expected Data

### Central Accountant (Multi-Branch Access)
**Login:** `accountant_central_1` / `accountant123`

### Dashboard Overview
```
Financial Summary (All Branches):
- Total Revenue: 164,521 EGP
- Total Expenses (Approved): 77,070 EGP
- Net Profit: 87,451 EGP
- Pending Expenses: 10 (3 urgent ⚠️)

Transaction Count:
- Total: 472 transactions
- Subscription Payments: 123
- Renewals: 69
- Freezes: 37
- Miscellaneous: 243
```

### Payment Method Distribution
```
Revenue by Payment Type:
┌─────────────────────────────────┐
│ 💵 Cash:     65,808 EGP (40%)  │
│ 💳 Network:  65,808 EGP (40%)  │
│ 🏦 Transfer: 32,905 EGP (20%)  │
└─────────────────────────────────┘

Bar Chart:
Cash:     ████████████████████ 40%
Network:  ████████████████████ 40%
Transfer: ██████████          20%
```

### Expense Management
```
Expense Summary (75 total):

📊 By Status:
- Pending: 10 (13%)
  - Regular: 7
  - URGENT (7+ days): 3 🔴
- Approved: 56 (75%) - 77,070 EGP
- Rejected: 9 (12%)

Urgent Expenses Requiring Immediate Action:
1. [Expense 1] - 12 days pending
2. [Expense 2] - 9 days pending
3. [Expense 3] - 8 days pending

Approval Workflow:
[List of pending expenses with details]
- Expense amount
- Category
- Requesting branch
- Days pending
- Description
```

### Branch Financial Comparison
```
Revenue by Branch:
┌───────────────────────────────────┐
│ Dragon Club:  ~60,000-70,000 EGP  │ ████████████████████ (1st)
│ Phoenix Club: ~50,000-60,000 EGP  │ ████████████████ (2nd)
│ Tiger Club:   ~40,000-50,000 EGP  │ ████████████ (3rd)
└───────────────────────────────────┘

Expense by Branch:
[Distribution of approved expenses across branches]
```

### Daily Sales Report
```
Daily Transaction View (472 total):
- Filter by date range
- Filter by branch
- Filter by payment method
- Filter by transaction type

Sample Daily Record:
Date: 2026-02-07
Transactions: 8
Total Amount: 2,450 EGP
- 3 Subscriptions: 1,800 EGP
- 2 Renewals: 450 EGP
- 1 Freeze: 100 EGP
- 2 Misc: 100 EGP
```

### Cash Reconciliation
```
Daily Closing Review (75 records):

By Alert Level:
- ✅ Normal (±30 EGP): 62 closings
- ⚠️ Medium (±50-100 EGP): 8 closings
- 🔴 High Priority (±100-200 EGP): 5 closings

Recent High-Priority Discrepancies:
1. Dragon Club - 2026-02-06: -150 EGP 🔴
2. Phoenix Club - 2026-02-05: +120 EGP 🔴
3. Tiger Club - 2026-02-04: -180 EGP 🔴
4. Dragon Club - 2026-02-03: +100 EGP 🔴
5. Phoenix Club - 2026-02-02: -110 EGP 🔴

Action Required: Investigate and resolve discrepancies
```

### Weekly/Monthly Reports
```
Weekly Summary (Last 7 Days):
- Total Revenue: [calculated]
- Total Transactions: [count]
- Average Daily: [calculated]
- Top Revenue Day: [date]
- Payment Method Trend: [chart]

Monthly Summary:
- Total Revenue: 164,521 EGP
- Total Expenses: 77,070 EGP
- Net Profit: 87,451 EGP
- Profit Margin: 53%
- Transaction Count: 472
- Average Transaction: 348 EGP
```

### Branch Accountant (Single Branch)
**Login:** `accountant_branch_1` / `accountant123`

```
Similar to Central Accountant but:
- Data filtered to assigned branch only
- Cannot see other branch financials
- Branch-specific expense management
- Branch cash reconciliation
```

---

## 📊 Charts & Visualizations Expected

### Revenue Chart (Owner Dashboard)
```
Multi-Branch Bar Chart:
           70K
           60K
           50K
           40K
           30K
           20K
           10K
            0
         ┌────┬────┬────┐
         │████│████│████│
         │████│████│████│
         │████│████│████│
         │████│████│███ │
         └────┴────┴────┘
        Dragon Phoenix Tiger
```

### Subscription Status Pie Chart
```
Active:  83 (67%) ████████████████
Expired: 35 (29%) ██████████
Frozen:   4 (3%)  █
Stopped:  1 (1%)  ▌
```

### Payment Method Distribution
```
Cash:     40% ████████████████████
Network:  40% ████████████████████
Transfer: 20% ██████████
```

### Complaint Trend Line Chart
```
50 total complaints over time:
- Shows weekly/monthly trend
- Filtered by branch
- Resolution rate tracking
```

---

## 🎯 Data Validation Checklist

Use this checklist to verify the Flutter app is correctly displaying backend data:

### Owner Dashboard
- [ ] Total revenue shows ~164,521 EGP
- [ ] Customer count shows 150
- [ ] Branch count shows 3
- [ ] Active subscriptions shows 83
- [ ] Open complaints shows 11
- [ ] Smart alerts section displays 4 alert types
- [ ] Branch comparison chart shows all 3 branches
- [ ] Dragon Club shown as best performer
- [ ] Tiger Club shown with most complaints

### Manager Dashboards
- [ ] Dragon manager sees 60 customers
- [ ] Phoenix manager sees 55 customers
- [ ] Tiger manager sees 35 customers
- [ ] Each manager sees only their branch data
- [ ] Staff list shows 2 reception per branch
- [ ] Complaint counts match (12, 16, 22)
- [ ] Revenue metrics display correctly

### Reception Screens
- [ ] Customer list filtered by branch
- [ ] Dragon reception sees 60 customers
- [ ] Phoenix reception sees 55 customers
- [ ] Tiger reception sees 35 customers
- [ ] Subscription statuses color-coded
- [ ] 35 expired subscriptions available for renewal
- [ ] Payment method options: Cash, Network, Transfer
- [ ] Daily closing form accessible

### Accountant Screens
- [ ] Central accountant sees all branch data
- [ ] Total revenue: 164,521 EGP
- [ ] Pending expenses: 10
- [ ] Urgent expenses: 3 (highlighted)
- [ ] Approved expenses: 56 (77,070 EGP)
- [ ] Payment distribution: 40/40/20
- [ ] Daily closings: 75 total
- [ ] High-priority alerts: 5
- [ ] Branch comparison chart shows all branches

### Navigation & UI
- [ ] Bottom navigation bar (not tabs)
- [ ] Role-based color themes
- [ ] Smooth transitions
- [ ] Loading states handled
- [ ] Error messages displayed properly
- [ ] Refresh functionality works

---

## 🔍 Common Data Issues & Solutions

### Issue: Wrong Customer Count
**Expected:** 150 total (60/55/35 by branch)  
**Solution:** Check API endpoint, verify branch filtering

### Issue: Revenue Mismatch
**Expected:** ~164,521 EGP total  
**Solution:** Verify transaction summation logic, check decimal handling

### Issue: Missing Alerts
**Expected:** 4 alert types for owner  
**Solution:** Check alert calculation logic, verify data thresholds

### Issue: Empty Customer List
**Expected:** 35-60 per branch  
**Solution:** Verify branch_id filtering, check API response

### Issue: No Pending Expenses
**Expected:** 10 pending (3 urgent)  
**Solution:** Check expense status filtering, verify approval workflow

---

## 📝 Notes for Developers

### Data Consistency
- All monetary values in EGP
- Date format: ISO 8601 (YYYY-MM-DD)
- Phone format: +20 XXX XXX XXXX
- Percentages: Calculated, not stored

### API Response Structure
```json
{
  "success": true,
  "data": {
    "total_revenue": 164521.00,
    "customer_count": 150,
    "active_subscriptions": 83,
    "branches": [...]
  }
}
```

### Error Handling
- Network errors: Show retry option
- 401: Auto logout
- 403: Permission denied message
- 404: "No data found" message
- 500: "Server error, try again"

---

**Last Updated:** February 8, 2026  
**Data Version:** Production v1.0  
**Status:** ✅ Verified with seed.py
