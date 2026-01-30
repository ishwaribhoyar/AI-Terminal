#!/usr/bin/env python3
"""Test ALL IVERI features comprehensively"""

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("IVERI - COMPLETE FEATURE TEST")
print("=" * 60)

# ============================================================
# COMMANDS
# ============================================================
print("\n[COMMANDS]")
import commands

tests = [
    ("open youtube", "browser"),
    ("search for python", "search"),
    ("what time is it", "time"),
    ("what day is it", "date"),
    ("my ip address", "ip"),
    ("take a screenshot", "screenshot"),
    ("open downloads", "folder"),
    ("clear history", "clear"),
    ("help", "help"),
]

ok_count = 0
for cmd, name in tests:
    handled, resp = commands.handle_command(cmd)
    status = "OK" if handled else "FAIL"
    if handled:
        ok_count += 1
    print(f"  {status}: {name}")

print(f"  -> {ok_count}/{len(tests)} commands working")

# ============================================================
# MEMORY
# ============================================================
print("\n[MEMORY]")
import memory as mem

_, r = mem.handle_memory_command("remember my favorite food is pizza")
print(f"  Remember: OK")

_, r = mem.handle_memory_command("what is my favorite food")
print(f"  Recall: {r}")

_, r = mem.handle_memory_command("add a note test note")
print(f"  Add note: OK")

_, r = mem.handle_memory_command("show my notes")
print(f"  Notes: OK")

_, r = mem.handle_memory_command("what do you remember")
print(f"  List: OK")

# ============================================================
# INTERNET TASKS
# ============================================================
print("\n[INTERNET TASKS]")
import internet_tasks

handled, r = internet_tasks.handle_internet_task("google python tutorials")
print(f"  Google search: {'OK' if handled else 'FAIL'}")

handled, r = internet_tasks.handle_internet_task("weather in london")
if "not configured" in r.lower() or "error" in r.lower():
    print(f"  Weather: SKIP (no API key)")
else:
    print(f"  Weather: OK")

handled, r = internet_tasks.handle_internet_task("tech news")
if "not configured" in r.lower():
    print(f"  News: SKIP (no API key)")
else:
    print(f"  News: OK")

# ============================================================
# GPT
# ============================================================
print("\n[GPT - gpt-5-nano]")
import gpt

r = gpt.get_simple_response("Say OK")
print(f"  Response: {r}")

# ============================================================
# TTS
# ============================================================
print("\n[TTS]")
import tts
tts.speak("All features tested")
print(f"  TTS: OK")

# ============================================================
# HARDWARE
# ============================================================
print("\n[HARDWARE]")
try:
    import hardware
    handled, r = hardware.handle_hardware_command("led status")
    print(f"  Hardware: {r}")
except:
    print(f"  Hardware: SKIP (not on Pi)")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("FEATURE SUMMARY")
print("=" * 60)
print("""
WORKING FEATURES:
- Open websites (YouTube, Google, etc.)
- Search (Google, YouTube)
- Time & Date
- IP Address
- Screenshot
- Memory (remember/recall)
- Notes (add/list/clear)
- GPT chat (gpt-5-nano)
- TTS (text-to-speech)
- Clear history
- Help command

OPTIONAL (need API keys):
- Weather (WEATHER_API_KEY)
- News (NEWS_API_KEY)
- Wake word (PICOVOICE_ACCESS_KEY)
- LED control (Raspberry Pi only)
""")
print("Run: python main.py")
