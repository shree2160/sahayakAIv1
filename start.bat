@echo off
REM ============================================
REM Sahayak AI - Quick Start Script for Windows
REM ============================================

echo.
echo  🙏 Sahayak AI - Voice Assistant for India
echo  ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python found

REM Navigate to backend
cd /d "%~dp0backend"

REM Check if venv exists
if not exist "venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
)

@REM REM Activate venv
@REM call venv\Scripts\activate

@REM REM Install dependencies
@REM echo.
@REM echo 📥 Installing dependencies...
@REM pip install -r requirements.txt --quiet

REM Check for .env file
if not exist ".env" (
    echo.
    echo ⚠️  No .env file found!
    echo    Creating from template...
    copy .env.example .env
    echo.
    echo 📝 Please edit backend\.env with your API keys:
    echo    - GEMINI_API_KEY (get from https://makersuite.google.com/app/apikey)
    echo    - SUPABASE_URL and SUPABASE_KEY (optional)
    echo.
    notepad .env
)

REM Check for VOSK model
if not exist "vosk_models\vosk-model-small-hi-0.22" (
    echo.
    echo ⚠️  VOSK Hindi model not found!
    echo    Please download manually:
    echo    1. Go to: https://alphacephei.com/vosk/models
    echo    2. Download: vosk-model-small-hi-0.22.zip
    echo    3. Extract to: backend\vosk_models\
    echo.
)

REM Start the server
echo.
echo 🚀 Starting Sahayak AI Backend...
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo.
echo    Press Ctrl+C to stop
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000
