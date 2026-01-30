#!/usr/bin/env python3
"""
IVERI AI - Comprehensive End-to-End System Test
Tests ALL modules individually and together
"""

import os
import sys
import traceback

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("IVERI AI - COMPREHENSIVE END-TO-END SYSTEM TEST")
print("=" * 70)

errors = []
warnings = []

# ============================================================
# TEST 1: Environment Setup
# ============================================================
print("\n[1/10] Testing environment setup...")
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("   OK: .env file loaded")
    else:
        errors.append(".env file not found")
        print("   FAIL: .env file not found")
except Exception as e:
    errors.append(f"dotenv: {e}")
    print(f"   FAIL: {e}")

# ============================================================
# TEST 2: API Keys
# ============================================================
print("\n[2/10] Checking API keys...")
openai_key = os.getenv('OPENAI_API_KEY', '')
picovoice_key = os.getenv('PICOVOICE_ACCESS_KEY', '')

if openai_key and 'your' not in openai_key.lower():
    print(f"   OK: OPENAI_API_KEY set")
else:
    errors.append("OPENAI_API_KEY missing")
    print("   FAIL: OPENAI_API_KEY missing")

if picovoice_key and 'your' not in picovoice_key.lower():
    print(f"   OK: PICOVOICE_ACCESS_KEY set")
else:
    warnings.append("PICOVOICE_ACCESS_KEY missing - wake word disabled")
    print("   WARN: PICOVOICE_ACCESS_KEY missing")

# ============================================================
# TEST 3: Import All Modules
# ============================================================
print("\n[3/10] Testing module imports...")

modules_to_test = [
    ('openai', 'OpenAI API'),
    ('speech_recognition', 'Speech Recognition'),
    ('pyttsx3', 'Text-to-Speech'),
    ('pvporcupine', 'Wake Word (Porcupine)'),
    ('pvrecorder', 'Audio Recorder'),
    ('requests', 'HTTP Requests'),
    ('pygame', 'Pygame Audio'),
]

for module_name, description in modules_to_test:
    try:
        __import__(module_name)
        print(f"   OK: {description} ({module_name})")
    except ImportError as e:
        errors.append(f"Import {module_name}: {e}")
        print(f"   FAIL: {description} - {e}")

# ============================================================
# TEST 4: config.py
# ============================================================
print("\n[4/10] Testing config.py...")
try:
    import config
    print(f"   OK: config.py loaded")
    print(f"   -> GPT_MODEL: {config.GPT_MODEL}")
except Exception as e:
    errors.append(f"config.py: {e}")
    print(f"   FAIL: {e}")

# ============================================================
# TEST 5: gpt.py - OpenAI API
# ============================================================
print("\n[5/10] Testing gpt.py (OpenAI gpt-5-nano)...")
try:
    import gpt
    response = gpt.get_response("Say only the word 'SUCCESS'", use_history=False)
    if response:
        print(f"   OK: gpt.py working")
        print(f"   -> Response: {response[:100]}")
    else:
        errors.append("gpt.py returned empty response")
        print("   FAIL: Empty response")
except Exception as e:
    errors.append(f"gpt.py: {e}")
    print(f"   FAIL: {e}")
    traceback.print_exc()

# ============================================================
# TEST 6: speech.py
# ============================================================
print("\n[6/10] Testing speech.py...")
try:
    import speech
    import speech_recognition as sr
    
    # Check microphone availability
    mics = sr.Microphone.list_microphone_names()
    if mics:
        print(f"   OK: speech.py loaded, {len(mics)} microphones found")
    else:
        warnings.append("No microphones found")
        print("   WARN: No microphones detected")
except Exception as e:
    errors.append(f"speech.py: {e}")
    print(f"   FAIL: {e}")

# ============================================================
# TEST 7: tts.py
# ============================================================
print("\n[7/10] Testing tts.py...")
try:
    import tts
    print("   OK: tts.py loaded")
    # Test speaking
    tts.speak("IVERI end to end test successful")
    print("   OK: TTS spoke test message")
except Exception as e:
    errors.append(f"tts.py: {e}")
    print(f"   FAIL: {e}")

# ============================================================
# TEST 8: commands.py
# ============================================================
print("\n[8/10] Testing commands.py...")
try:
    import commands
    
    # Test time command
    handled, response = commands.handle_command("what time is it")
    if handled and response:
        print(f"   OK: commands.py working")
        print(f"   -> Time command: {response}")
    else:
        errors.append("commands.py time command failed")
        print("   FAIL: Time command not working")
except Exception as e:
    errors.append(f"commands.py: {e}")
    print(f"   FAIL: {e}")

# ============================================================
# TEST 9: memory.py
# ============================================================
print("\n[9/10] Testing memory.py...")
try:
    import memory
    
    # Test remember and recall
    result = memory.memory.remember("test_key", "test_value")
    recalled = memory.memory.recall("test_key")
    
    if recalled == "test_value":
        print("   OK: memory.py working (remember/recall)")
        # Clean up test
        memory.memory.forget("test_key")
    else:
        errors.append("memory.py recall failed")
        print("   FAIL: Recall returned wrong value")
except Exception as e:
    errors.append(f"memory.py: {e}")
    print(f"   FAIL: {e}")

# ============================================================
# TEST 10: wakeword.py
# ============================================================
print("\n[10/10] Testing wakeword.py...")
try:
    if picovoice_key and 'your' not in picovoice_key.lower():
        import wakeword
        print("   OK: wakeword.py loaded")
        print("   -> Wake word detection ready")
    else:
        print("   SKIP: No PICOVOICE_ACCESS_KEY (wake word disabled)")
        warnings.append("Wake word skipped - no API key")
except Exception as e:
    errors.append(f"wakeword.py: {e}")
    print(f"   FAIL: {e}")
    traceback.print_exc()

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

if not errors:
    print("\nALL TESTS PASSED!")
    print("\nTo run IVERI AI: python main.py")
else:
    print(f"\nERRORS ({len(errors)}):")
    for err in errors:
        print(f"   - {err}")

if warnings:
    print(f"\nWARNINGS ({len(warnings)}):")
    for warn in warnings:
        print(f"   - {warn}")

print("\n" + "=" * 70)
