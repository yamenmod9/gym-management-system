@echo off
echo ================================================
echo SUBSCRIPTION ACTIVATION TEST
echo ================================================
echo.
echo Target Device: Samsung SM A566B (Wireless)
echo.
echo This will:
echo 1. Build and install the app on your Samsung phone
echo 2. Show detailed logs to identify the error
echo.
echo AFTER APP OPENS:
echo 1. Login with your credentials
echo 2. Go to Reception screen
echo 3. Click "Activate Subscription"
echo 4. Fill the form (use customer_id: 1, amount: 100)
echo 5. Click "Activate" button
echo 6. Watch THIS CONSOLE for the error message
echo.
pause

echo.
echo Building and installing on Samsung...
echo.

flutter run -d adb-RKGYA00QEMD-K5pUFY._adb-tls-connect._tcp

pause

