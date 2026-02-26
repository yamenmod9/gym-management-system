# 🔑 TEST CREDENTIALS - Quick Reference

## 📱 STAFF APP LOGIN

### Owner (Full System Access)
```
Username: owner
Password: owner123
Access: All branches, all features
```

### Branch Managers (Choose one)
```
Dragon Club:
  Username: manager_dragon
  Password: manager123
  Branch: 1 (Dragon Club)

Phoenix Fitness:
  Username: manager_phoenix
  Password: manager123
  Branch: 2 (Phoenix Fitness)

Tiger Gym:
  Username: manager_tiger
  Password: manager123
  Branch: 3 (Tiger Gym)
```

### Receptionists (Choose one)
```
Dragon Club:
  Username: reception_dragon_1
  Password: reception123
  Branch: 1

Phoenix Fitness:
  Username: reception_phoenix_1
  Password: reception123
  Branch: 2

Tiger Gym:
  Username: reception_tiger_1
  Password: reception123
  Branch: 3
```

### Accountants (Choose one)
```
Central (All branches):
  Username: accountant_central
  Password: accountant123
  Branch: None (sees all)

Dragon Club:
  Username: accountant_dragon
  Password: accountant123
  Branch: 1
```

---

## 📱 CLIENT APP LOGIN (Customers)

### First-Time Login Customers (Must Change Password)

These customers have `password_changed = false` and their temporary passwords are visible to staff:

```
Customer 1 (Dragon Club):
  Phone: 01077827639
  Password: [Generated, e.g., "RX04AF"]
  Status: First-time user
  
Customer 2 (Dragon Club):
  Phone: 01077827640
  Password: [Generated, e.g., "SI19IC"]
  Status: First-time user

Customer 21 (Phoenix Fitness):
  Phone: 01077827660
  Password: [Generated]
  Status: First-time user

...and 72 more first-time users (75 total)
```

**To Get Actual Passwords:**
1. Run the seed script - it will print all passwords
2. OR login to staff app as reception
3. Go to "All Customers"
4. Find customer with `password_changed: false`
5. See password field (e.g., "RX04AF")
6. Give to customer for login

### Regular Login Customers (Password Already Changed)

These customers have `password_changed = true`:
- Customers 31-60 (Dragon Club)
- Customers 88-115 (Phoenix Fitness)  
- Customers 133-150 (Tiger Gym)

**You cannot see their passwords** - they set their own

---

## 🎯 TEST WORKFLOW

### Test 1: Staff Registration Flow
1. Login as reception: `reception_dragon_1` / `reception123`
2. Register new customer:
   - Name: "Ahmed Test"
   - Phone: "01099999999"
   - Email: "test@example.com"
   - Branch: Dragon Club
3. **System returns temporary password** (e.g., "AB12CD")
4. Give password to customer

### Test 2: Client First Login Flow
1. Open client app
2. Enter phone: "01099999999"
3. Enter password: "AB12CD" (from registration)
4. Click Login
5. **Forced to change password screen**
6. Enter current password: "AB12CD"
7. Enter new password: "MyPassword123"
8. Confirm password: "MyPassword123"
9. Click "Change Password"
10. **Success!** Navigate to home screen

### Test 3: Staff View Customer Password
1. Login as reception
2. Go to "All Customers"
3. Find "Ahmed Test" customer
4. Expand card
5. **Should see:** "Password: AB12CD" with copy button
6. After customer changes password:
7. **Should see:** "Password: ••••••••" (hidden)

### Test 4: QR Code Check-In
1. Login as reception
2. Click "Scan QR" button
3. Scan customer QR code (or enter customer ID)
4. **Shows:**
   - Customer name and details
   - Active subscription info
   - Remaining sessions/coins
5. Click "Deduct 1 Session"
6. **Success!** Shows new remaining count

### Test 5: Owner Dashboard
1. Login as owner
2. **Should see:**
   - Total Revenue: ~164,521 EGP
   - Active Subscriptions: 87
   - Total Customers: 150
   - Branches: 3
3. Click "Branches" tab
4. **Should list:**
   - Dragon Club (60 customers)
   - Phoenix Fitness (55 customers)
   - Tiger Gym (35 customers)
5. Click "Staff" tab
6. **Should list:** 14 staff members

---

## 📊 EXPECTED DATA SUMMARY

### Branches
- **Total:** 3
- Dragon Club (Branch 1): Capacity 150
- Phoenix Fitness (Branch 2): Capacity 120
- Tiger Gym (Branch 3): Capacity 100

### Customers
- **Total:** 150
- Branch 1: 60 (30 first-time, 30 password changed)
- Branch 2: 55 (27 first-time, 28 password changed)
- Branch 3: 35 (18 first-time, 17 password changed)

### Subscriptions
- **Active:** 87
  - Branch 1: 45 active
  - Branch 2: 27 active
  - Branch 3: 15 active
- **Expired:** 63

### Revenue (Active Subscriptions)
- **Monthly** (45 @ 1200 EGP): 54,000 EGP
- **Coins** (25 @ avg 1200 EGP): ~30,000 EGP
- **Sessions** (17 @ avg 1440 EGP): ~24,480 EGP
- **Total:** ~164,521 EGP

### Staff
- **Total:** 14
- 1 Owner (system-wide)
- 3 Managers (1 per branch)
- 6 Receptionists (2 per branch)
- 4 Accountants (1 central + 3 branch)

### Expenses
- **Total:** 45
- Pending: 10 (3 urgent)
- Approved: 25
- Rejected: 10

### Complaints
- **Total:** 20
- Pending: 8
- Investigating: 7
- Resolved: 5

### Attendance Records
- **Total:** 500+
- Last 30 days
- Linked to active customers

---

## 🔍 DEBUGGING TIPS

### Issue: Can't see temporary passwords
**Check:**
- Backend returns `temporary_password` field in customer data
- Field is ONLY present when `password_changed = false`
- Field contains plain text (e.g., "RX04AF"), not hash

### Issue: Dashboard shows 0s
**Check:**
- Backend `/api/reports/revenue` returns correct data
- OR `/api/customers` and `/api/subscriptions` return data
- Check Flutter console for debug logs:
  - `💰 Loading revenue data...`
  - `✅ Total Customers: 150`
  - `✅ Active Subscriptions: 87`

### Issue: QR scanner doesn't work
**Check:**
- Backend `/api/customers/{id}` returns customer data
- Backend `/api/subscriptions?customer_id={id}` returns active sub
- Backend `/api/attendance` accepts POST with `deduct_session: true`

### Issue: Client can't login
**Check:**
- Backend `/api/client/auth/login` accepts phone + password
- Password verification uses `check_password_hash()`
- Response includes `password_changed` field

### Issue: Client not forced to change password
**Check:**
- Backend login response has `password_changed: false`
- Flutter app checks this field in `ClientAuthProvider`
- Navigation goes to change-password screen

---

## 📚 RELATED DOCUMENTS

- **SINGLE_COMPREHENSIVE_BACKEND_PROMPT.md** - Complete backend implementation guide
- **COMPLETE_BACKEND_API_SPECIFICATION.md** - Full list of all 60+ endpoints
- **CLAUDE_TEMP_PASSWORD_FIX_PROMPT.md** - Temporary password system details
- **COMPREHENSIVE_FIX_SUMMARY_FEB14.md** - Complete status of all features

---

*Quick Reference Guide - February 14, 2026*

