@echo off
echo ============================================================
echo SamanSport Seasonality Dashboard - Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Checking for .env file...
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo ============================================================
    echo IMPORTANT: Edit .env file and add your Tharanis credentials
    echo ============================================================
    echo.
    notepad .env
)

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Next steps:
echo 1. Make sure .env file has your Tharanis credentials
echo 2. Run: venv\Scripts\activate
echo 3. Test API: python tharanis_client.py
echo 4. Launch dashboard: streamlit run app.py
echo.
pause
