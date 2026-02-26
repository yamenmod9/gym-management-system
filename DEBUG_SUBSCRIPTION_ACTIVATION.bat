@echo off
REM Debug Subscription Activation Issues

echo ================================================
echo   SUBSCRIPTION ACTIVATION - DEBUG TOOL
echo ================================================
echo.

echo This tool will help diagnose subscription activation issues.
echo.
echo COMMON ISSUES:
echo 1. CORS Error (Web) - Run on Android instead
echo 2. Connection Error - Check backend server
echo 3. Invalid Data - Check form inputs
echo 4. Backend Error - Check backend logs
echo.

:menu
echo ------------------------------------------------
echo SELECT DEBUG ACTION:
echo ------------------------------------------------
echo 1. Run app on Android Device (Your SM A566B)
echo 2. Run app on Emulator (No CORS)
echo 3. Test Backend API Connection
echo 4. View Flutter Logs (Real-time)
echo 5. Clean Build and Restart
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto android_device
if "%choice%"=="2" goto android_emulator
if "%choice%"=="3" goto test_backend
if "%choice%"=="4" goto view_logs
if "%choice%"=="5" goto clean_build
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
goto menu

:android_device
echo.
echo [Running on your Android Device: SM A566B]
echo This will run on your wirelessly connected device.
echo.
flutter run -d RKGYA00QEMD lib\main.dart
goto menu

:android_emulator
echo.
echo [Starting Android Emulator]
echo.
adb devices | find "emulator" >nul
if errorlevel 1 (
    echo Starting Pixel 9 Pro emulator...
    start /min flutter emulators --launch Pixel_9_Pro
    echo Waiting 20 seconds for emulator to boot...
    timeout /t 20 /nobreak >nul
)
echo.
echo [Running app on emulator]
flutter run -d emulator-5554 lib\main.dart
goto menu

:test_backend
echo.
echo [Testing Backend API Connection]
echo Backend URL: https://yamenmod91.pythonanywhere.com
echo.
echo Testing /api/auth/login endpoint...
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"test\"}" -w "\nHTTP Status: %%{http_code}\n"
echo.
echo Testing /api/subscriptions/activate endpoint (requires auth)...
echo Note: This will fail without valid JWT token, but shows if endpoint is reachable
curl -X POST https://yamenmod91.pythonanywhere.com/api/subscriptions/activate -H "Content-Type: application/json" -w "\nHTTP Status: %%{http_code}\n"
echo.
pause
goto menu

:view_logs
echo.
echo [Starting Flutter with Verbose Logging]
echo This will show detailed error messages.
echo Press Ctrl+C to stop.
echo.
flutter run -d edge --verbose
goto menu

:clean_build
echo.
echo [Cleaning and Rebuilding]
echo This will clear cache and rebuild the app.
echo.
flutter clean
flutter pub get
echo.
echo Clean complete! Now select option 1 or 2 to run the app.
echo.
pause
goto menu

:end
echo.
echo Exiting debug tool...
exit

