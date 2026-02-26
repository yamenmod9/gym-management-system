@echo off
echo ========================================
echo TESTING CLIENT APP LOGIN ENDPOINT
echo ========================================
echo.

echo Testing client login endpoint...
echo Endpoint: POST /api/client/auth/login
echo.

curl -X POST https://yamenmod91.pythonanywhere.com/api/client/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"phone\":\"01234567890\",\"password\":\"ABC123\"}"

echo.
echo.
echo ========================================
echo If you see 404: Backend endpoint not implemented yet
echo If you see 401: Invalid credentials (backend is working)
echo If you see 200: Login successful!
echo ========================================
echo.
pause

