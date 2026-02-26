# 🔐 Test Credentials - Production-Quality Dataset

## Overview

The database has been seeded with realistic test data representing a multi-branch gym operation. Below are all available test accounts organized by role and branch.

---

## 🏢 Database Summary

### System Statistics
- **Total Users:** 14 staff members
- **Total Customers:** 150 across 3 branches
- **Total Subscriptions:** 123 (83 Active, 4 Frozen, 1 Stopped, 35 Expired)
- **Total Transactions:** 472 (164,521 EGP revenue)
- **Total Complaints:** 50 (11 open)
- **Total Expenses:** 75 (10 pending, 56 approved, 9 rejected)
- **Daily Closings:** 75 (5 with high-priority alerts)

### Branch Distribution
1. **Dragon Club** (Best Performance)
   - 60 customers
   - 12 complaints (1 open)
   - High revenue performance

2. **Phoenix Club** (Medium Performance)
   - 55 customers
   - 16 complaints (0 open)
   - Steady growth

3. **Tiger Club** (Growing)
   - 35 customers
   - 22 complaints (10 open)
   - Most opportunities for improvement

---

## 👤 Test User Accounts

### 1. Owner Account (Full System Access)

```
Username: owner
Password: owner123
Role: Owner
Access: All branches, all features
```

**What you can test:**
- ✅ Multi-branch analytics dashboard
- ✅ Revenue comparison across branches
- ✅ Smart alerts (2 expiring subscriptions, 11 expiring in 7 days)
- ✅ Staff leaderboard across all branches
- ✅ Operational monitor
- ✅ Organization-wide complaint management (50 total)
- ✅ Financial decision support

**Expected Dashboard Stats:**
- Total Revenue: ~164,521 EGP
- Active Subscriptions: 83
- Total Customers: 150
- Open Complaints: 11
- Pending Expenses: 10 (3 urgent)

---

### 2. Branch Manager Accounts

#### Dragon Club Manager (Best Branch)
```
Username: manager_dragon
Password: manager123
Role: Branch Manager
Branch: Dragon Club (ID: 1)
```

**What you can test:**
- ✅ Single-branch performance metrics
- ✅ Staff attendance tracking (2 front desk staff)
- ✅ Revenue by service analysis
- ✅ Daily operations summary
- ✅ Branch-level complaints (12 total, 1 open)

**Expected Dashboard Stats:**
- Branch Customers: 60
- Active Subscriptions: ~35-40
- Branch Revenue: ~60,000-70,000 EGP
- Complaints: 12 (1 open)

#### Phoenix Club Manager (Medium Branch)
```
Username: manager_phoenix
Password: manager123
Role: Branch Manager
Branch: Phoenix Club (ID: 2)
```

**What you can test:**
- ✅ Medium-performance branch operations
- ✅ Staff management
- ✅ Service revenue tracking
- ✅ Complaint resolution (16 total, 0 open)

**Expected Dashboard Stats:**
- Branch Customers: 55
- Active Subscriptions: ~30-35
- Branch Revenue: ~50,000-60,000 EGP
- Complaints: 16 (all resolved)

#### Tiger Club Manager (Growing Branch)
```
Username: manager_tiger
Password: manager123
Role: Branch Manager
Branch: Tiger Club (ID: 3)
```

**What you can test:**
- ✅ Growing branch with challenges
- ✅ High complaint volume management (22 total, 10 open)
- ✅ Staff performance improvement
- ✅ Revenue growth tracking

**Expected Dashboard Stats:**
- Branch Customers: 35
- Active Subscriptions: ~15-20
- Branch Revenue: ~40,000-50,000 EGP
- Complaints: 22 (10 open - needs attention!)

---

### 3. Front Desk / Reception Accounts

#### Dragon Club Reception (2 Staff Members)
```
Username: reception_dragon_1
Password: reception123
Role: Reception/Front Desk
Branch: Dragon Club

Username: reception_dragon_2
Password: reception123
Role: Reception/Front Desk
Branch: Dragon Club
```

#### Phoenix Club Reception (2 Staff Members)
```
Username: reception_phoenix_1
Password: reception123
Role: Reception/Front Desk
Branch: Phoenix Club

Username: reception_phoenix_2
Password: reception123
Role: Reception/Front Desk
Branch: Phoenix Club
```

#### Tiger Club Reception (2 Staff Members)
```
Username: reception_tiger_1
Password: reception123
Role: Reception/Front Desk
Branch: Tiger Club

Username: reception_tiger_2
Password: reception123
Role: Reception/Front Desk
Branch: Tiger Club
```

**What you can test:**
- ✅ Quick customer registration with auto health metrics
- ✅ Subscription activation (30-365 days)
- ✅ Subscription renewal (123 customers available)
- ✅ Subscription freeze (4 currently frozen)
- ✅ Subscription stop (1 currently stopped)
- ✅ Payment recording (Cash, Network, Transfer)
- ✅ Daily closing with cash reconciliation
- ✅ Complaint submission

