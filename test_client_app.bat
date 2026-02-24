@echo off
REM ========================================
REM CLIENT APP - QUICK TEST SCRIPT
REM ========================================

echo.
echo =====================================
echo   GYM CLIENT APP - QUICK TEST
echo =====================================
echo.

cd C:\Programming\Flutter\gym_frontend

echo [1/4] Checking Flutter...
flutter --version
if errorlevel 1 (
    echo ERROR: Flutter not found!
    pause
    exit /b 1
)

echo.
echo [2/4] Getting dependencies...
flutter pub get
if errorlevel 1 (
    echo ERROR: Dependencies failed!
    pause
    exit /b 1
)

echo.
echo [3/4] Analyzing code...
flutter analyze lib\client_main.dart
if errorlevel 1 (
    echo WARNING: Analysis found issues
)

echo.
echo [4/4] Checking available devices...
flutter devices

echo.
echo =====================================
echo   READY TO RUN!
echo =====================================
echo.
echo Choose your device:
echo   1. Web (Edge)
echo   2. Android
echo   3. Windows (requires Developer Mode)
echo   4. Cancel
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting on Edge...
    flutter run -d edge lib\client_main.dart
)

if "%choice%"=="2" (
    echo.
    echo Starting on Android...
    flutter run -d android lib\client_main.dart
)

if "%choice%"=="3" (
    echo.
    echo Starting on Windows...
    echo NOTE: Developer Mode must be enabled!
    flutter run -d windows lib\client_main.dart
)

if "%choice%"=="4" (
    echo Cancelled.
    exit /b 0
)

echo.
echo =====================================
echo   TEST CREDENTIALS
echo =====================================
echo   Phone: 01234567890
echo   Email: test@email.com
echo   Code: (from backend)
echo =====================================
echo.
pause

