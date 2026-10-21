# speech.py - Speech Recognition for IVERI AI

import speech_recognition as sr
try:
    import config
except ImportError:
    config = None

# Initialize recognizer
recognizer = sr.Recognizer()

# Stability settings for better recognition
recognizer.energy_threshold = getattr(config, 'ENERGY_THRESHOLD', 300)
recognizer.pause_threshold = getattr(config, 'PAUSE_THRESHOLD', 0.8)

def is_microphone_available():
    """Check if at least one audio input device is available"""
    try:
        mics = sr.Microphone.list_microphone_names()
        return len(mics) > 0
    except Exception:
        return False


def listen():
    """
    Listen for user speech and convert to text.
    
    Returns:
        Recognized text string, or None if recognition failed
    """
    if not is_microphone_available():
        print("⚠️ No microphone detected. Please connect a microphone or use keyboard input.")
        return None

    listen_timeout = getattr(config, 'LISTEN_TIMEOUT', 5)
    phrase_limit = getattr(config, 'PHRASE_TIME_LIMIT', 10)
    language = getattr(config, 'SPEECH_LANGUAGE', 'en-US')

    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = recognizer.listen(source, timeout=listen_timeout, phrase_time_limit=phrase_limit)
                print("🔄 Processing speech...")
                
                text = recognizer.recognize_google(audio, language=language)
                print(f"📝 You said: {text}")
                return text
                
            except sr.WaitTimeoutError:
                print("⏰ No speech detected")
                return None
            except sr.UnknownValueError:
                print("❓ Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition network error: {e}")
                return None
    except Exception as e:
        print(f"⚠️ Microphone error: {e}")
        return None


def listen_for_duration(duration=5):
    """
    Listen for a specific duration.
    
    Args:
        duration: How long to listen in seconds
    
    Returns:
        Recognized text string, or None if recognition failed
    """
    if not is_microphone_available():
        print("⚠️ No microphone detected.")
        return None

    language = getattr(config, 'SPEECH_LANGUAGE', 'en-US')
    try:
        with sr.Microphone() as source:
            print(f"🎤 Listening for {duration} seconds...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            
            audio = recognizer.record(source, duration=duration)
            text = recognizer.recognize_google(audio, language=language)
            return text
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
