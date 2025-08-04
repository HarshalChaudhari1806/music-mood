@echo off
echo.
echo ==========================================
echo    Music Mood Player - Windows Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found. Continuing setup...
echo.

REM Install dependencies
echo Installing Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    echo.
    pause
    exit /b 1
)

echo.
echo Running setup script...
python setup.py

echo.
echo Running system tests...
python test_system.py

echo.
echo ==========================================
echo           Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Add your music files to the mood folders in 'music' directory
echo 2. Run: start_app.bat
echo 3. Open your browser to: http://localhost:5000
echo.
echo Press any key to continue...
pause >nul
