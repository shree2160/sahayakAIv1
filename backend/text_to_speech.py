"""
Sahayak AI - Text to Speech Module
==================================
Converts text responses to speech using eSpeak NG (offline, free).
Supports Hindi and English output.
"""

import os
import subprocess
import tempfile
import base64
import logging
from pathlib import Path
from typing import Optional, Tuple

from config import ESPEAK_VOICE, ESPEAK_SPEED, ESPEAK_PITCH, AUDIO_DIR

# Set up logging
logger = logging.getLogger(__name__)


class TextToSpeech:
    """
    Text-to-Speech converter using eSpeak NG.
    
    eSpeak NG is a compact, open-source speech synthesizer that supports
    many languages including Hindi. It works completely offline.
    
    Installation:
        Windows: Download from https://github.com/espeak-ng/espeak-ng/releases
        Ubuntu: sudo apt install espeak-ng
        Mac: brew install espeak-ng
    
    Usage:
        tts = TextToSpeech()
        audio_path = tts.synthesize("नमस्ते, आप कैसे हैं?")
    """
    
    def __init__(self, voice: str = None, speed: int = None, pitch: int = None):
        """
        Initialize TTS with configuration.
        
        Args:
            voice: Voice/language code (e.g., 'hi' for Hindi, 'en' for English)
            speed: Speaking rate in words per minute (80-450)
            pitch: Voice pitch (0-99)
        """
        self.voice = voice or ESPEAK_VOICE
        self.speed = speed or ESPEAK_SPEED
        self.pitch = pitch or ESPEAK_PITCH
        self.is_ready = self._check_espeak()
    
    def _check_espeak(self) -> bool:
        """Check if eSpeak NG is installed and accessible."""
        try:
            result = subprocess.run(
                ["espeak-ng", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"eSpeak NG found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            # Try alternative command name on some systems
            try:
                result = subprocess.run(
                    ["espeak", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.espeak_cmd = "espeak"
                    logger.info(f"eSpeak found: {result.stdout.strip()}")
                    return True
            except FileNotFoundError:
                pass
        except Exception as e:
            logger.error(f"Error checking eSpeak: {e}")
        
        logger.warning(
            "eSpeak NG not found. Please install it:\n"
            "Windows: Download from https://github.com/espeak-ng/espeak-ng/releases\n"
            "Ubuntu: sudo apt install espeak-ng\n"
            "Mac: brew install espeak-ng"
        )
        return False
    
    @property
    def espeak_command(self) -> str:
        """Get the correct eSpeak command for this system."""
        return getattr(self, 'espeak_cmd', 'espeak-ng')
    
    def synthesize(
        self, 
        text: str, 
        output_path: str = None,
        voice: str = None,
        speed: int = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Convert text to speech and save as audio file.
        
        Args:
            text: Text to convert to speech
            output_path: Path for output audio file (optional)
            voice: Override voice setting
            speed: Override speed setting
            
        Returns:
            Tuple of (audio_file_path, error_message)
        """
        if not self.is_ready:
            return None, "eSpeak NG not available"
        
        if not text or not text.strip():
            return None, "No text provided for synthesis"
        
        # Generate output path if not provided
        if output_path is None:
            output_path = os.path.join(
                AUDIO_DIR,
                f"response_{os.urandom(8).hex()}.wav"
            )
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Build eSpeak command
        cmd = [
            self.espeak_command,
            "-v", voice or self.voice,  # Voice/language
            "-s", str(speed or self.speed),  # Speed
            "-p", str(self.pitch),  # Pitch
            "-w", output_path,  # Output WAV file
            text
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"eSpeak error: {result.stderr}")
                return None, f"Speech synthesis failed: {result.stderr}"
            
            if not os.path.exists(output_path):
                return None, "Audio file was not created"
            
            logger.info(f"Audio generated: {output_path}")
            return output_path, None
            
        except subprocess.TimeoutExpired:
            return None, "Speech synthesis timed out"
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None, f"Speech synthesis error: {str(e)}"
    
    def synthesize_to_base64(
        self, 
        text: str, 
        voice: str = None,
        speed: int = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Convert text to speech and return as base64-encoded audio.
        
        Args:
            text: Text to convert to speech
            voice: Override voice setting
            speed: Override speed setting
            
        Returns:
            Tuple of (base64_audio, error_message)
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Synthesize to file
            audio_path, error = self.synthesize(
                text, 
                temp_path, 
                voice, 
                speed
            )
            
            if error:
                return None, error
            
            # Read and encode as base64
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            return audio_base64, None
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def list_voices(self) -> list:
        """List available eSpeak NG voices."""
        if not self.is_ready:
            return []
        
        try:
            result = subprocess.run(
                [self.espeak_command, "--voices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                voices = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 4:
                        voices.append({
                            "language": parts[1],
                            "name": parts[3] if len(parts) > 3 else parts[1],
                            "gender": parts[2] if len(parts) > 2 else "?"
                        })
                return voices
            
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
        
        return []
    
    def get_status(self) -> dict:
        """Get the status of the text-to-speech service."""
        return {
            "available": self.is_ready,
            "voice": self.voice,
            "speed": self.speed,
            "pitch": self.pitch,
            "command": self.espeak_command if self.is_ready else None
        }


# Global instance for reuse
_tts_instance: Optional[TextToSpeech] = None


def get_tts() -> TextToSpeech:
    """Get or create the global TextToSpeech instance."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech()
    return _tts_instance


# =============================================================================
# ALTERNATIVE TTS OPTIONS
# =============================================================================
"""
If eSpeak NG is not suitable, here are other FREE TTS options:

1. gTTS (Google Text-to-Speech) - Requires internet
   pip install gtts
   from gtts import gTTS
   tts = gTTS(text="नमस्ते", lang='hi')
   tts.save("output.mp3")

2. pyttsx3 - Offline, uses system voices
   pip install pyttsx3
   import pyttsx3
   engine = pyttsx3.init()
   engine.say("Hello")
   engine.runAndWait()

3. Web Speech API (Frontend fallback)
   Uses browser's built-in speech synthesis
   Implemented in frontend/app.js
"""
