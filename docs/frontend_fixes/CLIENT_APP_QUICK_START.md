# 🎯 CLIENT APP - QUICK START GUIDE

## 🚀 Run the Client App

```bash
# Make sure you're in the project directory
cd gym_frontend

# Run the CLIENT app (not the staff app)
flutter run lib/client_main.dart
```

## 📱 Test the App

### Step 1: Welcome Screen
1. App opens to welcome screen
2. Enter your phone or email (e.g., `01234567890` or `client@gym.com`)
3. Tap **"Request Activation Code"**
4. Should see: ✅ "Activation code sent! Check your phone/email."

### Step 2: Activation Screen
1. You'll be navigated to activation screen
2. Enter the 6-digit code (backend will send this)
3. Code auto-advances as you type
4. After 6th digit, auto-verifies
5. Should navigate to home dashboard

### Step 3: Home Dashboard
Check that you see:
- ✅ Welcome message with your name
- ✅ Subscription status card
- ✅ Remaining coins & days
- ✅ Quick action cards (QR, Subscription, History)

### Step 4: QR Code
1. Tap "My QR Code" card
2. Should see:
   - ✅ Large QR code
   - ✅ Status indicator (Active/Frozen/Stopped)
   - ✅ Countdown timer
   - ✅ Refresh button

### Step 5: Subscription
1. Go back, tap "Subscription" card
2. Should see:
   - ✅ Subscription type
   - ✅ Start & expiry dates
   - ✅ Days remaining
   - ✅ Remaining coins
   - ✅ Allowed services (chips)
   - ✅ Freeze history (if any)

### Step 6: Entry History
1. Go back, tap "Entry History" card
2. Should see:
   - ✅ List of gym visits
   - ✅ Date, time, branch
   - ✅ Service used
   - ✅ Coins consumed
   - ✅ Empty state if no entries

### Step 7: Logout
1. Tap logout icon in home screen
2. Should navigate back to welcome screen

## 🔧 If Backend Not Ready

The app will show error messages like:
- "Failed to request activation code"
- "Verification failed"
- "Failed to load data"

This is EXPECTED until backend endpoints are implemented.

## ✅ What to Check

### Visual
- [ ] Dark grey background (#1F1F1F)
- [ ] Red primary color (#DC143C)
- [ ] All text readable
- [ ] Icons are red
- [ ] Cards have elevation
- [ ] Buttons are red with white text

### Functionality
- [ ] Navigation between screens works
- [ ] Pull to refresh works (subscription & history)
- [ ] QR code countdown updates every second
- [ ] Loading indicators show during API calls
- [ ] Error messages are clear
- [ ] Logout clears data

### UX
- [ ] One-hand usage (all buttons reachable)
- [ ] Large tap targets
- [ ] Clear visual hierarchy
- [ ] Smooth animations
- [ ] No lag or jank

## 🐛 Common Issues

### "Resource not found" error
**Cause:** Backend endpoints not implemented yet
**Fix:** Implement backend endpoints (see COPY_TO_CLAUDE_SONNET.md)

### App crashes on startup
**Cause:** Missing dependencies
**Fix:** Run `flutter pub get`

### QR code not showing
**Cause:** Client data missing QR code field
**Fix:** Check API response has `qr_code` field

### Token expired error
**Cause:** Token expired and refresh failed
**Fix:** Logout and login again

## 📝 Test Credentials

Once backend is ready, test with:
- Phone: `01234567890`
- Email: `client@gym.com`
- Code: (backend will generate)

## 🎨 Design Check

The app should look like:

### Welcome Screen
```
┌─────────────────────────────┐
│      [Dumbbell Icon]        │
│                             │
│     Welcome to              │
│     Gym Client              │
│                             │
│ ┌─────────────────────────┐ │
│ │ Phone or Email          │ │
│ └─────────────────────────┘ │
│                             │
│ [Request Activation Code]   │
└─────────────────────────────┘
```

### Home Dashboard
```
┌─────────────────────────────┐
│ Dashboard          [Logout] │
├─────────────────────────────┤
│ Welcome back,               │
│ JOHN DOE                    │
│ 📍 Dragon Club              │
├─────────────────────────────┤
│ Subscription    [ACTIVE]    │
│ • Type: Gold                │
│ • Expires: 31/12/2026       │
│ • Coins: 50                 │
├─────────────────────────────┤
│ Quick Actions               │
│ ┌───────┐  ┌───────┐       │
│ │ QR    │  │ Sub   │       │
│ │ Code  │  │ scri. │       │
│ └───────┘  └───────┘       │
│ ┌─────────────────┐        │
│ │ Entry History   │        │
│ └─────────────────┘        │
└─────────────────────────────┘
```

### QR Code Screen
```
┌─────────────────────────────┐
│ My QR Code            [←]   │
├─────────────────────────────┤
│      [ACTIVE]               │
│                             │
│  ┌─────────────────────┐   │
│  │                     │   │
│  │   [Large QR Code]   │   │
│  │                     │   │
│  └─────────────────────┘   │
│                             │
│  GYM-CLIENT-001-ABC123      │
│                             │
│  ⏱️ Expires in: 59:32       │
│                             │
│  [Refresh QR Code]          │
└─────────────────────────────┘
```

## ✅ Ready to Test

When backend is ready:
1. Run the app
2. Go through all screens
3. Test all features
4. Check for errors
5. Report any issues

---

**Status:** ✅ App ready for backend integration

Once backend endpoints are implemented, test the full flow end-to-end.
