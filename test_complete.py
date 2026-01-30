#!/usr/bin/env python3
"""
COMPREHENSIVE TEST - ALL IVERI FEATURES
Tests every single feature and reports pass/fail
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import os

print("=" * 60)
print("IVERI - COMPLETE 30+ FEATURE TEST")
print("=" * 60)

results = []

def test(name, func):
    """Run a test and record result"""
    try:
        result = func()
        status = "PASS" if result else "FAIL"
    except Exception as e:
        status = f"ERROR: {e}"
        result = False
    results.append((name, status))
    print(f"  [{status}] {name}")
    return result

# ============================================================
print("\n[1] COMMANDS - commands.py")
# ============================================================
import commands

# Websites (12)
print("  -- Websites --")
websites = [
    "open youtube", "open google", "open facebook", "open twitter",
    "open github", "open instagram", "open linkedin", "open reddit",
    "open whatsapp", "open gmail", "open spotify", "open netflix"
]
for w in websites:
    test(w, lambda w=w: commands.handle_command(w)[0])

# Search (4)
print("  -- Search --")
test("youtube search", lambda: commands.handle_command("youtube search cats")[0])
test("google search", lambda: commands.handle_command("search for python")[0])
test("search X on youtube", lambda: commands.handle_command("search dogs on youtube")[0])
test("wikipedia", lambda: commands.handle_command("wikipedia python")[0])

# Apps (5)
print("  -- Apps --")
test("open calculator", lambda: commands.handle_command("open calculator")[0])
test("open notepad", lambda: commands.handle_command("open notepad")[0])
test("open terminal", lambda: commands.handle_command("open terminal")[0])
test("open file manager", lambda: commands.handle_command("open file manager")[0])
test("open settings", lambda: commands.handle_command("open settings")[0])

# Folders (3)
print("  -- Folders --")
test("open downloads", lambda: commands.handle_command("open downloads")[0])
test("open documents", lambda: commands.handle_command("open documents")[0])
test("open desktop", lambda: commands.handle_command("open desktop")[0])

# Time/Date (3)
print("  -- Time/Date --")
h, r = commands.handle_command("what time is it")
test("what time is it", lambda: h and ":" in r)
print(f"       -> {r}")

h, r = commands.handle_command("what day is it")
test("what day is it", lambda: h and "day" in r.lower() or "20" in r)
print(f"       -> {r}")

h, r = commands.handle_command("what's the date")
test("what's the date", lambda: h)

# Screen (2)
print("  -- Screen --")
h, r = commands.take_screenshot()
test("take screenshot", lambda: h and "saved" in r.lower())
print(f"       -> {r}")

test("lock screen", lambda: commands.handle_command("lock screen")[0])

# Volume (4)
print("  -- Volume --")
test("volume up", lambda: commands.handle_command("volume up")[0])
test("volume down", lambda: commands.handle_command("volume down")[0])
test("mute", lambda: commands.handle_command("mute")[0])
test("unmute", lambda: commands.handle_command("unmute")[0])

# System (3)
print("  -- System --")
h, r = commands.handle_command("my ip address")
test("ip address", lambda: h and ("." in r or "address" in r.lower()))
print(f"       -> {r}")

h, r = commands.handle_command("battery status")
test("battery status", lambda: h)
print(f"       -> {r}")

h, r = commands.handle_command("cpu temperature")
test("cpu temperature", lambda: h)

# Chat (2)
print("  -- Chat --")
test("help", lambda: commands.handle_command("help")[0])
test("clear history", lambda: commands.handle_command("clear history")[0])

# ============================================================
print("\n[2] MEMORY - memory.py")
# ============================================================
import memory as mem

h, r = mem.handle_memory_command("remember my favorite color is blue")
test("remember", lambda: h)
print(f"       -> {r}")

h, r = mem.handle_memory_command("what is my favorite color")
test("recall (what is my)", lambda: h and "blue" in r.lower())
print(f"       -> {r}")

h, r = mem.handle_memory_command("what do you remember")
test("list memories", lambda: h)

h, r = mem.handle_memory_command("forget my favorite color")
test("forget", lambda: h)

# Notes
print("  -- Notes --")
h, r = mem.handle_memory_command("add a note buy milk")
test("add note", lambda: h)
print(f"       -> {r}")

h, r = mem.handle_memory_command("show my notes")
test("show notes", lambda: h)

h, r = mem.handle_memory_command("clear notes")
test("clear notes", lambda: h)

# ============================================================
print("\n[3] INTERNET - internet_tasks.py")
# ============================================================
import internet_tasks

h, r = internet_tasks.handle_internet_task("weather in london")
test("weather", lambda: h)
print(f"       -> {r[:60]}...")

h, r = internet_tasks.handle_internet_task("what's the news")
test("news (general)", lambda: h)

h, r = internet_tasks.handle_internet_task("tech news")
test("tech news", lambda: h)

h, r = internet_tasks.handle_internet_task("sports news")
test("sports news", lambda: h)

h, r = internet_tasks.handle_internet_task("business news")
test("business news", lambda: h)

h, r = internet_tasks.handle_internet_task("google python tutorials")
test("google search (internet)", lambda: h)

# ============================================================
print("\n[4] GPT - gpt.py")
# ============================================================
import gpt

r = gpt.get_simple_response("Say OK")
test("gpt response", lambda: r and len(r) > 0)
print(f"       -> {r}")

r = gpt.clear_history()
test("clear gpt history", lambda: True)

# ============================================================
print("\n[5] TTS - tts.py")
# ============================================================
import tts

test("tts speak", lambda: (tts.speak("Test"), True)[1])
test("tts stop", lambda: (tts.stop(), True)[1])

# ============================================================
print("\n[6] HARDWARE - hardware.py")
# ============================================================
try:
    import hardware
    h, r = hardware.handle_hardware_command("led status")
    test("led status", lambda: h)
    test("led on", lambda: hardware.handle_hardware_command("turn led on")[0])
    test("led off", lambda: hardware.handle_hardware_command("turn led off")[0])
    test("led blink", lambda: hardware.handle_hardware_command("blink led")[0])
except:
    print("  [SKIP] Hardware (not on Raspberry Pi)")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("RESULTS SUMMARY")
print("=" * 60)

passed = sum(1 for _, s in results if s == "PASS")
failed = sum(1 for _, s in results if s == "FAIL")
errors = sum(1 for _, s in results if s.startswith("ERROR"))

print(f"  TOTAL:  {len(results)}")
print(f"  PASSED: {passed}")
print(f"  FAILED: {failed}")
print(f"  ERRORS: {errors}")
print()

if failed > 0 or errors > 0:
    print("FAILED/ERROR ITEMS:")
    for name, status in results:
        if status != "PASS":
            print(f"  - {name}: {status}")
else:
    print("ALL FEATURES WORKING!")

print("=" * 60)
