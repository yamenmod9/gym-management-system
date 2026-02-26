@echo off
echo.
echo ========================================
echo   TEST SUBSCRIPTION ACTIVATION
echo   COMPLETE SOLUTION
echo ========================================
echo.
echo Step 1: Choose your option
echo.
echo [1] Launch Emulator (Pixel 9 Pro)
echo [2] Reconnect Samsung Device
echo [3] Run App (device/emulator must be ready)
echo [4] Show Instructions
echo [5] Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto launch_emulator
if "%choice%"=="2" goto reconnect_samsung
if "%choice%"=="3" goto run_app
if "%choice%"=="4" goto show_instructions
if "%choice%"=="5" goto end

:launch_emulator
echo.
echo Launching emulator...
call LAUNCH_EMULATOR.bat
goto end

:reconnect_samsung
echo.
echo Reconnecting Samsung device...
call RECONNECT_SAMSUNG.bat
goto end

:run_app
echo.
echo Running app...
call RUN_APP_NOW.bat
goto end

:show_instructions
echo.
echo ========================================
echo   HOW TO TEST SUBSCRIPTION ACTIVATION
echo ========================================
echo.
echo 1. PREPARE DEVICE:
echo    - Option A: Launch emulator (takes 30 seconds)
echo    - Option B: Reconnect your Samsung phone
echo.
echo 2. RUN THE APP:
echo    - Choose option 3 from this menu
echo    - Wait for app to build and install
echo.
echo 3. LOGIN:
echo    - Enter your username and password
echo    - Click Login
echo.
echo 4. TEST SUBSCRIPTION:
echo    - Go to Reception screen (bottom nav)
echo    - Click "Activate Subscription"
echo    - Fill the form:
echo      * Customer ID: 151
echo      * Subscription Type: Coins Package
echo      * Coins Amount: 20
echo      * Amount: 100
echo      * Payment Method: cash
echo    - Click "ACTIVATE"
echo.
echo 5. CHECK RESULT:
echo    - Green message = SUCCESS!
echo    - Error dialog = Read the error message
echo.
echo Press any key to return to menu...
pause >nul
cls
goto start

:end
echo.
echo Done!
echo.

