@echo off
REM Gym Management System - Quick Start Script for Windows
REM This script sets up and runs the Flask backend

echo ============================================
echo  Gym Management System - Quick Start
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Checking Python installation...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo.
    echo [2/6] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo.
    echo [2/6] Virtual environment already exists, skipping...
)

REM Activate virtual environment
echo.
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade pip
echo.
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo.
echo [5/6] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Copy .env.example to .env if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env >nul
)

REM Initialize database if it doesn't exist
if not exist "instance\gym_management.db" (
    echo.
    echo [6/6] Initializing database...
    python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
    
    REM Seed database
    echo.
    echo Seeding database with test data...
    python seed.py
) else (
    echo.
    echo [6/6] Database already exists, skipping initialization...
    echo.
    set /p RESEED="Do you want to reseed the database? (This will delete all data) [y/N]: "
    if /i "%RESEED%"=="y" (
        echo Reseeding database...
        python seed.py
    )
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo Flask backend is ready to start!
echo.
echo Test Accounts:
echo   Owner:      username='owner'        password='owner123'
echo   Manager:    username='manager1'     password='manager123'
echo   Reception:  username='reception1'   password='reception123'
echo   Accountant: username='accountant1'  password='accountant123'
echo.
echo API Documentation: http://localhost:5000/test
echo.
echo ============================================
echo.

REM Start the Flask server
echo Starting Flask development server...
echo Press Ctrl+C to stop the server
echo.
python run.py

pause
