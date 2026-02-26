@echo off
echo ============================================
echo    GYM APP LAUNCHER
echo ============================================
echo.
echo Which app do you want to run?
echo.
echo 1. Staff App (Reception/Manager/Accountant)
echo 2. Client App (Gym Members/Customers)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting Staff App...
    flutter run -t lib\main.dart
) else if "%choice%"=="2" (
    echo.
    echo Starting Client App...
    flutter run -t lib\client_main.dart
) else (
    echo.
    echo Invalid choice! Please run again and select 1 or 2.
    pause
)

