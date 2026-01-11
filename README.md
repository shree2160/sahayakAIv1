# 🙏 Sahayak AI - Voice-Enabled Local Assistant for India

A voice-first, location-aware AI assistant designed for Indian users to solve everyday problems like mobile recharge, government forms, finding nearby services, and understanding local procedures.

![Sahayak AI](https://img.shields.io/badge/Made%20with-❤️%20for%20India-orange)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🎤 **Voice Input** - Speak in Hindi or English
- 🤖 **AI-Powered** - Uses Gemini AI for intelligent responses
- 📍 **Location-Aware** - Find nearby hospitals, banks, offices
- 📋 **Process Guidance** - Step-by-step help for Aadhaar, PAN, etc.
- 🔊 **Voice Response** - Answers spoken back to you
- 💯 **100% Free** - Uses only free APIs and tools
- 🌐 **Offline STT** - VOSK for offline speech recognition

## 🏗️ Architecture

```
User (Browser)
  → Frontend (Voice UI)
  → FastAPI Backend
      → VOSK (Speech-to-Text, offline)
      → Gemini (AI Reasoning)
      → Supabase (Local knowledge)
      → OpenStreetMap (Nearby places)
      → eSpeak NG (Text-to-Speech)
  → Audio + Text response
```

## 📁 Project Structure

```
sahayak-ai/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration & env vars
│   ├── schemas.py           # Pydantic models
│   ├── speech_to_text.py    # VOSK STT module
│   ├── text_to_speech.py    # eSpeak TTS module
│   ├── reasoning.py         # Gemini AI integration
│   ├── osm_service.py       # OpenStreetMap service
│   ├── supabase_client.py   # Database client
│   ├── location_service.py  # Location utilities
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
│
├── frontend/
│   ├── index.html           # Main UI
│   ├── style.css            # Styling
│   ├── app.js               # Application logic
│   └── recorder.js          # Audio recording
│
├── supabase_setup.sql       # Database schema
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+**
2. **Node.js** (optional, for frontend dev server)
3. **FFmpeg** (for audio conversion)
4. **eSpeak NG** (for text-to-speech)

### 1. Clone & Setup Backend

```bash
# Clone repository
git clone https://github.com/yourusername/sahayak-ai.git
cd sahayak-ai/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Free API Keys

#### Gemini AI (Required)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

#### Supabase (Optional but recommended)
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy the URL and `anon` key

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your keys
notepad .env  # Windows
# nano .env   # Linux
```

Add your keys:
```
GEMINI_API_KEY=your_gemini_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
```

### 4. Download VOSK Hindi Model

```bash
# Create models directory
mkdir vosk_models
cd vosk_models

# Download Hindi model (small version ~50MB)
# Option 1: Direct download
curl -LO https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip
unzip vosk-model-small-hi-0.22.zip

# Option 2: PowerShell
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip" -OutFile "vosk-model-small-hi-0.22.zip"
Expand-Archive -Path "vosk-model-small-hi-0.22.zip" -DestinationPath "."
```

### 5. Install System Dependencies

#### Windows
```powershell
# Install FFmpeg (using Chocolatey)
choco install ffmpeg

# Install eSpeak NG
# Download from: https://github.com/espeak-ng/espeak-ng/releases
# Run the installer
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg espeak-ng
```

#### macOS
```bash
brew install ffmpeg espeak-ng
```

### 6. Run the Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 7. Run the Frontend

Option A: Simple HTTP Server
```bash
cd frontend
python -m http.server 3000
```

Option B: VS Code Live Server
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

Open `http://localhost:3000` in your browser.

## 🗄️ Database Setup (Supabase)

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the contents of `supabase_setup.sql`

This creates the `local_knowledge` table with sample data.

## 🌐 Free Deployment

### Backend (Render)

1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create new "Web Service"
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`
6. Deploy!

### Frontend (Vercel)

1. Create account at [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Select `frontend` folder as root
4. Deploy!

Update `frontend/app.js` with your Render URL:
```javascript
API_BASE_URL: 'https://your-app.onrender.com'
```

## 🎮 Usage Examples

### Voice Commands (Hindi)
- "मोबाइल रिचार्ज कैसे करें?"
- "नजदीकी अस्पताल कहां है?"
- "आधार कार्ड अपडेट कैसे करें?"
- "पैन कार्ड कैसे बनवाएं?"
- "पासपोर्ट के लिए क्या डॉक्यूमेंट चाहिए?"

### Text Commands (English/Hinglish)
- "How to recharge mobile?"
- "Where is nearest bank?"
- "Driving license kaise banaye?"

## 🔧 API Endpoints

### POST /ask
Main endpoint for queries.

**Request:**
```json
{
  "audio_base64": "optional base64 audio",
  "text_query": "your question",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "language": "hi"
}
```

**Response:**
```json
{
  "success": true,
  "text_response": "Detailed answer...",
  "audio_base64": "base64 audio response",
  "transcribed_text": "what user said",
  "detected_intent": "mobile_recharge",
  "nearby_places": [...]
}
```

### GET /health
Check service status.

## 🐛 Troubleshooting

### VOSK not loading
- Ensure model is extracted to `backend/vosk_models/vosk-model-small-hi-0.22/`
- Check model name in `.env` matches folder name

### eSpeak not found
- Verify installation: `espeak-ng --version`
- Add to PATH if needed

### FFmpeg errors
- Install FFmpeg and add to PATH
- Verify: `ffmpeg -version`

### CORS errors
- Check `ALLOWED_ORIGINS` in `config.py`
- Ensure frontend URL is listed

## 📝 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 🙏 Acknowledgments

- [VOSK](https://alphacephei.com/vosk/) - Offline speech recognition
- [eSpeak NG](https://github.com/espeak-ng/espeak-ng) - Text-to-speech
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI reasoning
- [OpenStreetMap](https://www.openstreetmap.org/) - Map data
- [Supabase](https://supabase.com) - Database

---

**Made with ❤️ for India**
