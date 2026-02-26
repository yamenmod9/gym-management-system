@echo off
echo ================================================
echo TESTING BACKEND SUBSCRIPTION ENDPOINT
echo ================================================
echo.
echo Backend URL: https://yamenmod91.pythonanywhere.com
echo Endpoint: /api/subscriptions/activate
echo.
echo Testing if endpoint exists...
echo.

curl -X POST "https://yamenmod91.pythonanywhere.com/api/subscriptions/activate" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer test_token" ^
  -d "{\"customer_id\":1,\"service_id\":1,\"branch_id\":1,\"amount\":100,\"payment_method\":\"cash\"}" ^
  --verbose

echo.
echo ================================================
echo.
echo WHAT TO LOOK FOR:
echo.
echo ✅ HTTP 401 (Unauthorized) = Endpoint exists but needs valid token
echo ✅ HTTP 400 (Bad Request) = Endpoint exists but data invalid
echo ❌ HTTP 404 (Not Found) = Endpoint doesn't exist on backend
echo ❌ Connection refused = Backend server is down
echo.
pause

