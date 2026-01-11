#!/bin/bash
# ============================================
# Sahayak AI - Quick Start Script for Linux/Mac
# ============================================

echo ""
echo " 🙏 Sahayak AI - Voice Assistant for India"
echo " =========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found! Please install Python 3.10+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Navigate to backend
cd "$(dirname "$0")/backend" || exit

# Check if venv exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "   Creating from template..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit backend/.env with your API keys"
fi

# Check for VOSK model
if [ ! -d "vosk_models/vosk-model-small-hi-0.22" ]; then
    echo ""
    echo "📥 Downloading VOSK Hindi model..."
    mkdir -p vosk_models
    cd vosk_models
    curl -LO https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip
    unzip vosk-model-small-hi-0.22.zip
    rm vosk-model-small-hi-0.22.zip
    cd ..
fi

# Start the server
echo ""
echo "🚀 Starting Sahayak AI Backend..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
