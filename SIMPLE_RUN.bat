@echo off
echo ========================================
echo   RUNNING GYM APP ON YOUR DEVICE
echo ========================================
echo.
echo Device: SM A566B (Samsung)
echo.
echo Building and installing...
echo.

cd /d "%~dp0"
flutter run -d adb-RKGYA00QEMD-K5pUFY._adb-tls-connect._tcp

pause

