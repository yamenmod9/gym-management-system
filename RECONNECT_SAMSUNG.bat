@echo off
echo.
echo ========================================
echo   RECONNECT SAMSUNG DEVICE WIRELESSLY
echo ========================================
echo.
echo Before continuing, make sure:
echo 1. Your phone and PC are on the SAME WiFi network
echo 2. Wireless debugging is ENABLED on your phone
echo    (Settings -^> Developer Options -^> Wireless debugging)
echo.
echo.
set /p ip="Enter your phone's IP address (e.g., 192.168.1.100): "
echo.
echo Connecting to %ip%:5555...
adb connect %ip%:5555
echo.
echo.
echo Checking connected devices...
flutter devices
echo.
echo.
echo If your Samsung device appears above, you can now run:
echo    RUN_APP_NOW.bat
echo.
pause

