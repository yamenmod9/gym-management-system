# 🧪 CLIENT LOGIN TEST SCRIPT

## Quick Test Procedure

### 1. Stop and Restart the App

**In your terminal where the app is running:**
```bash
# Press Ctrl+C to stop the app
# Then restart:
flutter run -t lib/client_main.dart
```

### 2. Watch for Initialization Logs

You should see:
```
🔐 ClientAuthProvider: Initializing...
🔐 ClientAuthProvider: isAuthenticated = false
🔐 ClientAuthProvider: Initialization complete
🔀 Router Redirect: isAuth=false, passwordChanged=true, currentPath=/welcome
✅ No redirect needed - staying on /welcome
```

### 3. Enter Test Credentials

**Example credentials (use your actual customer data):**
- Phone: `01234567890` (or email if customer has one)
- Password: The password provided by reception

### 4. Click Login and Watch Console

**Expected Success Logs:**
```
🔐 WelcomeScreen: Starting login...
🔐 ClientAuthProvider: Starting login...
🔐 ClientAuthProvider: Current state - isAuth=false, passwordChanged=true
🔐 ClientAuthService: Login response received
🔐 Response keys: [success, data, message]
🔐 Has status field: false
🔐 Has success field: true
🔐 success value: true
🔐 isSuccess: true                              ← KEY: Must be TRUE
🔐 Token saved successfully
🔐 ClientAuthProvider: password_changed = true
🔐 ClientAuthProvider: Login successful! Client: [Customer Name]
🔐 ClientAuthProvider: New state - isAuth=true, passwordChanged=true
🔐 WelcomeScreen: Login completed, isAuth=true, passwordChanged=true
➡️ WelcomeScreen: User authenticated, going to home   ← NAVIGATION HAPPENS HERE
```

**What you'll see on screen:**
1. Green snackbar: "Login successful!"
2. Screen immediately transitions to dashboard (within 100ms)

---

## ❌ If Login Still Fails

### Check These Logs:

**1. If you see:**
```
🔐 isSuccess: false
❌ WelcomeScreen: Login error: Exception: [message]
```

**Problem:** Response validation still failing  
**Action:** Check what the actual response structure is in the logs

**2. If you see:**
```
🔐 isSuccess: true
🔐 Token saved successfully
[But no navigation happens]
```

**Problem:** Navigation issue (not auth issue)  
**Action:** Check router redirect logic

**3. If you see:**
```
Error: No element
```

**Problem:** Missing field in response (access_token or client data)  
**Action:** Backend response is incomplete

---

## 🔍 Get Actual Response Structure

If the fix doesn't work, run this curl command to see what the backend actually returns:

```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"01234567890","password":"YourPassword"}' \
  | python -m json.tool
```

**Expected output:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ...",
    "client": {
      "id": 151,
      "full_name": "Customer Name",
      "phone": "01234567890",
      ...
    },
    "password_changed": true
  }
}
```

---

## ✅ Success Criteria

**Login is working when you see:**

1. ✅ Console shows `isSuccess: true`
2. ✅ Token saved successfully
3. ✅ Green "Login successful" snackbar appears
4. ✅ Screen navigates to dashboard automatically
5. ✅ Dashboard shows customer name/data
6. ✅ No exception or error messages

---

## 📱 Test Different Scenarios

### Test Case 1: Regular Login (Password Already Changed)
- Use credentials with `password_changed: true`
- Expected: Direct navigation to dashboard

### Test Case 2: First-Time Login (Need Password Change)
- Use fresh credentials with `password_changed: false`
- Expected: Navigation to Change Password screen

### Test Case 3: Wrong Password
- Use correct phone, wrong password
- Expected: Red snackbar with error message, stay on login screen

### Test Case 4: Non-existent Customer
- Use phone/email not in database
- Expected: Red snackbar with "Customer not found", stay on login screen

---

## 🎯 Next Steps After Login Works

Once login is confirmed working:

1. Test QR code generation
2. Test subscription viewing
3. Test entry history
4. Test password change functionality
5. Then address reception dashboard customer list issue

---

**Last Updated:** February 13, 2026  
**Status:** Ready for Testing

