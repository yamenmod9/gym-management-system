@echo off
REM Script to run both Client and Staff apps simultaneously

echo Starting Gym Client App...
start "Client App" cmd /k "flutter run --flavor client -t lib/client_main.dart --observatory-port=50001 --device-vmservice-port=50002"

echo Waiting 5 seconds before starting Staff App...
timeout /t 5 /nobreak >nul

echo Starting Gym Staff App...
start "Staff App" cmd /k "flutter run --flavor staff -t lib/main.dart --observatory-port=50003 --device-vmservice-port=50004"

echo.
echo Both apps are starting!
echo Client App will show as "Gym Client" on your device
echo Staff App will show as "Gym Staff" on your device
echo.
echo Press any key to close this window (apps will continue running)
pause >nul

