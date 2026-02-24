@echo off
REM Backend Connection Test Script for Windows
REM Run this to test if the backend is working

echo ========================================
echo GYM APP BACKEND CONNECTION TEST
echo ========================================
echo.

set BASE_URL=https://yamenmod91.pythonanywhere.com

REM Test 1: Check if backend is accessible
echo Test 1: Checking backend accessibility...
echo URL: %BASE_URL%/api/auth/login
echo.

curl -s -o nul -w "HTTP Status: %%{http_code}" %BASE_URL%/api/auth/login
echo.
echo.

echo If you see "HTTP Status: 405" or "200", backend is accessible!
echo If you see other status or timeout, backend might be down.
echo.

echo ========================================
echo Test 2: Login Test
echo ========================================
echo.
set /p USERNAME="Enter username: "
set /p PASSWORD="Enter password: "
echo.

echo Attempting login...
curl -X POST %BASE_URL%/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"%USERNAME%\", \"password\": \"%PASSWORD%\"}" ^
  -w "\nHTTP Status: %%{http_code}\n"

echo.
echo.
echo Copy the token from above response if login successful
echo.
set /p TOKEN="Paste token here to test registration (or press Enter to skip): "

if "%TOKEN%"=="" (
    echo.
    echo Skipping registration test
    goto :end
)

echo.
echo ========================================
echo Test 3: Registration Test
echo ========================================
echo Testing customer registration...
echo.

curl -X POST %BASE_URL%/api/customers/register ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"full_name\": \"Test Customer\", \"age\": 25, \"weight\": 75.0, \"height\": 1.75, \"gender\": \"male\", \"phone\": \"01234567890\", \"email\": \"test@test.com\", \"branch_id\": 1, \"bmi\": 24.49, \"bmi_category\": \"Normal\", \"bmr\": 1750.0, \"daily_calories\": 2450.0}" ^
  -w "\nHTTP Status: %%{http_code}\n"

echo.
echo.

:end
echo ========================================
echo Test Complete
echo ========================================
echo.
echo Summary:
echo - Check the HTTP status codes above
echo - 200/201 = Success
echo - 401 = Unauthorized (check token)
echo - 400 = Bad Request (check data format)
echo - 500 = Server Error (backend issue)
echo.
echo If you need help, copy all the output above
echo.
pause
