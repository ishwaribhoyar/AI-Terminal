#!/usr/bin/env python3
"""Test specific features requested by user"""

from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("IVERI FEATURE CHECK")
print("=" * 50)

import commands
import memory as mem
import internet_tasks

# 1. TIME
print("\n[TIME]")
h, r = commands.handle_command("what time is it")
print(f"  Time: {r}")
h, r = commands.handle_command("what day is it")
print(f"  Date: {r}")

# 2. WEATHER
print("\n[WEATHER]")
h, r = internet_tasks.handle_internet_task("weather in london")
print(f"  Weather: {r[:80]}...")

# 3. MEMORY
print("\n[MEMORY]")
h, r = mem.handle_memory_command("remember my pet is dog")
print(f"  Remember: {r}")
h, r = mem.handle_memory_command("what is my pet")
print(f"  Recall: {r}")

# 4. SEARCH
print("\n[SEARCH]")
h, r = commands.handle_command("search for python")
print(f"  Google: {r}")
h, r = commands.handle_command("search youtube for music")
print(f"  YouTube: {r}")
h, r = commands.handle_command("wikipedia python")
print(f"  Wikipedia: {r}")

# 5. APPS
print("\n[APPS]")
h, r = commands.handle_command("open calculator")
print(f"  Calculator: {r}")
h, r = commands.handle_command("open notepad")
print(f"  Notepad: {r}")

# 6. SCREEN
print("\n[SCREEN]")
h, r = commands.handle_command("take a screenshot")
print(f"  Screenshot: {r}")

# 7. VOLUME
print("\n[VOLUME]")
h, r = commands.handle_command("volume up")
print(f"  Volume up: {r}")
h, r = commands.handle_command("mute")
print(f"  Mute: {r}")

# 8. SYSTEM
print("\n[SYSTEM]")
h, r = commands.handle_command("my ip address")
print(f"  IP: {r}")
h, r = commands.handle_command("battery status")
print(f"  Battery: {r}")

print("\n" + "=" * 50)
print("ALL FEATURES CHECKED!")
print("=" * 50)
