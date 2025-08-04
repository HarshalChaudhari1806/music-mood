@echo off
echo.
echo ==========================================
echo    Starting Music Mood Player...
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist app.py (
    echo ERROR: app.py not found
    echo Please make sure you're in the correct directory
    echo.
    pause
    exit /b 1
)

echo Starting the Music Mood Player...
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app.py

echo.
echo Application stopped.
pause
