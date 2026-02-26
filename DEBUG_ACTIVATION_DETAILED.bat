@echo off
echo ================================================
echo SUBSCRIPTION ACTIVATION - DETAILED DEBUG
echo ================================================
echo.
echo This script will:
echo 1. Check backend connectivity
echo 2. Run app with detailed logging
echo 3. Help identify the exact error
echo.
pause

echo.
echo [STEP 1] Testing Backend Connection...
echo ================================================
echo.

curl -s -o nul -w "HTTP Status: %%{http_code}\n" "https://yamenmod91.pythonanywhere.com/api/auth/login"

if %errorlevel% equ 0 (
    echo ✅ Backend is reachable
) else (
    echo ❌ Cannot reach backend
    echo.
    echo PROBLEM: Network connection issue
    echo SOLUTION: Check your internet connection
    pause
    exit /b 1
)

echo.
echo [STEP 2] Checking Connected Devices...
echo ================================================
echo.

flutter devices

echo.
echo [STEP 3] Starting App with Debug Logs...
echo ================================================
echo.
echo WATCH FOR THESE PATTERNS:
echo.
echo 1. "=== ACTIVATING SUBSCRIPTION ===" - Activation started
echo 2. "Request Data: {...}" - Data being sent
echo 3. "Response Status: XXX" - HTTP response code
echo 4. "=== DIO EXCEPTION ===" - Error occurred
echo.
echo COMMON ERROR TYPES:
echo   • connectionError = CORS issue (use Android)
echo   • Response Status: 400 = Invalid data
echo   • Response Status: 401 = Not logged in
echo   • Response Status: 404 = Backend endpoint missing
echo   • Response Status: 500 = Backend error
echo.
echo ================================================
echo LOGS START BELOW:
echo ================================================
echo.

flutter run --verbose

pause

