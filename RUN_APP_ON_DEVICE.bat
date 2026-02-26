@echo off
echo =====================================
echo   RUNNING APP ON YOUR SAMSUNG DEVICE
echo =====================================
echo.
echo Device: SM A566B (Android 16)
echo.
echo Please wait while the app builds and installs...
echo This may take 1-2 minutes on first run.
echo.

cd /d "%~dp0"

flutter run -d adb-RKGYA00QEMD-K5pUFY._adb-tls-connect._tcp

pause

