# 🚀 PYTHONANYWHERE DEPLOYMENT GUIDE - February 17, 2026

## ✅ BACKEND FIXES PUSHED TO GITHUB

**Commit:** `dfde872`  
**Files Changed:**
- `app/models/customer.py`
- `app/routes/client_routes.py`

**Fixes Included:**
1. Entry history data structure (fixes JsonMap error)
2. Subscription status validation (coins + expiry)
3. Age calculation improvement
4. QR code active status validation

---

## 📋 DEPLOYMENT STEPS

### Step 1: Open PythonAnywhere Console

Go to: https://www.pythonanywhere.com/user/yamenmod9/

Click: **Consoles** → Open Bash console

---

### Step 2: Pull Latest Changes

```bash
cd ~/gym-management-system
git pull origin main
```

**Expected Output:**
```
remote: Enumerating objects: 8, done.
remote: Counting objects: 100% (8/8), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 8 (delta 7), reused 8 (delta 7), pack-reused 0
Unpacking objects: 100% (8/8), done.
From https://github.com/yamenmod9/gym-management-system
   fd84d09..dfde872  main       -> origin/main
Updating fd84d09..dfde872
Fast-forward
 app/models/customer.py       | 25 ++++++++++++++++++++-----
 app/routes/client_routes.py  | 35 ++++++++++++++++++++++++++++-------
 2 files changed, 48 insertions(+), 12 deletions(-)
```

---

### Step 3: Reload Web App

1. Go to **Web** tab in PythonAnywhere
2. Click the green **Reload** button for `yamenmod9.pythonanywhere.com`
3. Wait for "Reload successful" message

---

### Step 4: Verify Deployment

#### Test Entry History
```bash
# Get client token first
curl -X POST https://yamenmod9.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "01077827638", "password": "RX04AF"}'

# Save the token, then test entry history
curl -X GET https://yamenmod9.pythonanywhere.com/api/client/history \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "date": "2026-02-17",
      "time": "10:30:00",
      "branch": "Dragon Club",
      "service": "Gym Access",
      "coins_used": 1
    }
  ]
}
```

#### Test Subscription Status
```bash
# Get staff token first
curl -X POST https://yamenmod9.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "01511111111", "password": "reception123"}'

# Test customer list
curl -X GET https://yamenmod9.pythonanywhere.com/api/customers?branch_id=1 \
  -H "Authorization: Bearer YOUR_STAFF_TOKEN"
```

**Check Response:**
- Each customer should have `has_active_subscription: true/false`
- BMI values should be reasonable (18-35 range)
- Age values should be realistic

---

## 🧪 FLUTTER APP TESTING

### Test 1: Entry History (Client App)
1. Open client app
2. Login with: `01077827638` / `RX04AF`
3. Navigate to **Entry History**
4. Should see list of check-ins (if any exist)
5. Should NOT see type error

### Test 2: Subscription Status (Staff App)
1. Open staff app
2. Login as receptionist
3. Go to **Clients** screen
4. Customers with active subscriptions should show:
   - ✅ Green checkmark icon
   - "Active" badge
5. Customers without subscriptions should show:
   - ⚠️ Warning icon
   - "No Subscription" badge

### Test 3: Recent Customers (Staff Dashboard)
1. On reception dashboard
2. Check "Recent Customers" section
3. Verify:
   - BMI values are reasonable (20-35)
   - Age is accurate (based on birth year)
   - Time shows correctly (e.g., "2 days ago")

### Test 4: QR Code Status (Client App)
1. Open client app
2. Login with active subscription
3. Go to **QR Code** screen
4. Should show: **"Active"** status (green)
5. QR code should be scannable

---

## ⚠️ TROUBLESHOOTING

### Issue: Git pull fails
```bash
# Reset local changes
cd ~/gym-management-system
git reset --hard origin/main
git pull origin main
```

### Issue: Web app won't reload
- Wait 60 seconds and try again
- Check error log in PythonAnywhere console:
```bash
tail -n 50 ~/pythonanywhere.log
```

### Issue: Still seeing old data
- Clear browser cache
- Restart Flutter app completely
- Check that commit hash matches:
```bash
cd ~/gym-management-system
git log --oneline -1
# Should show: dfde872 Fix: Entry history, subscription status...
```

---

## 📞 VERIFICATION CHECKLIST

After deployment, verify these work:

- [ ] Entry history loads without JsonMap error
- [ ] Subscribed customers show green badge
- [ ] Unsubscribed customers show orange warning
- [ ] Recent customers display correct BMI
- [ ] Recent customers show accurate age
- [ ] Registration time displays correctly
- [ ] QR code shows "Active" for subscribed users
- [ ] QR code shows "Inactive" for unsubscribed users
- [ ] Check-in still works normally

---

## 🎯 NEXT STEPS (Flutter Only)

After backend deployment is verified, fix the Flutter display issues:

### Dynamic Subscription Display
**Files to update:**
- `lib/client/screens/client_overview_tab.dart`
- `lib/client/screens/subscription_screen.dart`

**Logic:**
```dart
// In overview tab - replace "Time Remaining" with dynamic display
if (subscription.subscriptionType == 'coins') {
  // Show: "25 Coins Remaining"
} else {
  // Show: "15 Days Remaining"
}

// In plan screen - adjust validity display
if (subscription.subscriptionType == 'coins') {
  // Show: "Validity: Unlimited" (for 30+ coins)
  // OR "Valid for 1 year" (for <30 coins)
} else {
  // Show: "Expires: March 15, 2026"
}
```

This is frontend-only and doesn't need backend deployment.

---

**END OF DEPLOYMENT GUIDE**

