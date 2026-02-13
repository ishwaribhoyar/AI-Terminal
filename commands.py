# commands.py - Local Command Handler for IVERI AI

import subprocess
import webbrowser
import os
import sys
from datetime import datetime

# Import gpt for clear history command
try:
    import gpt
except ImportError:
    gpt = None

# Platform detection
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')


def handle_command(user_input):
    """
    Check if user input matches a local command.
    
    Args:
        user_input: The user's spoken text
    
    Returns:
        tuple: (command_handled: bool, response: str)
    """
    text = user_input.lower().strip()
    
    # === BROWSER COMMANDS ===
    
    if 'open youtube' in text:
        webbrowser.open('https://www.youtube.com')
        return True, "Opening YouTube."
    
    if 'open google' in text:
        webbrowser.open('https://www.google.com')
        return True, "Opening Google."
    
    if 'open facebook' in text:
        webbrowser.open('https://www.facebook.com')
        return True, "Opening Facebook."
    
    if 'open twitter' in text or 'open x' in text:
        webbrowser.open('https://www.twitter.com')
        return True, "Opening Twitter."
    
    if 'open github' in text:
        webbrowser.open('https://www.github.com')
        return True, "Opening GitHub."
    
    if 'open instagram' in text:
        webbrowser.open('https://www.instagram.com')
        return True, "Opening Instagram."
    
    if 'open linkedin' in text:
        webbrowser.open('https://www.linkedin.com')
        return True, "Opening LinkedIn."
    
    if 'open reddit' in text:
        webbrowser.open('https://www.reddit.com')
        return True, "Opening Reddit."
    
    if 'open whatsapp' in text:
        webbrowser.open('https://web.whatsapp.com')
        return True, "Opening WhatsApp Web."
    
    if 'open gmail' in text:
        webbrowser.open('https://mail.google.com')
        return True, "Opening Gmail."
    
    if 'open spotify' in text:
        webbrowser.open('https://open.spotify.com')
        return True, "Opening Spotify."
    
    if 'open netflix' in text:
        webbrowser.open('https://www.netflix.com')
        return True, "Opening Netflix."
    
    # === SEARCH COMMANDS ===
    
    # YouTube search - multiple patterns
    if 'youtube' in text and ('search' in text or 'play' in text or 'find' in text):
        # Extract query - remove common words
        query = text
        for word in ['search', 'youtube', 'for', 'on', 'play', 'find', 'video', 'videos']:
            query = query.replace(word, '')
        query = query.strip()
        if query:
            import urllib.parse
            webbrowser.open(f'https://www.youtube.com/results?search_query={urllib.parse.quote(query)}')
            return True, f"Searching YouTube for {query}."
    
    # Google search - multiple patterns
    if text.startswith('search for ') or text.startswith('google ') or text.startswith('search '):
        query = text
        for word in ['search for', 'search', 'google', 'for']:
            query = query.replace(word, '', 1)
        query = query.strip()
        if query and 'youtube' not in query:
            import urllib.parse
            webbrowser.open(f'https://www.google.com/search?q={urllib.parse.quote(query)}')
            return True, f"Searching Google for {query}."
    
    # Wikipedia
    if 'wikipedia' in text:
        query = text.replace('wikipedia', '').replace('search', '').replace('look up', '').strip()
        if query:
            webbrowser.open(f'https://en.wikipedia.org/wiki/{query.replace(" ", "_")}')
            return True, f"Opening Wikipedia for {query}."
    
    # === APPLICATION COMMANDS ===
    
    if 'open calculator' in text or 'calculator' in text:
        print(f"[DEBUG] Calculator command detected in: '{text}'")
        if IS_WINDOWS:
            os.system('calc.exe')
        else:
            os.system('gnome-calculator &')
        return True, "Opening calculator."
    
    if 'open notepad' in text or 'open text editor' in text or 'notepad' in text:
        print(f"[DEBUG] Notepad command detected in: '{text}'")
        if IS_WINDOWS:
            os.system('notepad.exe')
        else:
            os.system('gedit &')
        return True, "Opening text editor."
    
    if 'open terminal' in text or 'open command prompt' in text or 'terminal' in text:
        print(f"[DEBUG] Terminal command detected in: '{text}'")
        if IS_WINDOWS:
            os.system('start cmd.exe')
        else:
            os.system('lxterminal &')
        return True, "Opening terminal."
    
    if 'open file manager' in text or 'open files' in text or 'open explorer' in text or 'file manager' in text:
        print(f"[DEBUG] File manager command detected in: '{text}'")
        if IS_WINDOWS:
            os.system('explorer.exe')
        else:
            os.system('pcmanfm &')
        return True, "Opening file manager."
    
    if 'open settings' in text:
        if IS_WINDOWS:
            os.system('start ms-settings:')
        return True, "Opening settings."
    
    # === FOLDER COMMANDS ===
    
    if 'open downloads' in text:
        downloads = os.path.expanduser('~/Downloads')
        if IS_WINDOWS:
            os.startfile(downloads)
        else:
            subprocess.Popen(['xdg-open', downloads])
        return True, "Opening downloads folder."
    
    if 'open documents' in text:
        docs = os.path.expanduser('~/Documents')
        if IS_WINDOWS:
            os.startfile(docs)
        else:
            subprocess.Popen(['xdg-open', docs])
        return True, "Opening documents folder."
    
    if 'open desktop' in text:
        desktop = os.path.expanduser('~/Desktop')
        if IS_WINDOWS:
            os.startfile(desktop)
        else:
            subprocess.Popen(['xdg-open', desktop])
        return True, "Opening desktop folder."
    
    # === SCREENSHOT ===
    
    if 'take screenshot' in text or 'take a screenshot' in text or 'capture screen' in text:
        return take_screenshot()
    
    # === VOLUME CONTROL ===
    
    if 'volume up' in text or 'increase volume' in text:
        return adjust_volume('up')
    
    if 'volume down' in text or 'decrease volume' in text:
        return adjust_volume('down')
    
    if 'mute' in text:
        return adjust_volume('mute')
    
    if 'unmute' in text:
        return adjust_volume('unmute')
    
    # === TIME/DATE COMMANDS ===
    
    if 'what time is it' in text or 'current time' in text or "what's the time" in text:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        return True, f"It's {time_str}."
    
    if 'what day is it' in text or "what's the date" in text or 'current date' in text or "what's today" in text:
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return True, f"Today is {date_str}."
    
    # === SYSTEM INFO COMMANDS ===
    
    if 'ip address' in text or 'my ip' in text:
        return get_ip_address()
    
    if 'cpu temperature' in text or 'temperature' in text:
        return get_cpu_temp()
    
    if 'battery' in text:
        return get_battery_status()
    
    # === SYSTEM CONTROL ===
    
    if 'lock screen' in text or 'lock computer' in text:
        if IS_WINDOWS:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            return True, "Locking the screen."
        return True, "Lock not available on this system."
    
    if 'shutdown' in text or 'shut down' in text:
        return True, "Shutdown disabled for safety. Enable in code if needed."
    
    if 'restart' in text or 'reboot' in text:
        return True, "Restart disabled for safety. Enable in code if needed."
    
    # === CONVERSATION COMMANDS ===
    
    if 'clear history' in text or 'forget everything' in text or 'start fresh' in text:
        if gpt:
            gpt.clear_history()
        return True, "Conversation cleared."
    
    if 'help' in text or 'what can you do' in text:
        return True, list_available_commands()
    
    # === NO COMMAND MATCHED ===
    return False, None


