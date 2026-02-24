# 🔧 Troubleshooting 401 Error

## Problem
Getting a 401 (Unauthorized) error when trying to login.

## What I've Fixed

### 1. Enhanced Error Handling
- ✅ Added detailed logging to API service
- ✅ Added logging to authentication service
- ✅ Updated API service to not throw on 401 during login
- ✅ Added better error messages for different failure scenarios

### 2. API Service Updates
- ✅ Changed `validateStatus` to allow responses < 500 (including 401)
- ✅ Added request/response logging
- ✅ Skip token injection for login endpoint
- ✅ Better error handling for DioException types

### 3. Debug Tools
- ✅ Created API Debug Tool (`ApiDebugger`)
- ✅ Created Debug Screen accessible from login
- ✅ Added backend connection test
- ✅ Added login test with detailed output

## How to Use the Debug Tool

### Step 1: Run the App
```bash
flutter run
```

### Step 2: Access Debug Tool
1. Launch the app
2. On the login screen, click **"API Debug Tool"** button
3. You'll see the debug interface

### Step 3: Test Backend Connection
1. Click **"Test Backend Connection"**
2. This will:
   - Test if backend is reachable
   - Try to find the correct login endpoint
   - Show what the backend expects

### Step 4: Test Login
1. Enter test username and password
2. Click **"Test Login"**
3. View detailed response including:
   - Status code
   - Response headers
   - Response body
   - Error messages

## Possible Causes of 401 Error

### 1. Wrong Endpoint
**Symptom:** Backend returns 401 or 404
**Solution:** The debug tool will test multiple endpoint variations:
- `/api/auth/login`
- `/api/login`
- `/auth/login`
- `/login`

### 2. Wrong Request Format
**Symptom:** Backend returns 401 with message about missing fields
**Solution:** Check the debug output to see what the backend expects

### 3. Invalid Credentials
**Symptom:** Backend returns 401 with "invalid username/password"
**Solution:** You need valid test credentials from the backend team

### 4. Backend Not Accessible
**Symptom:** Connection timeout or network error
**Solution:** Check:
- Internet connection
- Backend URL is correct
- Backend server is running

### 5. CORS Issues (Web only)
**Symptom:** Network error on web platform
**Solution:** Backend needs to allow CORS from your origin

## Expected Backend Response Format

The app expects one of these response formats:

**Success Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "owner",
  "user_id": 1,
  "username": "john_doe",
  "branch_id": 1
}
```

**Or:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "owner",
  "user_id": 1,
  "username": "john_doe",
  "branch_id": 1
}
```

**Error Response:**
```json
{
  "message": "Invalid username or password"
}
```

## What to Check in Debug Output

### 1. Connectivity Test
```
✅ Backend is reachable (Status: 200/404/etc.)
```
If this fails, backend is not accessible.

### 2. Endpoint Test
```
✅ Found endpoint: /api/auth/login (Status: 401)
Response: {"message": "Missing username"}
```
This confirms the endpoint exists.

### 3. Login Test
```
Status Code: 401
Response data: {"message": "Invalid credentials"}
```
This shows why login failed.

## Next Steps Based on Debug Output

### If Backend is Unreachable
1. Check URL: `https://yamenmod91.pythonanywhere.com`
2. Try accessing it in browser
3. Contact backend team

### If Endpoint is Wrong
1. Check debug output for correct endpoint
2. Update `lib/core/api/api_endpoints.dart`:
```dart
static const String login = '/correct/endpoint/here';
```

### If Request Format is Wrong
1. Check what backend expects in debug output
2. Update the login request in `auth_service.dart`

### If Credentials are Invalid
1. Get valid test credentials from backend team
2. Try login with those credentials

## Console Logs to Watch

When you try to login, you'll see detailed logs:
```
🔐 Attempting login...
URL: https://yamenmod91.pythonanywhere.com/api/auth/login
Username: test_user
📤 Request: POST https://yamenmod91.pythonanywhere.com/api/auth/login
📥 Response: 401 https://yamenmod91.pythonanywhere.com/api/auth/login
❌ Error: 401
❌ Error message: ...
❌ Error data: ...
```

## Quick Fix Checklist

- [ ] Backend is accessible at `https://yamenmod91.pythonanywhere.com`
- [ ] Login endpoint exists
- [ ] Request format matches backend expectations
- [ ] Valid test credentials obtained
- [ ] Used debug tool to verify all above
- [ ] Console logs reviewed
- [ ] Backend documentation checked

## Contact Backend Team

If none of the above helps, contact the backend team with:
1. Debug tool output
2. Console logs
3. Expected vs actual request format
4. Ask for:
   - Correct login endpoint
   - Required request format
   - Valid test credentials
   - API documentation

---

**Updated:** January 28, 2026
**Status:** Debug tools added, ready for testing
