# config.py - Centralized Configuration for IVERI AI

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === API KEYS ===
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PICOVOICE_ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

# === MODEL SETTINGS ===
GPT_MODEL = "gpt-5-nano"
MAX_TOKENS = 150
TEMPERATURE = 0.7

# === SPEECH SETTINGS ===
SPEECH_RATE = 150           # Words per minute
SPEECH_VOLUME = 0.9         # 0.0 to 1.0
SPEECH_LANGUAGE = "en-US"

# === RECOGNITION SETTINGS ===
ENERGY_THRESHOLD = 300
PAUSE_THRESHOLD = 0.8
LISTEN_TIMEOUT = 5          # Seconds
PHRASE_TIME_LIMIT = 10      # Seconds

# === WAKE WORD SETTINGS ===
DEFAULT_WAKE_WORD = "alexa"  # Built-in fallback
CUSTOM_WAKE_WORD_PATH = os.path.expanduser("~/iveri/models/IVERI_en_raspberry-pi.ppn")

# === FILE PATHS ===
PROJECT_DIR = os.path.expanduser("~/iveri")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MODELS_DIR = os.path.join(PROJECT_DIR, "models")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

# === GPIO PINS (Raspberry Pi) ===
LED_PIN = 17
BUTTON_PIN = 27
BUZZER_PIN = 22

# === CONVERSATION SETTINGS ===
MAX_CONVERSATION_HISTORY = 10  # Number of message pairs to remember

# === ENSURE DIRECTORIES EXIST ===
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def validate_config():
    """Validate that required configuration is present"""
    issues = []
    
    if not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY not set")
    
    if not PICOVOICE_ACCESS_KEY:
        issues.append("PICOVOICE_ACCESS_KEY not set")
    
    if issues:
        print("⚠️ Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("   Set these in your .env file")
    
    return len(issues) == 0


def print_config():
    """Print current configuration (for debugging)"""
    print("\n📋 IVERI AI Configuration:")
    print(f"   Model: {GPT_MODEL}")
    print(f"   OpenAI Key: {'✓ Set' if OPENAI_API_KEY else '✗ Missing'}")
    print(f"   Picovoice Key: {'✓ Set' if PICOVOICE_ACCESS_KEY else '✗ Missing'}")
    print(f"   Weather API: {'✓ Set' if WEATHER_API_KEY else '✗ Missing'}")
    print(f"   News API: {'✓ Set' if NEWS_API_KEY else '✗ Missing'}")
    print(f"   Data Directory: {DATA_DIR}")
    print()
