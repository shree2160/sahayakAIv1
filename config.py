"""
Sahayak AI - Configuration Module
=================================
Central configuration management for the application.
Uses environment variables for sensitive data.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# BASE PATHS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio_files"
VOSK_MODEL_DIR = BASE_DIR / "vosk_models"

# Create directories if they don't exist
AUDIO_DIR.mkdir(exist_ok=True)
VOSK_MODEL_DIR.mkdir(exist_ok=True)

# =============================================================================
# API KEYS & EXTERNAL SERVICES
# =============================================================================

# Gemini AI Configuration (Free tier)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Supabase Configuration (Free tier)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# =============================================================================
# VOSK SPEECH-TO-TEXT CONFIGURATION
# =============================================================================

# Hindi model for VOSK (download from https://alphacephei.com/vosk/models)
# Recommended: vosk-model-small-hi-0.22 (lightweight) or vosk-model-hi-0.22 (full)
VOSK_MODEL_NAME = os.getenv("VOSK_MODEL_NAME", "vosk-model-small-hi-0.22")
VOSK_MODEL_PATH = VOSK_MODEL_DIR / VOSK_MODEL_NAME

# Supported audio sample rate for VOSK
VOSK_SAMPLE_RATE = 16000

# =============================================================================
# eSpeak NG TEXT-TO-SPEECH CONFIGURATION
# =============================================================================

# Hindi voice for eSpeak NG
ESPEAK_VOICE = os.getenv("ESPEAK_VOICE", "hi")  # Hindi
ESPEAK_SPEED = int(os.getenv("ESPEAK_SPEED", "130"))  # Words per minute
ESPEAK_PITCH = int(os.getenv("ESPEAK_PITCH", "50"))  # Pitch (0-99)

# =============================================================================
# OPENSTREETMAP / OVERPASS API CONFIGURATION
# =============================================================================

# Overpass API endpoint (free, no API key needed)
OVERPASS_API_URL = os.getenv(
    "OVERPASS_API_URL", 
    "https://overpass-api.de/api/interpreter"
)

# Default search radius in meters for nearby services
DEFAULT_SEARCH_RADIUS = int(os.getenv("DEFAULT_SEARCH_RADIUS", "5000"))

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Application metadata
APP_NAME = "Sahayak AI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Voice-Enabled Local Assistant for Everyday India"

# CORS settings for frontend
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:5500,https://sahayak-ai.vercel.app"
).split(",")

# Maximum audio file size (in bytes) - 10MB default
MAX_AUDIO_SIZE = int(os.getenv("MAX_AUDIO_SIZE", str(10 * 1024 * 1024)))

# =============================================================================
# GEMINI PROMPTS CONFIGURATION
# =============================================================================

# System prompt for Gemini to understand Indian context
GEMINI_SYSTEM_PROMPT = """
You are Sahayak AI, a helpful voice assistant designed specifically for Indian users.
Your role is to help with everyday tasks like:
- Mobile recharge procedures
- Government form filling guidance
- Finding nearby services (banks, hospitals, offices)
- Understanding local processes and procedures

IMPORTANT GUIDELINES:
1. Always respond in simple, easy-to-understand language
2. If the user speaks in Hindi, respond in Hindi (Hinglish is acceptable)
3. Provide step-by-step instructions when explaining processes
4. Be aware of Indian-specific context (UPI, Aadhaar, PAN, government schemes)
5. If asked about locations, provide India-specific information
6. Keep responses concise but complete
7. Use examples familiar to Indian users
8. If you don't know something specific, acknowledge it honestly

You are speaking to users who may not be tech-savvy, so be patient and clear.
"""

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
