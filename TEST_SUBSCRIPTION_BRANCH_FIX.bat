@echo off
echo ================================================================
echo SUBSCRIPTION ACTIVATION - BRANCH FIX TEST
echo ================================================================
echo.
echo ✅ FIX APPLIED: Subscription now uses customer's branch_id
echo.
echo WHAT WAS FIXED:
echo - Before: Used staff's branch_id (caused "Cannot create subscription for another branch" error)
echo - After: Fetches customer details and uses customer's branch_id
echo.
echo ================================================================
echo TEST STEPS:
echo ================================================================
echo.
echo 1. Login as: reception1 / reception123
echo 2. Tap: "Activate Subscription"
echo 3. Fill form:
echo    - Customer ID: 115 (Branch 2 customer)
echo    - Type: Coins Package
echo    - Coins: 20
echo    - Amount: 100
echo    - Payment: Cash
echo 4. Tap "Activate"
echo 5. Should see: "Subscription activated successfully" ✅
echo.
echo ================================================================
echo CONSOLE LOGS TO WATCH:
echo ================================================================
echo.
echo === FETCHING CUSTOMER DETAILS ===
echo Customer ID: 115
echo Customer branch_id: 2
echo Staff branch_id: 1
echo === ACTIVATING SUBSCRIPTION ===
echo Request Data: {...branch_id: 2...}  ✅ Correct!
echo Response Status: 200  ✅ Success!
echo.
echo ================================================================
pause
echo.
echo Starting app on Android device...
echo.
flutter run -d SM A566B

