# config.py - Centralized Configuration for IVERI AI

import os
import sys
import shutil
from dotenv import load_dotenv

# Ensure console supports utf-8 encoding on Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Base directory of the repository
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure .env exists; copy from .env.example if missing
env_path = os.path.join(BASE_DIR, '.env')
example_env_path = os.path.join(BASE_DIR, '.env.example')
if not os.path.exists(env_path) and os.path.exists(example_env_path):
    try:
        shutil.copyfile(example_env_path, env_path)
    except Exception:
        pass

# Load environment variables
load_dotenv(env_path)

# === API KEYS ===
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
PICOVOICE_ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY', '')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

# === MODEL SETTINGS (Gemini Flash) ===
AI_MODEL = "gemini-1.5-flash"
GPT_MODEL = AI_MODEL
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.5'))

# === SPEECH & TTS SETTINGS ===
ENABLE_TTS = os.getenv('ENABLE_TTS', 'true').lower() in ('true', '1', 'yes')
TTS_PROVIDER = os.getenv('TTS_PROVIDER', 'elevenlabs' if ELEVENLABS_API_KEY else 'local').lower()
ELEVENLABS_MODEL_ID = os.getenv('ELEVENLABS_MODEL_ID', 'eleven_flash_v2_5')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Rachel
SPEECH_RATE = int(os.getenv('SPEECH_RATE', '150'))           # Words per minute for offline fallback
SPEECH_VOLUME = float(os.getenv('SPEECH_VOLUME', '0.9'))      # 0.0 to 1.0
SPEECH_LANGUAGE = os.getenv('SPEECH_LANGUAGE', 'en-US')

# === RECOGNITION SETTINGS ===
ENERGY_THRESHOLD = int(os.getenv('ENERGY_THRESHOLD', '300'))
PAUSE_THRESHOLD = float(os.getenv('PAUSE_THRESHOLD', '0.8'))
LISTEN_TIMEOUT = int(os.getenv('LISTEN_TIMEOUT', '5'))        # Seconds
PHRASE_TIME_LIMIT = int(os.getenv('PHRASE_TIME_LIMIT', '10')) # Seconds

# === FILE PATHS ===
PROJECT_DIR = os.getenv('IVERI_HOME', BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MODELS_DIR = os.path.join(PROJECT_DIR, "models")
CACHE_DIR = os.path.join(PROJECT_DIR, "cache", "audio")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

# === WAKE WORD SETTINGS ===
DEFAULT_WAKE_WORD = "jarvis"
CUSTOM_WAKE_WORD_PATH = os.path.join(MODELS_DIR, "IVERI_en_raspberry-pi.ppn")

# === GPIO PINS (Raspberry Pi) ===
LED_PIN = 17
BUTTON_PIN = 27
BUZZER_PIN = 22

# === CONVERSATION SETTINGS ===
MAX_CONVERSATION_HISTORY = 10

# === ENSURE DIRECTORIES EXIST ===
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def validate_config():
    """Validate configuration and print clear advisory status"""
    issues = []
    
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith('your'):
        issues.append("GEMINI_API_KEY not configured (Get free key at https://aistudio.google.com/app/apikey)")
    
    if issues:
        print("ℹ️ Configuration Notes:")
        for issue in issues:
            print(f"   - {issue}")
    
    return len(issues) == 0


def print_config():
    """Print current configuration (for debugging)"""
    print("\n📋 IVERI AI Configuration:")
    print(f"   AI Model: {AI_MODEL} (Google Gemini Flash)")
    has_gemini = bool(GEMINI_API_KEY and not GEMINI_API_KEY.startswith('your'))
    has_eleven = bool(ELEVENLABS_API_KEY and not ELEVENLABS_API_KEY.startswith('your'))
    has_pico = bool(PICOVOICE_ACCESS_KEY and not PICOVOICE_ACCESS_KEY.startswith('your'))
    has_weather = bool(WEATHER_API_KEY and not WEATHER_API_KEY.startswith('your'))
    print(f"   Gemini Key: {'✓ Set' if has_gemini else '✗ Missing'}")
    print(f"   TTS Engine: ElevenLabs Flash v2.5 ({'✓ Key Set' if has_eleven else '○ Offline Fallback'})")
    print(f"   Wake Word: {'Jarvis (Porcupine active)' if has_pico else 'Keyboard Trigger (ENTER)'}")
    print(f"   Weather API: {'✓ Set' if has_weather else '○ Free Fallback Active (wttr.in)'}")
    print(f"   TTS Enabled: {'✓ Yes' if ENABLE_TTS else '✗ Disabled'}")
    print(f"   Data Directory: {DATA_DIR}")
    print()
