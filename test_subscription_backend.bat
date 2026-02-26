@echo off
echo ================================================
echo SUBSCRIPTION ACTIVATION - BACKEND ENDPOINT TEST
echo ================================================
echo.
echo This script tests if the backend endpoint exists.
echo.
echo Backend URL: https://yamenmod91.pythonanywhere.com
echo Endpoint: /api/subscriptions/activate
echo.
echo ================================================
echo Testing endpoint...
echo ================================================
echo.

curl -X POST "https://yamenmod91.pythonanywhere.com/api/subscriptions/activate" ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":1,\"service_id\":1,\"branch_id\":1,\"amount\":100,\"payment_method\":\"cash\"}" ^
  -w "\n\nHTTP Status: %%{http_code}\n" ^
  -s

echo.
echo ================================================
echo WHAT THE STATUS CODES MEAN:
echo ================================================
echo.
echo ❌ 404 = Endpoint doesn't exist (CURRENT ISSUE)
echo ✅ 401 = Endpoint exists but needs authentication
echo ✅ 400 = Endpoint exists but data validation failed
echo ✅ 200/201 = SUCCESS! Endpoint working!
echo.
echo ================================================
echo.
echo If you see 404, the backend endpoint is not implemented yet.
echo If you see 401/400/200/201, the endpoint is ready!
echo.
pause

