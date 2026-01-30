#!/usr/bin/env python3
"""
IVERI AI Assistant
Modes: Chat (text) | Wake (voice with Jarvis or keyboard)
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys

import speech
import tts
import gpt
import commands
import internet_tasks
import memory as mem

# Optional hardware
try:
    import hardware
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False


def print_banner():
    print("\n" + "=" * 50)
    print("IVERI AI ASSISTANT")
    print("=" * 50)
    print("Model: gpt-5-nano")
    print("Modes: chat (text) | wake (voice)")
    print("=" * 50)


def process_input(user_input):
    """Process user input through all handlers"""
    if not user_input:
        return "I didn't understand that."
    
    # 1. Local commands (time, date, websites, etc.)
    handled, response = commands.handle_command(user_input)
    if handled:
        return response
    
    # 2. Memory commands
    handled, response = mem.handle_memory_command(user_input)
    if handled:
        return response
    
    # 3. Internet tasks (weather, news)
    handled, response = internet_tasks.handle_internet_task(user_input)
    if handled:
        return response
    
    # 4. Hardware commands (LED)
    if HAS_HARDWARE:
        handled, response = hardware.handle_hardware_command(user_input)
        if handled:
            return response
    
    # 5. Ask GPT
    return gpt.get_response(user_input)


def is_exit(text):
    """Check if user wants to exit"""
    if not text:
        return False
    words = ['goodbye', 'exit', 'quit', 'bye', 'stop']
    return any(w in text.lower() for w in words)


# ==============================================================
# CHAT MODE - Text-to-text with optional voice input
# ==============================================================
def chat_mode():
    print("\n--- CHAT MODE ---")
    print("Type message or press ENTER to speak")
    print("Type 'wake' to switch | 'quit' to exit")
    print("-" * 30 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            # Empty = voice input
            if user_input == '':
                print("Listening...")
                user_input = speech.listen()
                if not user_input:
                    print("IVERI: Didn't catch that.\n")
                    continue
                print(f"(You said: {user_input})")
            
            if user_input.lower() == 'wake':
                return 'wake'
            
            if is_exit(user_input):
                print("IVERI: Goodbye!")
                return 'exit'
            
            # Process
            response = process_input(user_input)
            print(f"IVERI: {response}\n")
            
        except (KeyboardInterrupt, EOFError):
            return 'exit'


# ==============================================================
# WAKE MODE - Voice with wake word or keyboard trigger
# ==============================================================
def wake_mode():
    print("\n--- WAKE MODE ---")
    
    # Check if Picovoice wake word is available
    use_keyboard = True
    try:
        import wakeword
        detector = wakeword.WakeWordDetector()
        if not detector.use_keyboard:
            use_keyboard = False
            print("Say 'Jarvis' to activate")
        else:
            print("Press ENTER to speak (wake word unavailable)")
        detector.cleanup()
    except:
        print("Press ENTER to speak")
    
    print("Say 'goodbye' to exit | Type 'chat' for text mode")
    print("-" * 30 + "\n")
    
    tts.speak("Wake mode active.")
    
    while True:
        try:
            if use_keyboard:
                # Keyboard activation
                cmd = input(">>> Press ENTER to speak: ").strip().lower()
                if cmd == 'chat':
                    return 'chat'
                if cmd in ['quit', 'exit']:
                    tts.speak("Goodbye!")
                    return 'exit'
            else:
                # Wake word activation
                import wakeword
                print("Waiting for 'Jarvis'...")
                if not wakeword.wait_for_wake_word():
                    continue
            
            tts.speak("Yes?")
            print("Listening...")
            user_input = speech.listen()
            
            if not user_input:
                tts.speak("Didn't catch that.")
                continue
            
            print(f"You said: {user_input}")
            
            if is_exit(user_input):
                tts.speak("Goodbye!")
                return 'exit'
            
            if 'chat mode' in user_input.lower():
                tts.speak("Switching to chat.")
                return 'chat'
            
            # Process and speak response
            response = process_input(user_input)
            print(f"IVERI: {response}")
            tts.speak(response)
            
        except (KeyboardInterrupt, EOFError):
            return 'exit'


# ==============================================================
# MAIN
# ==============================================================
def main():
    print_banner()
    
    print("\nSelect mode:")
    print("  1. chat - Type messages (press ENTER to speak)")
    print("  2. wake - Voice mode (Jarvis or keyboard)")
    
    try:
        choice = input("\nMode [chat]: ").strip().lower()
    except:
        choice = 'chat'
    
    mode = 'wake' if choice in ['2', 'wake', 'w'] else 'chat'
    
    while True:
        if mode == 'chat':
            result = chat_mode()
        else:
            result = wake_mode()
        
        if result == 'exit':
            break
        mode = result
    
    if HAS_HARDWARE:
        hardware.cleanup()
    
    print("\nIVERI shut down. Bye!")


if __name__ == "__main__":
    main()
