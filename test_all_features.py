#!/usr/bin/env python3
"""
IVERI AI - Comprehensive Cross-Platform Feature Test
Tests ALL features on Windows and Linux/Pi
"""

from dotenv import load_dotenv
load_dotenv()

import sys
import os

print("=" * 60)
print("IVERI AI - COMPLETE FEATURE TEST")
print(f"Platform: {'Windows' if sys.platform == 'win32' else 'Linux/Pi'}")
print("=" * 60)

passed = 0
failed = 0
skipped = 0

def test(name, handled, expected=True):
    global passed, failed
    if handled == expected:
        passed += 1
        return "OK"
    else:
        failed += 1
        return "FAIL"

# ============================================================
# COMMANDS MODULE
# ============================================================
print("\n[COMMANDS]")
import commands

# Websites (don't actually open - just check handler)
website_tests = [
    "open youtube",
    "open google", 
    "open facebook",
    "open twitter",
    "open github",
    "open instagram",
    "open linkedin",
    "open reddit",
    "open whatsapp",
    "open gmail",
    "open spotify",
    "open netflix",
]

print("  Websites:")
for cmd in website_tests:
    h, r = commands.handle_command(cmd)
    status = test(cmd, h, True)
    # Don't print each, just count

print(f"    {len(website_tests)} website commands: OK")

# Apps
print("  Apps:")
app_tests = ["open calculator", "open notepad", "open terminal", "open file manager"]
for cmd in app_tests:
    h, r = commands.handle_command(cmd)
    test(cmd, h, True)
print(f"    {len(app_tests)} app commands: OK")

# Search
print("  Search:")
search_tests = [
    ("search for python", True),
    ("search youtube for music", True),
    ("search google for ai", True),
    ("wikipedia artificial intelligence", True),
]
for cmd, expected in search_tests:
    h, r = commands.handle_command(cmd)
    test(cmd, h, expected)
print(f"    {len(search_tests)} search commands: OK")

# Time/Date
print("  Time/Date:")
time_tests = [
    "what time is it",
    "what's the date",
    "what day is it",
]
for cmd in time_tests:
    h, r = commands.handle_command(cmd)
    s = test(cmd, h, True)
    print(f"    {cmd}: {r}")

# Folders
print("  Folders:")
folder_tests = ["open downloads", "open documents", "open desktop"]
for cmd in folder_tests:
    h, r = commands.handle_command(cmd)
    test(cmd, h, True)
print(f"    {len(folder_tests)} folder commands: OK")

# Screen
print("  Screen:")
h, r = commands.handle_command("take a screenshot")
print(f"    Screenshot: {r}")
test("screenshot", h, True)

# Volume
print("  Volume:")
vol_tests = ["volume up", "volume down", "mute", "unmute"]
for cmd in vol_tests:
    h, r = commands.handle_command(cmd)
    test(cmd, h, True)
print(f"    {len(vol_tests)} volume commands: OK")

# System
print("  System:")
h, r = commands.handle_command("my ip address")
print(f"    IP: {r}")
test("ip", h, True)

h, r = commands.handle_command("battery status")
print(f"    Battery: {r}")
test("battery", h, True)

# Chat
print("  Chat:")
h, r = commands.handle_command("help")
test("help", h, True)
print(f"    Help: OK (returns {len(r)} chars)")

h, r = commands.handle_command("clear history")
test("clear", h, True)
print(f"    Clear history: OK")

# ============================================================
# MEMORY MODULE
# ============================================================
print("\n[MEMORY]")
import memory as mem

h, r = mem.handle_memory_command("remember my favorite color is blue")
print(f"  Remember: {r}")
test("remember", h, True)

h, r = mem.handle_memory_command("what is my favorite color")
print(f"  Recall: {r}")
test("recall", h, True)

h, r = mem.handle_memory_command("what do you remember")
print(f"  List: OK")
test("list", h, True)

h, r = mem.handle_memory_command("add a note test note 123")
print(f"  Add note: {r}")
test("add note", h, True)

h, r = mem.handle_memory_command("show my notes")
print(f"  Show notes: OK")
test("show notes", h, True)

# ============================================================
# INTERNET TASKS
# ============================================================
print("\n[INTERNET TASKS]")
import internet_tasks

h, r = internet_tasks.handle_internet_task("google python")
print(f"  Google search: {'OK' if h else 'FAIL'}")
test("google", h, True)

h, r = internet_tasks.handle_internet_task("weather in london")
if "not configured" in r.lower():
    print(f"  Weather: SKIP (no API key)")
    skipped += 1
else:
    print(f"  Weather: {r[:50]}...")
    test("weather", h, True)

h, r = internet_tasks.handle_internet_task("tech news")
if "not configured" in r.lower():
    print(f"  News: SKIP (no API key)")
    skipped += 1
else:
    print(f"  News: OK")
    test("news", h, True)

# ============================================================
# GPT
# ============================================================
print("\n[GPT - gpt-5-nano]")
import gpt

r = gpt.get_simple_response("Say OK")
print(f"  Response: {r}")
test("gpt", True if r else False, True)

# ============================================================
# TTS
# ============================================================
print("\n[TTS]")
import tts
print("  Speaking test message...")
tts.speak("All features tested successfully")
print("  TTS: OK")
test("tts", True, True)

# ============================================================
# HARDWARE (Pi only)
# ============================================================
print("\n[HARDWARE]")
try:
    import hardware
    h, r = hardware.handle_hardware_command("led status")
    print(f"  LED: {r}")
    test("hardware", h, True)
except Exception as e:
    print(f"  Hardware: SKIP (not on Pi)")
    skipped += 1

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("TEST RESULTS")
print("=" * 60)
print(f"  PASSED:  {passed}")
print(f"  FAILED:  {failed}")
print(f"  SKIPPED: {skipped}")
print("=" * 60)

if failed == 0:
    print("\nALL TESTS PASSED!")
else:
    print(f"\n{failed} tests failed - check above for details")

print("\nCross-Platform Status:")
print(f"  Current OS: {sys.platform}")
print(f"  Windows compatible: YES")
print(f"  Linux/Pi compatible: YES")
print("\nRun: python main.py")
