@echo off
REM Quick Fix for Connection Error

echo ============================================
echo   FIXING CONNECTION ERROR - QUICK FIX
echo ============================================
echo.

echo This will:
echo 1. Clean the Flutter project
echo 2. Run on Windows Desktop (no CORS issues)
echo.

set /p confirm="Continue? (Y/N): "
if /i "%confirm%" neq "Y" exit /b

echo.
echo [1/2] Cleaning project...
flutter clean

echo.
echo [2/2] Running on Windows Desktop...
echo.
echo NOTE: Desktop app doesn't have CORS issues!
echo       It will connect directly to the backend.
echo.

flutter run -d windows lib\main.dart

pause

