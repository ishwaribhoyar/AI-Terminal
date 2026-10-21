#!/usr/bin/env python3
"""
IVERI AI Assistant
Voice & Terminal AI Assistant for Windows, Linux, and Raspberry Pi
Modes: Chat (text/voice) | Wake (wake word or keyboard trigger)
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Ensure configuration is loaded
load_dotenv()

import config
import speech
import tts
import gpt
import commands
import internet_tasks
import memory as mem

# Optional hardware (Raspberry Pi GPIO)
try:
    import hardware
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False


def print_banner():
    print("\n" + "=" * 55)
    print("               🤖 IVERI AI ASSISTANT")
    print("=" * 55)
    print("  AI Model:      Gemini 1.5 Flash")
    has_key = bool(config.GEMINI_API_KEY and not config.GEMINI_API_KEY.startswith('your'))
    has_pico = bool(config.PICOVOICE_ACCESS_KEY and not config.PICOVOICE_ACCESS_KEY.startswith('your'))
    print(f"  AI Status:     {'Ready (Gemini API Key set)' if has_key else 'Local/Offline (commands ready)'}")
    print(f"  Wake Word:     {'Jarvis (Porcupine active)' if has_pico else 'Keyboard Trigger (ENTER)'}")
    print(f"  Voice (TTS):   {'Enabled' if config.ENABLE_TTS else 'Disabled (silent mode)'}")
    print("=" * 55)


def process_input(user_input):
    """Process user input through all handlers in priority order"""
    if not user_input or not user_input.strip():
        return "I didn't catch that."
    
    clean_input = user_input.strip()
    
    # 1. Local commands (time, date, websites, apps, calculator, screenshot, volume, etc.)
    handled, response = commands.handle_command(clean_input)
    if handled:
        return response
    
    # 2. Memory commands (remember, recall, forget, notes)
    handled, response = mem.handle_memory_command(clean_input)
    if handled:
        return response
    
    # 3. Internet tasks (weather, news, search, wikipedia)
    handled, response = internet_tasks.handle_internet_task(clean_input)
    if handled:
        return response
    
    # 4. Hardware commands (LED control on Raspberry Pi)
    if HAS_HARDWARE:
        handled, response = hardware.handle_hardware_command(clean_input)
        if handled:
            return response
    
    # 5. AI general knowledge (OpenAI / Local LLM)
    return gpt.get_response(clean_input)


def is_exit(text):
    """Check if user wants to exit"""
    if not text:
        return False
    words = ['goodbye', 'exit', 'quit', 'bye', 'stop']
    return any(w in text.lower().strip() for w in words)


# ==============================================================
# CHAT MODE - Text-to-text with optional voice input
# ==============================================================
def chat_mode():
    print("\n--- 💬 CHAT MODE ---")
    print("• Type your message and press ENTER")
    print("• Or press ENTER on empty line to speak via microphone")
    print("• Type 'wake' to switch to wake mode | 'help' for commands | 'quit' to exit")
    print("-" * 55 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            # Empty input = voice input trigger
            if user_input == '':
                if not speech.is_microphone_available():
                    print("IVERI: No microphone detected. Please type your message.\n")
                    continue
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
            
            # Process response
            response = process_input(user_input)
            print(f"IVERI: {response}\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\nIVERI: Goodbye!")
            return 'exit'


# ==============================================================
# WAKE MODE - Voice with wake word or keyboard trigger
# ==============================================================
def wake_mode():
    print("\n--- 🎙️ WAKE MODE ---")
    
    # Check if Picovoice wake word is available
    use_keyboard = True
    try:
        import wakeword
        detector = wakeword.WakeWordDetector()
        if not detector.use_keyboard:
            use_keyboard = False
            print("Say 'Jarvis' to activate IVERI")
        else:
            print("Keyboard trigger active: Press ENTER to speak (or type command)")
        detector.cleanup()
    except Exception:
        print("Keyboard trigger active: Press ENTER to speak (or type command)")
    
    print("Say 'goodbye' to exit | Type 'chat' for text mode | Press Ctrl+C to stop")
    print("-" * 55 + "\n")
    
    tts.speak("Wake mode active.")
    
    while True:
        try:
            if use_keyboard:
                cmd = input(">>> Press ENTER to speak (or type command): ").strip()
                if cmd.lower() == 'chat':
                    return 'chat'
                if is_exit(cmd):
                    tts.speak("Goodbye!")
                    return 'exit'
                # If user typed an actual command directly, process it
                if cmd:
                    response = process_input(cmd)
                    print(f"IVERI: {response}")
                    tts.speak(response)
                    continue
            else:
                import wakeword
                print("Waiting for wake word 'Jarvis'...")
                if not wakeword.wait_for_wake_word():
                    continue
            
            tts.speak("Yes?")
            user_input = speech.listen()
            
            if not user_input:
                tts.speak("Didn't catch that.")
                continue
            
            print(f"You said: {user_input}")
            
            if is_exit(user_input):
                tts.speak("Goodbye!")
                return 'exit'
            
            if 'chat mode' in user_input.lower():
                tts.speak("Switching to chat mode.")
                return 'chat'
            
            # Process and speak response
            response = process_input(user_input)
            print(f"IVERI: {response}")
            tts.speak(response)
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting wake mode...")
            return 'exit'


# ==============================================================
# SETUP WIZARD
# ==============================================================
def run_setup_wizard():
    """Interactive wizard to configure API keys and preferences"""
    import setup_wizard
    setup_wizard.interactive_setup()


# ==============================================================
# MAIN
# ==============================================================
def main():
    parser = argparse.ArgumentParser(description="IVERI - AI Voice & Terminal Assistant")
    parser.add_argument('--chat', action='store_true', help="Start directly in text chat mode")
    parser.add_argument('--wake', action='store_true', help="Start directly in voice wake mode")
    parser.add_argument('--setup', action='store_true', help="Run configuration setup wizard")
    parser.add_argument('--no-tts', action='store_true', help="Disable voice audio output (silent mode)")
    parser.add_argument('--status', action='store_true', help="Show current system configuration status")
    args = parser.parse_args()

    if args.no_tts:
        tts.set_enabled(False)
        config.ENABLE_TTS = False

    if args.status:
        config.print_config()
        return

    if args.setup:
        run_setup_wizard()
        return

    print_banner()

    # Determine starting mode
    if args.chat:
        mode = 'chat'
    elif args.wake:
        mode = 'wake'
    else:
        print("\nSelect mode:")
        print("  1. chat  - Text chat mode (press ENTER to speak)")
        print("  2. wake  - Voice wake mode ('Jarvis' or ENTER trigger)")
        print("  3. setup - Configure API keys and settings")
        try:
            choice = input("\nMode [1 for chat]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            return
        
        if choice in ['3', 'setup', 's']:
            run_setup_wizard()
            return
        elif choice in ['2', 'wake', 'w']:
            mode = 'wake'
        else:
            mode = 'chat'
    
    while True:
        if mode == 'chat':
            result = chat_mode()
        else:
            result = wake_mode()
        
        if result == 'exit':
            break
        mode = result
    
    if HAS_HARDWARE:
        try:
            hardware.cleanup()
        except Exception:
            pass
    
    print("\nIVERI shut down. Bye!")


if __name__ == "__main__":
    main()
