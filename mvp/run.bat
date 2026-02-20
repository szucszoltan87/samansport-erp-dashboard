@echo off
echo ============================================================
echo Launching SamanSport Seasonality Dashboard
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist venv\ (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found
    echo Please create .env file with your Tharanis credentials
    echo See .env.example for template
    pause
    exit /b 1
)

echo Starting Streamlit dashboard...
echo Dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py