**Expected Features:**
- Customer list with search/filter
- Quick registration form
- Subscription management panel
- Payment methods: Cash (40%), Network (40%), Transfer (20%)
- Daily closing alerts (5 high-priority alerts exist)

---

### 4. Accountant Accounts

#### Central Accountant (2 Accounts)
```
Username: accountant_central_1
Password: accountant123
Role: Accountant
Branch: Central (access to all branches)

Username: accountant_central_2
Password: accountant123
Role: Accountant
Branch: Central (access to all branches)
```

**What you can test:**
- ✅ Daily sales tracking across all branches
- ✅ Expense management (75 expenses total)
- ✅ Expense approval workflow (10 pending)
- ✅ Urgent expense alerts (3 over 7 days old)
- ✅ Cash reconciliation
- ✅ Multi-branch financial comparison
- ✅ Weekly & monthly reports
- ✅ Advanced filtering

**Expected Dashboard Stats:**
- Total Revenue: 164,521 EGP
- Pending Expenses: 10 (3 urgent)
- Approved Expenses: 56 (77,070 EGP)
- Rejected Expenses: 9
- Payment Methods Distribution: 40% Cash, 40% Network, 20% Transfer

#### Branch Accountants (2 Accounts)
```
Username: accountant_branch_1
Password: accountant123
Role: Accountant
Branch: Specific branch access

Username: accountant_branch_2
Password: accountant123
Role: Accountant
Branch: Specific branch access
```

**What you can test:**
- ✅ Single-branch financial operations
- ✅ Branch-specific expense management
- ✅ Branch cash reconciliation
- ✅ Branch revenue reports

---

## 🎯 Test Scenarios by Role

### Owner Testing Scenarios

1. **Multi-Branch Analytics**
   - Login as `owner`
   - View dashboard with 3 branches
   - Compare Dragon (best) vs Tiger (growing)
   - Check revenue distribution: 164,521 EGP total

2. **Smart Alerts**
   - Check expiring subscriptions alert (2 in 48h, 11 in 7 days)
   - Review open complaints (11 total, mostly in Tiger branch)
   - Monitor pending expenses (10, including 3 urgent)

3. **Staff Performance**
   - View staff leaderboard
   - Compare reception staff across branches
   - Analyze performance by branch

4. **Operational Monitor**
   - Check daily closing alerts (5 high-priority)
   - Review discrepancies (±100-200 EGP alerts)
   - Monitor cash reconciliation issues

### Manager Testing Scenarios

1. **Dragon Club Excellence** (`manager_dragon`)
   - View best-performing branch metrics
   - Check low complaint rate (1 open)
   - Review high customer retention (60 customers)
   - Analyze revenue performance

2. **Phoenix Club Stability** (`manager_phoenix`)
   - Monitor medium-performance operations
   - Verify zero open complaints
   - Track steady customer growth (55)
   - Review service revenue mix

3. **Tiger Club Growth** (`manager_tiger`)
   - Address high complaint volume (10 open)
   - Plan customer acquisition (35 current)
   - Improve staff performance
   - Implement retention strategies

### Reception Testing Scenarios

1. **Customer Registration** (Any reception account)
   - Register new customer
   - Auto-calculate BMI, BMR, calories
   - Activate first subscription
   - Record payment (Cash/Network/Transfer)

2. **Subscription Management**
   - Search for existing customer
   - Renew expiring subscription (35 expired available)
   - Freeze active subscription (4 currently frozen)
   - Stop subscription if needed (1 currently stopped)

3. **Daily Closing**
   - Record daily transactions
   - Calculate cash balance
   - Submit closing report
   - Handle discrepancy alerts

4. **Complaint Handling**
   - Submit customer complaint
   - Categorize issue type
   - Provide detailed description
   - Track resolution status

### Accountant Testing Scenarios

1. **Expense Management** (Central accountant)
   - Review 10 pending expenses
   - Prioritize 3 urgent (over 7 days)
   - Approve/reject based on policy
   - Track approved total (77,070 EGP)

2. **Financial Reports**
   - Generate daily sales report (472 transactions)
   - Compare branch revenues
   - Analyze payment method distribution (40/40/20)
   - Review weekly/monthly trends

3. **Cash Reconciliation**
   - Check daily closings (75 total)
   - Investigate 5 high-priority alerts
   - Verify cash balances
   - Resolve discrepancies

---

## 🔍 Data Distribution Details

### Customer Distribution
- **Total:** 150 customers
- **Dragon Club:** 60 (40%)
- **Phoenix Club:** 55 (37%)
- **Tiger Club:** 35 (23%)

### Subscription Status
- **Active:** 83 (67%)
  - 2 expiring in 48 hours ⚠️
  - 11 expiring in 7 days ⚠️
- **Frozen:** 4 (3%)
- **Stopped:** 1 (1%)
- **Expired:** 35 (29%)

### Transaction Breakdown (472 total)
- **Subscription Payments:** 123 (26%)
- **Renewal Transactions:** 69 (15%)
  - 35% have multi-renewal history
