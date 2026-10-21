#!/usr/bin/env python3
"""
setup_wizard.py - Interactive Setup & Configuration Wizard for IVERI AI
Helps users configure their Gemini API key, ElevenLabs voice key, audio settings, and optional services.
"""

import os
import sys

def interactive_setup():
    print("\n" + "=" * 60)
    print("        ⚙️ IVERI AI ASSISTANT - SETUP WIZARD")
    print("=" * 60)
    print("AI Model: Google Gemini Flash")
    print("Voice Engine: ElevenLabs Flash v2.5 (Fastest & Lowest Cost)\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    
    current_config = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    current_config[k.strip()] = v.strip()

    # 1. Gemini API Key
    print("[1/5] Google Gemini API Key")
    print("  Used for intelligent conversation and general answers.")
    print("  Get your FREE Gemini API key at: https://aistudio.google.com/app/apikey")
    cur_gemini = current_config.get("GEMINI_API_KEY", "")
    if cur_gemini and not cur_gemini.startswith("your"):
        default_display = f"[{cur_gemini[:8]}...{cur_gemini[-4:]}]"
    else:
        default_display = "[None]"
    gemini_key = input(f"  Enter Gemini API Key {default_display}: ").strip()
    if not gemini_key and cur_gemini:
        gemini_key = cur_gemini

    # 2. ElevenLabs API Key
    print("\n[2/5] ElevenLabs API Key (Flash v2.5 Voice)")
    print("  Used for high-fidelity speech synthesis (~75ms latency).")
    print("  Get your API key at: https://elevenlabs.io/app/settings/api-keys")
    print("  (Make sure 'Text to Speech' permission is enabled on your key)")
    cur_eleven = current_config.get("ELEVENLABS_API_KEY", "")
    if cur_eleven and not cur_eleven.startswith("your"):
        eleven_display = f"[{cur_eleven[:8]}...{cur_eleven[-4:]}]"
    else:
        eleven_display = "[None]"
    eleven_key = input(f"  Enter ElevenLabs API Key {eleven_display}: ").strip()
    if not eleven_key and cur_eleven:
        eleven_key = cur_eleven

    # 3. Picovoice Wake Word Key
    print("\n[3/5] Picovoice Access Key (Optional)")
    print("  Used for hands-free 'Jarvis' wake word detection.")
    print("  Free tier at: https://console.picovoice.ai/")
    print("  (Leave blank to use ENTER key trigger instead)")
    cur_pico = current_config.get("PICOVOICE_ACCESS_KEY", "")
    pico_display = f"[{cur_pico[:7]}...]" if cur_pico and not cur_pico.startswith("your") else "[None]"
    pico_key = input(f"  Enter Picovoice Key {pico_display}: ").strip()
    if not pico_key and cur_pico:
        pico_key = cur_pico

    # 4. OpenWeatherMap API Key
    print("\n[4/5] OpenWeatherMap Key (Optional)")
    print("  (Note: IVERI has a free built-in weather fallback if omitted!)")
    cur_weather = current_config.get("WEATHER_API_KEY", "")
    weather_display = f"[{cur_weather[:6]}...]" if cur_weather and not cur_weather.startswith("your") else "[None]"
    weather_key = input(f"  Enter OpenWeatherMap Key {weather_display}: ").strip()
    if not weather_key and cur_weather:
        weather_key = cur_weather

    # 5. NewsAPI Key
    print("\n[5/5] NewsAPI Key (Optional)")
    print("  (Note: IVERI now has built-in real-time Online RAG news if omitted!)")
    cur_news = current_config.get("NEWS_API_KEY", "")
    news_display = f"[{cur_news[:6]}...]" if cur_news and not cur_news.startswith("your") else "[None]"
    news_key = input(f"  Enter NewsAPI Key {news_display}: ").strip()
    if not news_key and cur_news:
        news_key = cur_news

    # Write .env file
    env_content = f"""# IVERI AI Assistant - Environment Configuration
# Automatically generated / updated by setup_wizard.py

# === AI CONFIGURATION (Gemini Flash) ===
GEMINI_API_KEY={gemini_key if gemini_key else 'your-gemini-api-key-here'}

# === ELEVENLABS SPEECH SYNTHESIS (Eleven Flash v2.5) ===
ELEVENLABS_API_KEY={eleven_key if eleven_key else 'your-elevenlabs-api-key-here'}
ELEVENLABS_MODEL_ID=eleven_flash_v2_5
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# === WAKE WORD ===
PICOVOICE_ACCESS_KEY={pico_key if pico_key else 'your-picovoice-access-key-here'}

# === EXTRA SERVICES ===
WEATHER_API_KEY={weather_key if weather_key else 'your-openweathermap-api-key-here'}
NEWS_API_KEY={news_key if news_key else 'your-newsapi-key-here'}

# === VOICE SETTINGS ===
ENABLE_TTS=true
SPEECH_RATE=150
SPEECH_VOLUME=0.9
SPEECH_LANGUAGE=en-US
"""

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)

    print("\n" + "=" * 60)
    print("✅ Configuration successfully saved to .env!")
    print("You can run IVERI anytime using: python main.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    interactive_setup()
