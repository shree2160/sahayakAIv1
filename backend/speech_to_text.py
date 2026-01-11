"""
Sahayak AI - Speech to Text Module
==================================
Converts audio input to text using VOSK (offline, free).
Supports Hindi and English.
"""

import os
import json
import wave
import logging
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import tempfile

# VOSK imports
try:
    from vosk import Model, KaldiRecognizer, SetLogLevel
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("VOSK not installed. Run: pip install vosk")

from config import VOSK_MODEL_PATH, VOSK_SAMPLE_RATE, VOSK_MODEL_DIR

# Set up logging
logger = logging.getLogger(__name__)

# Suppress VOSK's verbose logging
if VOSK_AVAILABLE:
    SetLogLevel(-1)


class SpeechToText:
    """
    Speech-to-Text converter using VOSK.
    
    VOSK is an offline speech recognition toolkit that supports multiple languages
    including Hindi. It's completely free and doesn't require internet connection.
    
    Usage:
        stt = SpeechToText()
        text = stt.transcribe("audio.wav")
    """
    
    def __init__(self):
        """Initialize the VOSK model for Hindi/English recognition."""
        self.model = None
        self.is_ready = False
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """
        Load the VOSK model from disk.
        If model doesn't exist, provides instructions to download it.
        """
        if not VOSK_AVAILABLE:
            logger.error("VOSK library not available")
            return
        
        model_path = Path(VOSK_MODEL_PATH)
        
        if not model_path.exists():
            logger.warning(f"VOSK model not found at {model_path}")
            logger.info(
                "Please download the Hindi model from: "
                "https://alphacephei.com/vosk/models\n"
                "Recommended: vosk-model-small-hi-0.22\n"
                f"Extract it to: {VOSK_MODEL_DIR}"
            )
            return
        
        try:
            logger.info(f"Loading VOSK model from {model_path}")
            self.model = Model(str(model_path))
            self.is_ready = True
            logger.info("VOSK model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load VOSK model: {e}")
    
    def convert_to_wav(self, input_path: str, output_path: str) -> bool:
        """
        Convert audio file to WAV format suitable for VOSK.
        Uses ffmpeg for conversion (supports webm, mp3, ogg, etc.)
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output WAV file
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            # Use ffmpeg to convert to 16kHz mono WAV
            cmd = [
                "ffmpeg", "-y",  # Overwrite output
                "-i", input_path,
                "-ar", str(VOSK_SAMPLE_RATE),  # Sample rate
                "-ac", "1",  # Mono
                "-sample_fmt", "s16",  # 16-bit
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return False
            
            return True
            
        except FileNotFoundError:
            logger.error(
                "FFmpeg not found. Please install FFmpeg:\n"
                "Windows: choco install ffmpeg\n"
                "Ubuntu: sudo apt install ffmpeg\n"
                "Mac: brew install ffmpeg"
            )
            return False
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return False
    
    def transcribe(self, audio_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, WebM, MP3, etc.)
            
        Returns:
            Tuple of (transcribed_text, error_message)
            If successful, error_message is None
            If failed, transcribed_text is None
        """
        if not self.is_ready:
            return None, "Speech recognition model not loaded"
        
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            return None, f"Audio file not found: {audio_path}"
        
        # Convert to WAV if needed
        wav_path = audio_path
        temp_wav = None
        
        if audio_path.suffix.lower() != ".wav":
            # Create temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(
                suffix=".wav", 
                delete=False
            )
            temp_wav.close()
            
            if not self.convert_to_wav(str(audio_path), temp_wav.name):
                os.unlink(temp_wav.name)
                return None, "Failed to convert audio to WAV format"
            
            wav_path = Path(temp_wav.name)
        
        try:
            # Open and process WAV file
            with wave.open(str(wav_path), "rb") as wf:
                # Verify audio format
                if wf.getnchannels() != 1:
                    return None, "Audio must be mono (single channel)"
                
                if wf.getsampwidth() != 2:
                    return None, "Audio must be 16-bit"
                
                # Create recognizer
                recognizer = KaldiRecognizer(self.model, wf.getframerate())
                recognizer.SetWords(True)
                
                # Process audio in chunks
                full_text = []
                
                while True:
                    data = wf.readframes(4000)  # Read ~0.25 seconds
                    if len(data) == 0:
                        break
                    
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if result.get("text"):
                            full_text.append(result["text"])
                
                # Get final result
                final_result = json.loads(recognizer.FinalResult())
                if final_result.get("text"):
                    full_text.append(final_result["text"])
                
                transcribed = " ".join(full_text).strip()
                
                if not transcribed:
                    return None, "No speech detected in audio"
                
                logger.info(f"Transcribed: {transcribed}")
                return transcribed, None
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None, f"Transcription failed: {str(e)}"
        
        finally:
            # Clean up temporary file
            if temp_wav and os.path.exists(temp_wav.name):
                os.unlink(temp_wav.name)
    
    def transcribe_from_bytes(self, audio_bytes: bytes, file_format: str = "webm") -> Tuple[Optional[str], Optional[str]]:
        """
        Transcribe audio from bytes (useful for processing uploaded files).
        
        Args:
            audio_bytes: Raw audio data
            file_format: Format of the audio (webm, wav, mp3, etc.)
            
        Returns:
            Tuple of (transcribed_text, error_message)
        """
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_format}", 
                delete=False
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            # Transcribe
            result = self.transcribe(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing audio bytes: {e}")
            return None, str(e)
    
    def get_status(self) -> dict:
        """Get the status of the speech-to-text service."""
        return {
            "available": VOSK_AVAILABLE,
            "model_loaded": self.is_ready,
            "model_path": str(VOSK_MODEL_PATH),
            "sample_rate": VOSK_SAMPLE_RATE
        }


# Global instance for reuse
_stt_instance: Optional[SpeechToText] = None


def get_stt() -> SpeechToText:
    """Get or create the global SpeechToText instance."""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = SpeechToText()
    return _stt_instance


# =============================================================================
# FALLBACK: Web Speech API Alternative
# =============================================================================
# Note: If VOSK is not available, the frontend can use Web Speech API
# (browser-based, requires internet) as a fallback. The backend will
# receive the transcribed text directly via text_query parameter.
