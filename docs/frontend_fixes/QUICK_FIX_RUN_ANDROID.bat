@echo off
echo ================================================
echo   QUICK FIX: Run on Your Android Device
echo ================================================
echo.
echo This will run the app on your SM A566B device.
echo No CORS errors on Android!
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

cd C:\Programming\Flutter\gym_frontend
flutter run -d RKGYA00QEMD lib\main.dart

pause