# === HELPER FUNCTIONS ===

def take_screenshot():
    """Take a screenshot (cross-platform)"""
    try:
        import pyautogui
        from datetime import datetime
        
        pictures = os.path.expanduser('~/Pictures')
        os.makedirs(pictures, exist_ok=True)
        
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(pictures, filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        return True, f"Screenshot saved to {filename}"
    except ImportError:
        return True, "Install pyautogui for screenshots: pip install pyautogui"
    except Exception as e:
        return True, f"Screenshot failed: {e}"


def adjust_volume(action):
    """Adjust system volume"""
    try:
        if IS_WINDOWS:
            # Windows volume control using nircmd or PowerShell
            if action == 'up':
                subprocess.run(['powershell', '-c', '(New-Object -ComObject WScript.Shell).SendKeys([char]175)'], capture_output=True)
                return True, "Volume increased."
            elif action == 'down':
                subprocess.run(['powershell', '-c', '(New-Object -ComObject WScript.Shell).SendKeys([char]174)'], capture_output=True)
                return True, "Volume decreased."
            elif action == 'mute':
                subprocess.run(['powershell', '-c', '(New-Object -ComObject WScript.Shell).SendKeys([char]173)'], capture_output=True)
                return True, "Muted."
            elif action == 'unmute':
                subprocess.run(['powershell', '-c', '(New-Object -ComObject WScript.Shell).SendKeys([char]173)'], capture_output=True)
                return True, "Unmuted."
        else:
            # Linux (ALSA)
            if action == 'up':
                subprocess.run(['amixer', 'set', 'Master', '10%+'], capture_output=True)
                return True, "Volume increased."
            elif action == 'down':
                subprocess.run(['amixer', 'set', 'Master', '10%-'], capture_output=True)
                return True, "Volume decreased."
            elif action == 'mute':
                subprocess.run(['amixer', 'set', 'Master', 'mute'], capture_output=True)
                return True, "Muted."
            elif action == 'unmute':
                subprocess.run(['amixer', 'set', 'Master', 'unmute'], capture_output=True)
                return True, "Unmuted."
        return True, "Volume adjusted."
    except Exception as e:
        return True, f"Volume control failed: {e}"


def get_ip_address():
    """Get local IP address"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return True, f"Your IP address is {ip}."
    except:
        return True, "Couldn't get IP address."


def get_cpu_temp():
    """Get CPU temperature (Pi only)"""
    try:
        if IS_LINUX:
            result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            temp = result.stdout.strip().replace("temp=", "").replace("'C", " degrees")
            return True, f"CPU temperature is {temp}."
        return True, "CPU temperature only available on Raspberry Pi."
    except:
        return True, "Couldn't read CPU temperature."


def get_battery_status():
    """Get battery status"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "plugged in" if battery.power_plugged else "on battery"
            return True, f"Battery is at {percent}%, {plugged}."
        return True, "No battery detected."
    except:
        return True, "Couldn't get battery status."


def list_available_commands():
    """Return a summary of all available commands"""
    return """Here's everything I can do:

WEBSITES: Open YouTube, Google, Facebook, Twitter, GitHub, Instagram, LinkedIn, Reddit, WhatsApp, Gmail, Spotify, Netflix

APPS: Open calculator | Open notepad | Open terminal | Open file manager | Open settings

SEARCH: Search for [topic] | Search YouTube for [topic] | Search Google for [topic] | Wikipedia [topic]

TIME: What time is it? | What's the date? | What day is it?

WEATHER: What's the weather in [city]?

NEWS: What's the news? | Tech news? | Sports news? | Business news?

MEMORY: Remember my [thing] is [value] | What's my [thing]? | Forget my [thing] | What do you remember?

NOTES: Add a note [text] | Show my notes | Clear notes

FOLDERS: Open downloads | Open documents | Open desktop

SCREEN: Take a screenshot | Lock screen

VOLUME: Volume up | Volume down | Mute | Unmute

SYSTEM: My IP address | Battery status | CPU temperature

LED (Pi only): Turn LED on/off | Blink LED | LED status

CHAT: Clear history | Help | Goodbye

Or just ask me anything!"""
