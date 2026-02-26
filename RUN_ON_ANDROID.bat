@echo off
REM Run Flutter App on Android (NO CORS Issues!)

echo ================================================
echo   RUNNING GYM APP ON ANDROID EMULATOR
echo   (No CORS restrictions - works immediately!)
echo ================================================
echo.

echo [Step 1/3] Checking if emulator is running...
adb devices | find "emulator" >nul
if errorlevel 1 (
    echo Emulator not running. Starting Pixel 9 Pro...
    start /min flutter emulators --launch Pixel_9_Pro
    echo Waiting 20 seconds for emulator to start...
    timeout /t 20 /nobreak >nul
) else (
    echo Emulator already running!
)

echo.
echo [Step 2/3] Building and installing app...
echo This may take a minute on first run...
echo.

cd C:\Programming\Flutter\gym_frontend
flutter run -d emulator-5554 lib\main.dart

echo.
echo ================================================
echo   APP RUNNING ON ANDROID
echo   No CORS errors will occur!
echo   Backend connection works directly!
echo ================================================
pause

