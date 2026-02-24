@echo off
REM Test Backend Connection Script
REM This will test if the backend API is accessible

echo ============================================
echo   TESTING BACKEND CONNECTION
echo ============================================
echo.

echo Testing backend URL: https://yamenmod91.pythonanywhere.com/api
echo.

REM Test 1: Ping the server
echo [1/3] Testing server connection...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" https://yamenmod91.pythonanywhere.com/api 2>nul
if errorlevel 1 (
    echo ERROR: Cannot reach server
    echo.
    echo This could mean:
    echo   1. No internet connection
    echo   2. Backend server is down
    echo   3. URL is incorrect
    echo.
) else (
    echo SUCCESS: Server is reachable
    echo.
)

REM Test 2: Test login endpoint
echo [2/3] Testing login endpoint...
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"test\",\"password\":\"test\"}" ^
  -s -o nul -w "HTTP Status: %%{http_code}\n"
echo.

REM Test 3: Test services endpoint
echo [3/3] Testing services endpoint...
curl -X GET https://yamenmod91.pythonanywhere.com/api/services ^
  -H "Content-Type: application/json" ^
  -s -o nul -w "HTTP Status: %%{http_code}\n"
echo.

echo ============================================
echo   COMMON SOLUTIONS
echo ============================================
echo.
echo If you see connection errors:
echo.
echo 1. CHECK INTERNET CONNECTION
echo    - Make sure you're connected to the internet
echo.
echo 2. CHECK BACKEND STATUS
echo    - Visit: https://yamenmod91.pythonanywhere.com
echo    - If it shows an error, the backend is down
echo.
echo 3. CORS ISSUE (Most likely)
echo    - The backend needs to allow requests from Flutter web
echo    - Backend must have CORS headers configured
echo.
echo 4. USE CHROME WITH CORS DISABLED (Development only)
echo    - Close all Chrome instances
echo    - Run: chrome.exe --disable-web-security --user-data-dir="C:\temp\chrome_dev"
echo    - Then run your Flutter app
echo.
echo 5. RUN ON MOBILE/DESKTOP INSTEAD OF WEB
echo    - flutter run -d windows lib\main.dart
echo    - flutter run -d android lib\main.dart
echo    (Web has CORS restrictions, desktop/mobile don't)
echo.
echo ============================================

pause

