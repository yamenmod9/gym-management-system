# QR CODE SCANNING - QUICK TEST GUIDE

## Date: February 15, 2026

## 🚀 Quick Start

### Prerequisites
- Flutter app installed on device
- Backend server running
- At least one customer account with credentials

---

## Test 1: Client QR Code Display ✅

### Steps:
1. Open **Client App**
2. Login with customer credentials:
   - Phone: `01077827638`
   - Password: (your customer password)
3. Navigate to **QR Code** tab/screen
4. Observe the QR code

### ✅ Expected Results:
- [ ] QR code displays (black on white background)
- [ ] QR code text shows format: `customer_id:123` or similar
- [ ] QR code is **NOT grey** (should be clear black)
- [ ] Status indicator shows subscription status
- [ ] If inactive, orange warning appears:
  > "QR code is valid, but you have no active subscription..."
- [ ] "Scannable: Yes" appears below QR code

### ❌ Failure Signs:
- QR code is grey/disabled
- QR code shows null/empty
- App crashes when opening QR screen

---

## Test 2: Staff QR Scanner ✅

### Steps:
1. Open **Staff App**
2. Login as Receptionist
3. Navigate to **QR Scanner**
4. Point camera at client's QR code from Test 1
5. Wait for scan to complete

### ✅ Expected Results:
- [ ] Scanner detects QR code automatically
- [ ] Loading dialog appears: "Loading customer..."
- [ ] Dialog closes after ~1-2 seconds
- [ ] Check-in dialog appears with:
  - Customer name (e.g., "Check-In: Mohamed Salem")
  - Customer ID
  - Subscription status (Active/Inactive)
  - If active: Shows remaining sessions/coins
  - Action buttons: "Check-In Only" or "Deduct 1 Session"

### ❌ Failure Signs:
- Scanner doesn't detect QR code
- Error: "Invalid QR code format"
- Error: "Customer not found"
- App crashes during scan

---

## Test 3: Multiple QR Code Formats ✅

### Test different QR code formats

Use a QR code generator (like qr-code-generator.com) to create test QR codes with these values:

| QR Code Value | Should Extract | Status |
|---------------|----------------|--------|
| `customer_id:115` | Customer ID: 115 | ✅ Should work |
| `GYM-115` | Customer ID: 115 | ✅ Should work |
| `GYM-2-115` | Customer ID: 115 | ✅ Should work |
| `CUST-115` | Customer ID: 115 | ✅ Should work |
| `115` | Customer ID: 115 | ✅ Should work |

### Steps:
1. Generate each QR code above
2. Display on screen/print
3. Scan with Staff App QR Scanner
4. Verify customer ID 115 is loaded each time

### ✅ Expected Results:
- [ ] All formats successfully scan
- [ ] All extract customer ID: 115
- [ ] Customer details load correctly
- [ ] No parsing errors

---

## Test 4: Subscription Status Display ⚠️

### Steps:
1. Login as client **WITH** active subscription
2. Go to QR Code screen
3. Check status indicator

### ✅ Expected Results (with backend fix):
- [ ] Status shows: "Active Subscription" (green)
- [ ] NO orange warning
- [ ] Subscription details visible

### ⚠️ Current Results (without backend fix):
- [ ] Status may show: "Inactive" (grey)
- [ ] Orange warning appears
- [ ] QR code still scannable

**Note:** This requires backend to include subscription status in login response. See `BACKEND_QR_CODE_AND_SUBSCRIPTION_FIX.md`.

---

## Debug Logging

### Enable Debug Output

When testing, watch the console/debug logs for these messages:

#### Client App (QR Code Display):
```
🔍 Loading QR Code: customer_id:115
🔍 ClientModel.fromJson - Raw JSON: {...}
🔑 Generated QR Code: customer_id:115
📊 Final subscription status: active
```

#### Staff App (QR Scanner):
```
📷 QR Code scanned: customer_id:115
👤 Extracted customer ID: 115
📋 Customer API Response: 200
📋 Customer API Data: {full_name: Mohamed Salem, ...}
✅ Customer loaded: Mohamed Salem
✅ Active subscription found: 45
```

### How to View Logs:
- **Android Studio:** Run → Logcat
- **VS Code:** Debug Console
- **Command Line:** `flutter logs`

---

## Common Issues & Solutions

