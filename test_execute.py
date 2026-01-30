#!/usr/bin/env python3
"""Test actual feature execution"""

import webbrowser
import subprocess
import sys
import os
from datetime import datetime

print("Testing actual feature execution...")
print()

# Test 1: Screenshot
print("[SCREENSHOT]")
try:
    import pyautogui
    pictures = os.path.expanduser("~/Pictures")
    os.makedirs(pictures, exist_ok=True)
    filename = f"test_screenshot_{datetime.now().strftime('%H%M%S')}.png"
    filepath = os.path.join(pictures, filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    exists = os.path.exists(filepath)
    print(f"  Screenshot saved: {exists}")
    print(f"  Path: {filepath}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: YouTube Search
print()
print("[YOUTUBE SEARCH]")
print("  Opening YouTube search for 'python tutorial'...")
result = webbrowser.open("https://www.youtube.com/results?search_query=python+tutorial")
print(f"  Browser opened: {result}")

# Test 3: Google Search  
print()
print("[GOOGLE SEARCH]")
print("  Opening Google search for 'raspberry pi'...")
result = webbrowser.open("https://www.google.com/search?q=raspberry+pi")
print(f"  Browser opened: {result}")

# Test 4: Calculator
print()
print("[CALCULATOR]")
if sys.platform == "win32":
    try:
        subprocess.Popen(["calc.exe"])
        print("  Calculator opened!")
    except Exception as e:
        print(f"  ERROR: {e}")

print()
print("=" * 40)
print("Check: Browser tabs + Calculator + ~/Pictures folder")
print("=" * 40)
