#!/usr/bin/env python3
"""Quick debug test - speaks your command and shows what happens"""

from dotenv import load_dotenv
load_dotenv()

import speech
import commands

print("=" * 40)
print("IVERI VOICE DEBUG TEST")
print("=" * 40)
print("Speak a command (like 'open calculator')...")
print()

# Listen
text = speech.listen()

if not text:
    print("ERROR: Didn't capture any audio")
else:
    print(f"You said: '{text}'")
    print(f"Lowercase: '{text.lower()}'")
    print()
    
    # Test command
    handled, response = commands.handle_command(text)
    print(f"Command handled: {handled}")
    print(f"Response: {response}")
    
    if not handled:
        print()
        print("Command NOT recognized!")
        print("Try saying exactly: 'open calculator'")