### Issue 1: QR Code Shows Grey/Disabled ✅ FIXED
**Symptom:** QR code has grey background, can't scan  
**Solution:** Already fixed in `lib/client/screens/qr_screen.dart`  
**Verification:** QR code should be black on white

### Issue 2: Scanner Doesn't Detect QR Code ✅ FIXED
**Symptom:** Camera shows but never scans  
**Solution:** Improved QR format parsing in `qr_scanner_screen.dart`  
**Verification:** Scanner should detect in 1-2 seconds

### Issue 3: "Invalid QR code format" Error ✅ FIXED
**Symptom:** Scanner detects but shows error  
**Solution:** Now supports multiple formats (customer_id:X, GYM-X, etc)  
**Verification:** All formats in Test 3 should work

### Issue 4: Subscription Shows "Inactive" ⚠️ NEEDS BACKEND FIX
**Symptom:** Status is grey even with active subscription  
**Solution:** Backend must include subscription status in login response  
**See:** `BACKEND_QR_CODE_AND_SUBSCRIPTION_FIX.md`

### Issue 5: QR Code is Null/Empty ✅ PARTIALLY FIXED
**Symptom:** QR code doesn't display  
**Solution:**  
- Frontend now generates fallback: `customer_id:{id}`
- Backend should store QR codes properly
**Verification:** QR code always shows, even if backend returns null

---

## Success Checklist

After all tests, verify:

### Client App:
- [ ] Can login successfully
- [ ] QR code screen loads without errors
- [ ] QR code displays clearly (black on white)
- [ ] QR code has valid format: `customer_id:123`
- [ ] Can refresh QR code (button works)
- [ ] Status indicator shows (even if "inactive")

### Staff App:
- [ ] QR scanner opens successfully
- [ ] Camera permission granted
- [ ] Can scan QR codes from client app
- [ ] Customer details load after scan
- [ ] Check-in dialog appears
- [ ] Can perform check-in or session deduction

### End-to-End:
- [ ] Client generates QR → Staff scans → Customer identified
- [ ] Process takes < 5 seconds total
- [ ] No app crashes
- [ ] All actions work (check-in, deduct session)

---

## Test Data

### Sample Customer Credentials:
(From backend seed data)

| Phone | Password | Name | Expected ID |
|-------|----------|------|-------------|
| 01077827638 | RX04AF | Mohamed Salem | 1 |
| 01022981052 | SI19IC | Layla Rashad | 2 |
| 01041244663 | PS02HC | Ibrahim Hassan | 3 |

**Note:** Passwords shown are temporary passwords. Users may have changed them.

---

## Performance Metrics

### Target Performance:
- QR code display: < 1 second
- QR code scan: < 2 seconds
- Customer load after scan: < 3 seconds
- **Total check-in time: < 6 seconds**

### Measure:
1. Start timer when opening QR scanner
2. Stop timer when customer dialog appears
3. Should be under 5 seconds

---

## Reporting Issues

If tests fail, collect this information:

1. **Which test failed?** (Test 1, 2, 3, or 4)
2. **Error message** (exact text)
3. **Console/log output** (copy relevant lines)
4. **Device info** (Android/iOS, version)
5. **Screenshots** (if visual issue)

### Example Report:
```
Test: Test 2 - Staff QR Scanner
Error: "Customer not found (ID: 115)"
Logs:
  📷 QR Code scanned: customer_id:115
  👤 Extracted customer ID: 115
  📋 Customer API Response: 404
  ❌ Customer not found (ID: 115)
Device: Android 12, Samsung Galaxy A52
```

---

## Next Steps After Testing

### If All Tests Pass ✅:
1. Deploy to production
2. Train staff on QR scanning
3. Inform clients about QR code feature

### If Tests Fail ⚠️:
1. Check backend is running and accessible
2. Verify customer exists in database with ID
3. Check backend logs for API errors
4. Implement backend fixes from `BACKEND_QR_CODE_AND_SUBSCRIPTION_FIX.md`

---

## Summary

✅ **Fixed:** QR code display, scanning, format parsing  
⚠️ **Needs Backend:** Subscription status, QR code storage  
📄 **See Also:** 
- `FLUTTER_QR_CODE_FIX_SUMMARY.md` - Detailed changes
- `BACKEND_QR_CODE_AND_SUBSCRIPTION_FIX.md` - Backend requirements

**Estimated Test Time:** 10-15 minutes for all tests

---

**Good luck with testing! 🚀**

