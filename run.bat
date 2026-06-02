@echo off
setlocal enabledelayedexpansion

echo.
echo 🌲 Tree Lead Ranker
echo ====================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version
echo.

REM Create venv if needed
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Check .env
if not exist ".env" (
    echo.
    echo ⚠️  .env file not found!
    echo 📝 Creating .env from template...
    copy .env.example .env
    echo.
    echo 🔑 Please edit .env and add your API keys:
    echo    - GOOGLE_PLACES_API_KEY
    echo    - ANTHROPIC_API_KEY (or OPENAI_API_KEY)
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if keys are set
findstr /M "your_google_places_api_key_here" .env >nul
if %errorlevel% equ 0 (
    echo.
    echo ❌ API keys not configured!
    echo 📝 Edit .env and add:
    echo    - GOOGLE_PLACES_API_KEY
    echo    - ANTHROPIC_API_KEY (or OPENAI_API_KEY)
    pause
    exit /b 1
)

echo ✅ Configuration complete
echo.
echo 🚀 Starting server...
echo    API: http://localhost:8000
echo    Dashboard: http://localhost:8000/docs (or open dashboard.html)
echo.
echo Press Ctrl+C to stop
echo.

python main.py
pause
