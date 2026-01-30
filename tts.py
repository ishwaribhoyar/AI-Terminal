# tts.py - Text to Speech for IVERI AI

import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()


def setup_voice():
    """Configure IVERI's voice settings"""
    # Set speech rate (words per minute)
    engine.setProperty('rate', 150)
    
    # Set volume (0.0 to 1.0)
    engine.setProperty('volume', 0.9)
    
    # Get available voices and try to set a suitable one
    voices = engine.getProperty('voices')
    
    # Try to use a female voice for IVERI (if available)
    for voice in voices:
        if 'female' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            print(f"🔊 Using voice: {voice.name}")
            break
    else:
        # Use first available voice if no female voice found
        if voices:
            engine.setProperty('voice', voices[0].id)


def speak(text):
    """
    Convert text to speech and play it.
    
    Args:
        text: The text to speak
    """
    print(f"🔊 IVERI: {text}")
    engine.say(text)
    engine.runAndWait()


def speak_async(text):
    """
    Start speaking without waiting for completion.
    
    Args:
        text: The text to speak
    """
    print(f"🔊 IVERI: {text}")
    engine.say(text)
    engine.startLoop(False)
    engine.iterate()


def stop():
    """Stop current speech"""
    engine.stop()


def set_rate(rate):
    """
    Set speech rate.
    
    Args:
        rate: Words per minute (default 150)
    """
    engine.setProperty('rate', rate)


def set_volume(volume):
    """
    Set speech volume.
    
    Args:
        volume: Volume level 0.0 to 1.0
    """
    engine.setProperty('volume', max(0.0, min(1.0, volume)))


# Setup voice on module load
setup_voice()
