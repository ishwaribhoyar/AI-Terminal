# tts.py - High-Performance Text-to-Speech for IVERI AI
# Powered by ElevenLabs Eleven Flash v2.5 with local offline fallback

import os
import sys
import hashlib
import time
import requests

# Ensure UTF-8 console on Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def _safe_print(msg):
    """Print safely across Windows, Linux, and legacy terminals"""
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            clean = msg.encode('ascii', errors='replace').decode('ascii')
            print(clean)
        except Exception:
            pass


try:
    import config
except ImportError:
    config = None

TTS_ENABLED = getattr(config, 'ENABLE_TTS', True)

# Audio player initialization via pygame
_pygame_initialized = False
try:
    import pygame
    pygame.mixer.init()
    _pygame_initialized = True
except Exception as e:
    _pygame_initialized = False

# Local offline TTS engine (pyttsx3) fallback
_offline_engine = None
try:
    if TTS_ENABLED:
        import pyttsx3
        _offline_engine = pyttsx3.init()
        rate = getattr(config, 'SPEECH_RATE', 150)
        volume = getattr(config, 'SPEECH_VOLUME', 0.9)
        _offline_engine.setProperty('rate', rate)
        _offline_engine.setProperty('volume', volume)
except Exception:
    _offline_engine = None

# Track if ElevenLabs warning has been shown to avoid spamming console
_eleven_warning_shown = False


def _play_audio_file(filepath):
    """Play audio file using pygame.mixer"""
    if not _pygame_initialized:
        return False
    try:
        import pygame
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(20)
        pygame.mixer.music.unload()
        return True
    except Exception as e:
        print(f"Audio playback note: {e}")
        return False


def _speak_elevenlabs(text):
    """
    Synthesize and play speech using ElevenLabs Flash v2.5 (~75ms latency)
    
    Returns:
        bool: True if successful, False if failed
    """
    global _eleven_warning_shown
    
    api_key = getattr(config, 'ELEVENLABS_API_KEY', '') or os.getenv('ELEVENLABS_API_KEY', '')
    if not api_key or api_key.startswith('your'):
        return False
        
    voice_id = getattr(config, 'ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
    model_id = getattr(config, 'ELEVENLABS_MODEL_ID', 'eleven_flash_v2_5')
    cache_dir = getattr(config, 'CACHE_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'audio'))
    os.makedirs(cache_dir, exist_ok=True)
    
    # Hash text to check local audio cache (saves latency and character quota)
    text_hash = hashlib.md5(f"{model_id}_{voice_id}_{text}".encode('utf-8')).hexdigest()
    cache_file = os.path.join(cache_dir, f"{text_hash}.mp3")
    
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 500:
        return _play_audio_file(cache_file)
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(cache_file, "wb") as f:
                f.write(response.content)
            return _play_audio_file(cache_file)
        elif response.status_code == 401:
            if not _eleven_warning_shown:
                _safe_print("⚠️ ElevenLabs Note: API key is missing 'text_to_speech' permission. Falling back to offline voice.")
                _eleven_warning_shown = True
            return False
        elif response.status_code == 429:
            if not _eleven_warning_shown:
                _safe_print("⚠️ ElevenLabs Note: Rate limit or character quota reached. Falling back to offline voice.")
                _eleven_warning_shown = True
            return False
        else:
            if not _eleven_warning_shown:
                _safe_print(f"⚠️ ElevenLabs API ({response.status_code}). Using offline voice fallback.")
                _eleven_warning_shown = True
            return False
    except Exception as e:
        if not _eleven_warning_shown:
            _safe_print(f"ElevenLabs connection note: {e}. Using offline voice.")
            _eleven_warning_shown = True
        return False


def _speak_offline(text):
    """Fallback local speech synthesis using pyttsx3"""
    if _offline_engine and TTS_ENABLED:
        try:
            _offline_engine.say(text)
            _offline_engine.runAndWait()
            return True
        except Exception:
            return False
    return False


def speak(text):
    """
    Convert text to speech and play it.
    Prioritizes ElevenLabs Flash v2.5; falls back to offline engine gracefully.
    
    Args:
        text: The text to speak
    """
    if not text:
        return
        
    _safe_print(f"🔊 IVERI: {text}")
    
    if not TTS_ENABLED:
        return

    # 1. Try ElevenLabs Flash v2.5
    success = _speak_elevenlabs(text)
    
    # 2. Offline fallback if ElevenLabs is unavailable or unpermitted
    if not success:
        _speak_offline(text)


def speak_async(text):
    """Speak text asynchronously"""
    speak(text)


def stop():
    """Stop current speech playback"""
    try:
        if _pygame_initialized:
            import pygame
            pygame.mixer.music.stop()
    except Exception:
        pass
        
    try:
        if _offline_engine:
            _offline_engine.stop()
    except Exception:
        pass


def set_rate(rate):
    """Set speech rate (words per minute) for offline engine"""
    if _offline_engine:
        try:
            _offline_engine.setProperty('rate', rate)
        except Exception:
            pass


def set_volume(volume):
    """Set speech volume (0.0 to 1.0)"""
    if _offline_engine:
        try:
            _offline_engine.setProperty('volume', max(0.0, min(1.0, volume)))
        except Exception:
            pass
    if _pygame_initialized:
        try:
            import pygame
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        except Exception:
            pass


def set_enabled(enabled):
    """Enable or disable voice output"""
    global TTS_ENABLED
    TTS_ENABLED = enabled
