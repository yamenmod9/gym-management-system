@echo off
echo ========================================
echo CLIENT SUBSCRIPTION FIX - TEST GUIDE
echo ========================================
echo.
echo This will run BOTH apps on your device so you can test:
echo 1. Client dashboard subscription display
echo 2. Reception dashboard active subscriptions count
echo.
echo ========================================
echo STEP 1: Test Client App
echo ========================================
echo.
echo Press any key to launch CLIENT app...
pause >nul

echo.
echo Launching CLIENT app...
flutter run -d SM_A566B --flavor client lib\client_main.dart

echo.
echo ========================================
echo CLIENT APP TEST CHECKLIST:
echo ========================================
echo [ ] 1. Login with client credentials
echo [ ] 2. Dashboard loads without errors
echo [ ] 3. Subscription details show correctly
echo [ ] 4. No "null is not a subtype" error
echo [ ] 5. Service name displays properly
echo.
echo If successful, close the app and continue to test staff app.
echo.
pause

echo.
echo ========================================
echo STEP 2: Test Staff App
echo ========================================
echo.
echo Press any key to launch STAFF app...
pause >nul

echo.
echo Launching STAFF app...
flutter run -d SM_A566B --flavor staff lib\main.dart

echo.
echo ========================================
echo STAFF APP TEST CHECKLIST:
echo ========================================
echo [ ] 1. Login as receptionist
echo [ ] 2. Dashboard shows actual active subscriptions count (not 0)
echo [ ] 3. Console shows: "Active subscriptions count loaded: X"
echo [ ] 4. Click "Activate Subscription"
echo [ ] 5. Fill form and submit
echo [ ] 6. Wait for success message
echo [ ] 7. Count should increase by 1
echo [ ] 8. Dashboard refreshes automatically
echo.
echo ========================================
echo SUCCESS INDICATORS:
echo ========================================
echo.
echo CLIENT APP:
echo   * No crash on dashboard
echo   * Subscription details visible
echo   * Dates and service name correct
echo.
echo STAFF APP:
echo   * Active subscriptions shows real number
echo   * After activation, count increases
echo   * Auto-refresh works
echo.
echo ========================================
echo.
pause

