@echo off
echo ================================================
echo SUBSCRIPTION ACTIVATION - LIVE TEST
echo ================================================
echo.
echo This will run your app on the Samsung device with
echo detailed logging so you can see exactly what happens
echo when you try to activate a subscription.
echo.
echo ================================================
echo STEPS:
echo ================================================
echo.
echo 1. Wait for app to launch on your phone
echo 2. Login with your credentials
echo 3. Go to Reception screen
echo 4. Click "Activate Subscription"
echo 5. Fill the form (use customer_id: 1, amount: 100)
echo 6. Click "Activate"
echo 7. Watch THIS console for the error details
echo.
echo ================================================
echo WHAT YOU'LL SEE IN CONSOLE:
echo ================================================
echo.
echo "=== ACTIVATING SUBSCRIPTION ==="
echo "Endpoint: /api/subscriptions/activate"
echo "Request Data: {...}"
echo.
echo Then you'll see:
echo "=== DIO EXCEPTION ==="
echo "Response Status: 404"
echo "Response Data: {"error":"Resource not found"}"
echo.
echo This confirms the backend endpoint doesn't exist!
echo.
echo ================================================
pause

echo.
echo Launching app on Samsung device...
echo.

flutter run -d adb-RKGYA00QEMD-K5pUFY._adb-tls-connect._tcp

echo.
echo ================================================
echo App closed
echo ================================================
pause

