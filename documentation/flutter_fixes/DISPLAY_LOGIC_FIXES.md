# 📱 FLUTTER DISPLAY FIXES - Not Urgent

## 🎯 Remaining Issues (Frontend Only)

These are **display logic** issues in Flutter - NO backend changes needed.

### Issue 1: Time Remaining Container for Coins
**Location:** Client Dashboard  
**Problem:** Shows "Time Remaining" even for coins subscriptions  
**File:** `lib/client/screens/client_overview_tab.dart`

**Fix:**
```dart
// Around line 80-100, replace static "Time Remaining" with:
if (subscription.subscriptionType == 'coins') {
  Text('${subscription.remainingCoins ?? 0} Coins Remaining');
} else {
  Text('${_calculateDaysRemaining(subscription.endDate)} Days Remaining');
}
```

---

### Issue 2: Plan Screen Static Info
**Location:** Client Plan Screen  
**Problem:** Shows start/end dates for ALL subscriptions  
**File:** `lib/client/screens/subscription_screen.dart`

**Fix:**
```dart
// Around line 150-200, wrap date fields with:
if (subscription.subscriptionType != 'coins') {
  // Show start date, end date, time remaining
  Row(
    children: [
      Icon(Icons.calendar_today),
      Text('Start: ${subscription.startDate}'),
    ],
  ),
  Row(
    children: [
      Icon(Icons.event),
      Text('Expires: ${subscription.endDate}'),
    ],
  ),
} else {
  // For coins, show validity instead
  Row(
    children: [
      Icon(Icons.all_inclusive),
      Text('Validity: ${subscription.coins >= 30 ? "Unlimited" : "1 Year"}'),
    ],
  ),
}
```

---

## 🔍 How to Find the Code

### client_overview_tab.dart
1. Search for: `"Time Remaining"`
2. Replace with conditional based on `subscriptionType`

### subscription_screen.dart  
1. Search for: `"Start Date"` or `"Expires"`
2. Wrap with `if (subscriptionType != 'coins')`
3. Add coins validity display

---

## 📊 Testing After Fix

### Test Coins Subscription:
1. Customer has 50 coins
2. Dashboard shows: "50 Coins Remaining"
3. Plan screen shows: "Validity: Unlimited"
4. NO start/end dates displayed

### Test Time-Based Subscription:
1. Customer has 3-month subscription
2. Dashboard shows: "75 Days Remaining" (or actual days)
3. Plan screen shows: "Expires: May 15, 2026"
4. Start date, end date visible

---

## 📝 Notes

- These are **cosmetic fixes** - not urgent
- Backend already returns correct data
- Just need to **display** it properly
- No API changes needed
- No PythonAnywhere deployment needed

---

**Priority:** Low - Backend fixes are more critical!