- **Freeze Payments:** 37 (8%)
- **Miscellaneous:** 243 (51%)
  - Personal training
  - Merchandise
  - Other services

### Payment Methods
- **Cash:** 40% (~189 transactions)
- **Network:** 40% (~189 transactions)
- **Transfer:** 20% (~94 transactions)

### Expenses (75 total)
- **Pending:** 10 (13%)
  - 3 urgent (over 7 days) ⚠️
- **Approved:** 56 (75%) - 77,070 EGP
- **Rejected:** 9 (12%)

### Complaints (50 total)
- **Dragon Club:** 12 (1 open)
- **Phoenix Club:** 16 (0 open)
- **Tiger Club:** 22 (10 open) ⚠️

### Daily Closings (75 total)
- **Normal:** 62 (±30 EGP variance)
- **Medium Alerts:** 8 (±50-100 EGP)
- **High Priority:** 5 (±100-200 EGP) ⚠️

---

## ⚠️ Known Issues to Test

### High Priority Items
1. **Tiger Club Complaints** - 10 open (needs manager attention)
2. **Expiring Subscriptions** - 2 in 48h, 11 in 7 days
3. **Urgent Expenses** - 3 pending over 7 days
4. **Cash Discrepancies** - 5 high-priority closing alerts

### Expected Alerts
- Owner dashboard should show 4 alert types
- Tiger branch manager should see high complaint count
- Reception should see expiring subscription warnings
- Accountant should see urgent expense notifications

---

## 🧪 Testing Checklist

### Login Flow
- [ ] Owner login successful
- [ ] All 3 manager logins work
- [ ] All 6 reception logins work
- [ ] All 4 accountant logins work
- [ ] Wrong username shows error
- [ ] Wrong password shows error
- [ ] Role-based dashboard loads correctly

### Owner Dashboard
- [ ] Shows 3 branches
- [ ] Total revenue: ~164,521 EGP
- [ ] 150 customers displayed
- [ ] Smart alerts visible (4 types)
- [ ] Branch comparison works
- [ ] Staff leaderboard loads

### Manager Dashboards
- [ ] Dragon: 60 customers, 1 open complaint
- [ ] Phoenix: 55 customers, 0 open complaints
- [ ] Tiger: 35 customers, 10 open complaints
- [ ] Revenue metrics per branch
- [ ] Staff attendance tracking

### Reception Operations
- [ ] Customer registration with health metrics
- [ ] Subscription activation
- [ ] Renewal process (35 expired available)
- [ ] Freeze subscription (4 frozen)
- [ ] Payment recording (3 methods)
- [ ] Daily closing submission

### Accountant Features
- [ ] 10 pending expenses visible
- [ ] 3 urgent expenses highlighted
- [ ] Multi-branch revenue: 164,521 EGP
- [ ] Payment distribution: 40/40/20
- [ ] Expense approval workflow
- [ ] Financial reports generation

---

## 📊 Expected Performance

### API Response Times
- Login: < 1 second
- Dashboard load: < 2 seconds
- Customer list: < 1 second
- Transaction history: < 2 seconds
- Reports generation: < 3 seconds

### UI Expectations
- Bottom navigation bar (not tabs)
- Modern gradient themes
- Large readable numbers (20px)
- Smooth transitions
- Responsive touch interactions

---

## 🔧 Troubleshooting

### Login Issues
```
Problem: "Username not found"
Solution: Check spelling, use exact usernames above

Problem: "Incorrect password"
Solution: Use password123 for staff, owner123 for owner

Problem: "Cannot connect to server"
Solution: Check network, verify backend is running
```

### Data Issues
```
Problem: No customers showing
Solution: Database might not be seeded, check backend logs

Problem: Wrong revenue amounts
Solution: Clear app cache, re-login

Problem: Missing branches
Solution: Verify branch data in backend database
```

---

## 📝 Notes

### Password Policy
- All test passwords use format: `{role}123`
- Owner: `owner123`
- Managers: `manager123`
- Reception: `reception123`
- Accountants: `accountant123`

### Branch IDs
- Dragon Club: ID 1
- Phoenix Club: ID 2
- Tiger Club: ID 3

### Test Data Characteristics
- Realistic revenue distributions
- Weighted customer placement
- Historical transaction patterns
- Multi-renewal customer histories
- Genuine complaint scenarios
- Cash reconciliation challenges

---

## 🚀 Quick Start

```bash
# 1. Verify backend is running
curl https://yamenmod91.pythonanywhere.com/api/health

# 2. Clean Flutter build
flutter clean && flutter pub get

# 3. Run app
flutter run

# 4. Login as owner
Username: owner
Password: owner123

# 5. Explore multi-branch analytics!
```

---

**Last Updated:** February 8, 2026  
**Dataset Version:** Production v1.0  
**Total Test Accounts:** 14 users  
**Total Customers:** 150  
**Total Revenue:** 164,521 EGP
