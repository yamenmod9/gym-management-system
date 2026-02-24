@echo off
echo ================================================================
echo CHECK-IN AND SUBSCRIPTION STATUS - FIX VERIFICATION
echo ================================================================
echo.
echo CHANGES APPLIED (Flutter App):
echo ✅ Check-in requests now include branch_id
echo ✅ Deduct session attendance includes branch_id
echo ✅ No compilation errors
echo.
echo ================================================================
echo TEST 1: CHECK-IN WITH BRANCH_ID
echo ================================================================
echo.
echo STEPS:
echo 1. Login as: reception1 / reception123
echo 2. Tap "Scan QR" button (floating action button)
echo 3. Scan customer QR code (customer ID: 115)
echo 4. Tap "Check-In Only"
echo.
echo EXPECTED RESULT:
echo ✅ Success message: "Adel Saad checked in successfully!"
echo ✅ No error about "branch_id is required"
echo ✅ Console shows: branch_id: 1 in request
echo.
echo CONSOLE LOGS TO WATCH:
echo   I/flutter: ✅ Recording check-in for customer: 115
echo   I/flutter: 📋 Check-in Response: 200
echo   I/flutter: 📋 Check-in Data: {success: true, ...}
echo.
echo ================================================================
echo TEST 2: CUSTOMER SUBSCRIPTION STATUS (Needs Backend Fix)
echo ================================================================
echo.
echo STEPS:
echo 1. Login as receptionist
echo 2. Tap hamburger menu → "All Customers"
echo 3. Find customer: Adel Saad (ID: 115)
echo.
echo CURRENT RESULT (Before Backend Fix):
echo ❌ Shows "No Subscription" (orange badge)
echo ❌ Warning icon displayed
echo.
echo EXPECTED RESULT (After Backend Fix):
echo ✅ Shows "Active" (green badge)
echo ✅ Checkmark icon displayed
echo.
echo BACKEND FIX REQUIRED:
echo → Add "has_active_subscription": true/false to customer list API
echo → See BACKEND_FIX_CHECKIN_AND_SUBSCRIPTION_STATUS.md
echo.
echo ================================================================
echo TEST 3: DEDUCT SESSION
echo ================================================================
echo.
echo STEPS:
echo 1. Scan QR code of customer with active subscription
echo 2. Tap "Deduct 1 Session"
echo.
echo EXPECTED RESULT:
echo ✅ "Session deducted successfully! Remaining: X"
echo ✅ Attendance record created with branch_id
echo.
echo CONSOLE LOGS TO WATCH:
echo   I/flutter: 🎯 Deducting session for customer: 115
echo   I/flutter: 📋 Deduct Response: 200
echo   I/flutter: Session deducted successfully!
echo.
echo ================================================================
echo IMPORTANT NOTES:
echo ================================================================
echo.
echo 1. Test 1 (Check-In) should work if backend accepts branch_id ✅
echo 2. Test 2 (Subscription Status) requires backend changes ⚠️
echo 3. Test 3 (Deduct Session) should work if backend accepts branch_id ✅
echo.
echo BACKEND REFERENCE:
echo → BACKEND_FIX_CHECKIN_AND_SUBSCRIPTION_STATUS.md
echo.
echo ================================================================
pause

