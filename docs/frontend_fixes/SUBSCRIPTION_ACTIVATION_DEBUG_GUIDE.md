# 🔍 Subscription Activation Error - Debug Guide

**Date:** February 10, 2026  
**Issue:** "Failed to activate subscription" error  
**Status:** ✅ READY TO DEBUG

---

## 🎯 QUICK DIAGNOSIS

The error "Failed to activate subscription" can have multiple causes. Let's identify yours:

### Step 1: Run Debug Script

**Double-click:** `DEBUG_ACTIVATION_DETAILED.bat`

This will:
1. ✅ Check if backend is reachable
2. ✅ Show connected devices
3. ✅ Run app with detailed logging

---

## 🔍 WHAT TO LOOK FOR

After the app starts, **login and try to activate a subscription**. Then look at the console output:

### ✅ SUCCESS PATTERN:
```
=== ACTIVATING SUBSCRIPTION ===
Endpoint: /api/subscriptions/activate
Request Data: {customer_id: 1, service_id: 1, ...}
Response Status: 200
Response Data: {"status": "success", ...}
✅ Subscription activated successfully
```

### ❌ ERROR PATTERNS:

#### Error Type 1: CORS/Connection Error
```
=== DIO EXCEPTION ===
Type: DioExceptionType.connectionError
```
**Cause:** Running on web browser  
**Solution:** Run on Android device or emulator (see below)

---

#### Error Type 2: Backend Endpoint Not Found (404)
```
=== DIO EXCEPTION ===
Response Status: 404
```
**Cause:** Backend doesn't have `/api/subscriptions/activate` endpoint  
**Solution:** Backend needs to implement this endpoint

---

#### Error Type 3: Authentication Error (401)
```
=== DIO EXCEPTION ===
Response Status: 401
```
**Cause:** Token expired or invalid  
**Solution:** Logout and login again

---

#### Error Type 4: Validation Error (400/422)
```
=== DIO EXCEPTION ===
Response Status: 400
Response Data: {"message": "Invalid data", ...}
```
**Cause:** Missing or invalid form data  
**Solution:** Check all required fields are filled correctly

---

#### Error Type 5: Backend Server Error (500)
```
=== DIO EXCEPTION ===
Response Status: 500
Response Data: {"message": "Internal server error", ...}
```
**Cause:** Backend code crashed  
**Solution:** Check backend logs for the actual error

---

## 🚀 SOLUTIONS

### Solution 1: If CORS Error (connectionError)

**Problem:** Web browser blocks cross-origin requests

**Fix:** Run on Android instead

1. **Connect device or start emulator:**
   ```
   flutter devices
   ```

2. **Run on Android:**
   - Double-click: `RUN_APP_NOW.bat`
   - OR manually: `flutter run -d [device-id]`

---

### Solution 2: If 404 Error

**Problem:** Backend endpoint doesn't exist

**Fix:** Test backend endpoint directly:

1. **Double-click:** `TEST_BACKEND_ENDPOINT.bat`

2. **Look for HTTP status:**
   - ✅ `401` = Endpoint exists (just needs auth)
   - ✅ `400` = Endpoint exists (just needs valid data)
   - ❌ `404` = Endpoint doesn't exist → Contact backend developer

---

### Solution 3: If 401 Error

**Problem:** Authentication token expired

**Fix:** Simply logout and login again

---

### Solution 4: If 400/422 Error

**Problem:** Invalid data sent to backend

**Fix:** Check the form fields:
- Customer ID must be valid (existing customer)
- Amount must be a number
- Service ID must be valid
- All required fields filled

---

### Solution 5: If 500 Error

**Problem:** Backend server crashed

**Fix:** This is a backend issue. Check backend logs:
```bash
# On pythonanywhere
cat /var/log/yamenmod91.pythonanywhere.com.error.log
```

---

## 📊 TEST BACKEND DIRECTLY

Want to test if the backend endpoint works?

**Double-click:** `TEST_BACKEND_ENDPOINT.bat`

This sends a test request directly to the backend to verify:
- ✅ Backend is online
- ✅ Endpoint exists
- ✅ Backend can receive requests

---

## 🎯 MOST LIKELY CAUSES

Based on your setup, the most likely causes are:

1. **CORS Error (if running on Edge/Chrome)**
   - **Symptom:** `connectionError` in logs
   - **Fix:** Use Android device/emulator

2. **Backend Endpoint Missing**
   - **Symptom:** `404` error
   - **Fix:** Backend needs to implement the endpoint

3. **Invalid Customer ID**
   - **Symptom:** `400` error with message about customer
   - **Fix:** Use a valid customer ID (e.g., 1, 2, 3...)

---

## 📝 WHAT TO DO NEXT

1. **Run the debug script:**
   ```
   Double-click: DEBUG_ACTIVATION_DETAILED.bat
   ```

2. **Try to activate a subscription:**
   - Login
   - Go to Reception screen
   - Click "Activate Subscription"
   - Fill the form
   - Click "Activate"

3. **Look at the console output and match it to the error patterns above**

4. **Report back with:**
   - The error pattern you saw (e.g., "connectionError", "404", "500")
   - The full console output from "=== ACTIVATING SUBSCRIPTION ===" to the error

---

## 🆘 STILL STUCK?

**Share this information:**
1. What device/platform are you running on? (Edge browser? Android phone? Emulator?)
2. What error pattern did you see in the console?
3. Copy the console output from "=== ACTIVATING SUBSCRIPTION ===" onwards

---

## 📁 AVAILABLE TOOLS

- `DEBUG_ACTIVATION_DETAILED.bat` - Full debug with logs
- `TEST_BACKEND_ENDPOINT.bat` - Test backend directly
- `RUN_APP_NOW.bat` - Quick run on connected device

---

**Status:** ✅ Ready to debug  
**Next:** Run `DEBUG_ACTIVATION_DETAILED.bat`

---

