@echo off
echo ================================================
echo SUBSCRIPTION ACTIVATION - ERROR DIAGNOSIS
echo ================================================
echo.
echo This will:
echo 1. Wait for emulator to be ready
echo 2. Run the app with verbose logging
echo 3. Show ALL error messages in console
echo.
echo INSTRUCTIONS:
echo 1. After app launches, login with your credentials
echo 2. Go to Reception screen
echo 3. Click "Activate Subscription"
echo 4. Fill the form (use customer_id: 1, amount: 100)
echo 5. Click "Activate" button
echo 6. Watch THIS console window for errors
echo.
pause

echo.
echo Waiting for emulator to be ready...
echo.

:CHECK_DEVICE
flutter devices | findstr /C:"emulator" >nul
if %errorlevel% neq 0 (
    echo Waiting for emulator... ^(will check again in 5 seconds^)
    timeout /t 5 >nul
    goto CHECK_DEVICE
)

echo.
echo ✓ Emulator is ready!
echo.
echo Starting app with verbose logging...
echo.
echo ================================================
echo WATCH FOR THESE MESSAGES:
echo ================================================
echo.
echo SUCCESS:
echo   =^> "Response Status: 200" or "Response Status: 201"
echo   =^> "Subscription activated successfully"
echo.
echo ERRORS TO LOOK FOR:
echo   =^> "DIO EXCEPTION"
echo   =^> "Response Status: 400" ^(validation error^)
echo   =^> "Response Status: 401" ^(not logged in^)
echo   =^> "Response Status: 404" ^(endpoint not found^)
echo   =^> "Response Status: 500" ^(backend error^)
echo   =^> "connectionError" ^(network issue^)
echo.
echo ================================================
echo APP LOGS START BELOW:
echo ================================================
echo.

flutter run -d emulator-5554 --verbose

echo.
echo ================================================
echo App closed or crashed
echo ================================================
pause

