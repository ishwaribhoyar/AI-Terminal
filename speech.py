# speech.py - Speech Recognition for IVERI AI

import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Stability settings for better recognition
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.8


def listen():
    """
    Listen for user speech and convert to text.
    
    Returns:
        Recognized text string, or None if recognition failed
    """
    with sr.Microphone() as source:
        print("🎤 Listening...")
        
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listen with timeout and phrase limit
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("🔄 Processing...")
            
            # Use Google Speech Recognition with explicit language
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"📝 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None


def listen_for_duration(duration=5):
    """
    Listen for a specific duration.
    
    Args:
        duration: How long to listen in seconds
    
    Returns:
        Recognized text string, or None if recognition failed
    """
    with sr.Microphone() as source:
        print(f"🎤 Listening for {duration} seconds...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        
        try:
            audio = recognizer.record(source, duration=duration)
            text = recognizer.recognize_google(audio, language="en-US")
            return text
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
