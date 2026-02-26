@echo off
echo ====================================
echo  Running Gym App on Your Device
echo ====================================
echo.

cd /d "%~dp0"

echo [1/3] Cleaning previous build...
call flutter clean >nul 2>&1

echo [2/3] Building debug APK...
call flutter build apk --debug

if errorlevel 1 (
    echo.
    echo ❌ Build failed! Check the error above.
    pause
    exit /b 1
)

echo [3/3] Installing and running on device...
call flutter run -d adb-RKGYA00QEMD-K5pUFY._adb-tls-connect._tcp --debug

pause

