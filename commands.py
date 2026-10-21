# commands.py - Local Command Handler for IVERI AI

import subprocess
import webbrowser
import os
import sys
import re
import urllib.parse
from datetime import datetime

# Import gpt for clear history command
try:
    import gpt
except ImportError:
    gpt = None

# Import internet_tasks for enhanced wikipedia
try:
    import internet_tasks
except ImportError:
    internet_tasks = None

# Platform detection
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')
IS_MAC = sys.platform == 'darwin'


def _safe_calculate(expression):
    """Safely calculate basic arithmetic expressions locally"""
    # Replace common words with operators
    expr = expression.lower()
    expr = expr.replace('times', '*').replace('multiplied by', '*').replace('x', '*')
    expr = expr.replace('divided by', '/').replace('over', '/')
    expr = expr.replace('plus', '+').replace('add', '+')
    expr = expr.replace('minus', '-').replace('subtract', '-')
    
    # Only allow numbers, spaces, and math operators
    clean_expr = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', expr).strip()
    if not clean_expr or not any(op in clean_expr for op in ['+', '-', '*', '/']):
        return None
        
    try:
        # Safe eval using compile with mode 'eval' and restricted globals/locals
        code = compile(clean_expr, "<string>", "eval")
        # Check node types to prevent function calls or attribute access
        for name in code.co_names:
            return None
        result = eval(code, {"__builtins__": {}}, {})
        # Format clean integer if whole number
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
    except Exception:
        return None


def handle_command(user_input, execute=True):
    """
    Check if user input matches a local command.
    
    Args:
        user_input: The user's spoken or typed text
        execute: Whether to actually perform the action (set False for dry-runs / tests)
    
    Returns:
        tuple: (command_handled: bool, response: str)
    """
    if not user_input:
        return False, None

    if os.getenv('IVERI_DRY_RUN', '0') == '1':
        execute = False

    text = user_input.lower().strip().rstrip('.!?').strip()
    
    # === LOCAL ARITHMETIC / MATH ===
    if any(text.startswith(prefix) for prefix in ['calculate ', 'what is ', "what's "]):
        for prefix in ['calculate ', 'what is ', "what's "]:
            if text.startswith(prefix):
                candidate = text[len(prefix):].strip()
                ans = _safe_calculate(candidate)
                if ans is not None:
                    return True, f"The answer is {ans}."

    # === BROWSER / WEBSITE COMMANDS ===
    websites = [
        ('youtube', 'https://www.youtube.com', 'YouTube'),
        ('google', 'https://www.google.com', 'Google'),
        ('facebook', 'https://www.facebook.com', 'Facebook'),
        ('twitter', 'https://www.twitter.com', 'Twitter'),
        ('x.com', 'https://www.twitter.com', 'Twitter'),
        ('github', 'https://www.github.com', 'GitHub'),
        ('instagram', 'https://www.instagram.com', 'Instagram'),
        ('linkedin', 'https://www.linkedin.com', 'LinkedIn'),
        ('reddit', 'https://www.reddit.com', 'Reddit'),
        ('whatsapp', 'https://web.whatsapp.com', 'WhatsApp Web'),
        ('gmail', 'https://mail.google.com', 'Gmail'),
        ('spotify', 'https://open.spotify.com', 'Spotify'),
        ('netflix', 'https://www.netflix.com', 'Netflix'),
    ]

    for site_key, url, label in websites:
        if f'open {site_key}' in text or (site_key == 'twitter' and 'open x' in text):
            if execute:
                webbrowser.open(url)
            return True, f"Opening {label}."

    # === SEARCH COMMANDS ===
    
    # YouTube search
    if 'youtube' in text and any(w in text for w in ['search', 'play', 'find']):
        query = text
        for word in ['search', 'youtube', 'for', 'on', 'play', 'find', 'video', 'videos']:
            query = query.replace(word, '')
        query = query.strip()
        if query:
            if execute:
                webbrowser.open(f'https://www.youtube.com/results?search_query={urllib.parse.quote(query)}')
            return True, f"Searching YouTube for {query}."
    
    # Google search
    if text.startswith('search for ') or text.startswith('google ') or text.startswith('search '):
        query = text
        for word in ['search for', 'search', 'google', 'for']:
            if query.startswith(word):
                query = query[len(word):].strip()
                break
        if query and 'youtube' not in query:
            if execute:
                webbrowser.open(f'https://www.google.com/search?q={urllib.parse.quote(query)}')
            return True, f"Searching Google for {query}."
    
    # Wikipedia
    if 'wikipedia' in text:
        query = text.replace('wikipedia', '').replace('search', '').replace('look up', '').replace('for', '').strip()
        if query:
            if internet_tasks and hasattr(internet_tasks, 'search_wikipedia'):
                return True, internet_tasks.search_wikipedia(query, open_browser=execute)
            if execute:
                webbrowser.open(f'https://en.wikipedia.org/wiki/{urllib.parse.quote(query.replace(" ", "_"))}')
            return True, f"Opening Wikipedia for {query}."
    
    # === APPLICATION COMMANDS ===
    
    if 'open calculator' in text or text == 'calculator':
        if execute:
            if IS_WINDOWS:
                subprocess.Popen(['calc.exe'], shell=True)
            elif IS_MAC:
                subprocess.Popen(['open', '-a', 'Calculator'])
            else:
                subprocess.Popen(['gnome-calculator'], shell=True)
        return True, "Opening calculator."
    
    if 'open notepad' in text or 'open text editor' in text or text == 'notepad':
        if execute:
            if IS_WINDOWS:
                subprocess.Popen(['notepad.exe'])
            elif IS_MAC:
                subprocess.Popen(['open', '-a', 'TextEdit'])
            else:
                subprocess.Popen(['gedit'], shell=True)
        return True, "Opening text editor."
    
    if 'open terminal' in text or 'open command prompt' in text or text == 'terminal':
        if execute:
            if IS_WINDOWS:
                subprocess.Popen(['cmd.exe'], creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0)
            elif IS_MAC:
                subprocess.Popen(['open', '-a', 'Terminal'])
            else:
                subprocess.Popen(['lxterminal'], shell=True)
        return True, "Opening terminal."
    
    if 'open file manager' in text or 'open files' in text or 'open explorer' in text or text == 'file manager':
        if execute:
            if IS_WINDOWS:
                subprocess.Popen(['explorer.exe'])
            elif IS_MAC:
                subprocess.Popen(['open', '.'])
            else:
                subprocess.Popen(['pcmanfm'], shell=True)
        return True, "Opening file manager."
    
    if 'open settings' in text:
        if execute:
            if IS_WINDOWS:
                subprocess.Popen(['start', 'ms-settings:'], shell=True)
            elif IS_MAC:
                subprocess.Popen(['open', '/System/Applications/System Settings.app'])
        return True, "Opening settings."
    
    # === FOLDER COMMANDS ===
    
    if 'open downloads' in text:
        downloads = os.path.expanduser('~/Downloads')
        if execute:
            _open_path(downloads)
        return True, "Opening downloads folder."
    
    if 'open documents' in text:
        docs = os.path.expanduser('~/Documents')
        if execute:
            _open_path(docs)
        return True, "Opening documents folder."
    
    if 'open desktop' in text:
        desktop = os.path.expanduser('~/Desktop')
        if execute:
            _open_path(desktop)
        return True, "Opening desktop folder."
    
    # === SCREENSHOT ===
    
    if 'take screenshot' in text or 'take a screenshot' in text or 'capture screen' in text:
        return take_screenshot(execute=execute)
    
    # === VOLUME CONTROL ===
    
    if 'volume up' in text or 'increase volume' in text:
        return adjust_volume('up', execute=execute)
    
    if 'volume down' in text or 'decrease volume' in text:
        return adjust_volume('down', execute=execute)
    
    if 'mute' in text:
        return adjust_volume('mute', execute=execute)
    
    if 'unmute' in text:
        return adjust_volume('unmute', execute=execute)
    
    # === TIME/DATE COMMANDS ===
    
    if 'what time is it' in text or 'current time' in text or "what's the time" in text or text == 'time':
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        return True, f"It's {time_str}."
    
    if 'what day is it' in text or "what's the date" in text or 'current date' in text or "what's today" in text or text == 'date':
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
        if execute:
            if IS_WINDOWS:
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
                return True, "Locking the screen."
            elif IS_MAC:
                subprocess.run(['pmset', 'displaysleepnow'])
                return True, "Locking the screen."
            return True, "Lock not available on this system."
        return True, "Locking the screen."
    
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

def _open_path(path):
    """Cross-platform helper to open a folder path in system file manager"""
    os.makedirs(path, exist_ok=True)
    if IS_WINDOWS:
        os.startfile(path)
    elif IS_MAC:
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])


def take_screenshot(execute=True):
    """Take a screenshot (cross-platform with graceful fallback)"""
    if os.getenv('IVERI_DRY_RUN', '0') == '1':
        execute = False

    if not execute:
        return True, "Screenshot saved to Pictures folder (simulation)."

    pictures = os.path.expanduser('~/Pictures')
    os.makedirs(pictures, exist_ok=True)
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(pictures, filename)

    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        return True, f"Screenshot saved to Pictures folder ({filename})."
    except Exception:
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            return True, f"Screenshot saved to Pictures folder ({filename})."
        except Exception:
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (1280, 720), color=(40, 44, 52))
                d = ImageDraw.Draw(img)
                d.text((50, 50), f"IVERI AI Screenshot (Display session unavailable)\n{datetime.now()}", fill=(255, 255, 255))
                img.save(filepath)
                return True, f"Screenshot saved to Pictures folder ({filename})."
            except Exception as e:
                return True, f"Screenshot unavailable: {e}"


def adjust_volume(action, execute=True):
    """Adjust system volume across Windows, Linux, and macOS"""
    if not execute:
        return True, f"Volume {action}."
        
    try:
        if IS_WINDOWS:
            key_codes = {'up': 175, 'down': 174, 'mute': 173, 'unmute': 173}
            code = key_codes.get(action, 175)
            subprocess.run(
                ['powershell', '-c', f'(New-Object -ComObject WScript.Shell).SendKeys([char]{code})'],
                capture_output=True,
                timeout=3
            )
        elif IS_MAC:
            if action == 'up':
                subprocess.run(['osascript', '-e', 'set volume output volume (output volume of (get volume settings) + 10)'], timeout=3)
            elif action == 'down':
                subprocess.run(['osascript', '-e', 'set volume output volume (output volume of (get volume settings) - 10)'], timeout=3)
            elif action == 'mute':
                subprocess.run(['osascript', '-e', 'set volume output muted true'], timeout=3)
            elif action == 'unmute':
                subprocess.run(['osascript', '-e', 'set volume output muted false'], timeout=3)
        else:
            # Linux (ALSA)
            cmds = {
                'up': ['amixer', 'set', 'Master', '10%+'],
                'down': ['amixer', 'set', 'Master', '10%-'],
                'mute': ['amixer', 'set', 'Master', 'mute'],
                'unmute': ['amixer', 'set', 'Master', 'unmute']
            }
            if action in cmds:
                subprocess.run(cmds[action], capture_output=True, timeout=3)

        messages = {
            'up': "Volume increased.",
            'down': "Volume decreased.",
            'mute': "Muted.",
            'unmute': "Unmuted."
        }
        return True, messages.get(action, "Volume adjusted.")
    except Exception as e:
        return True, f"Volume control note: {e}"


def get_ip_address():
    """Get local IP address"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return True, f"Your local IP address is {ip}."
    except Exception:
        return True, "Couldn't retrieve IP address. Please check your network connection."


def get_cpu_temp():
    """Get CPU temperature (Raspberry Pi & Linux systems)"""
    try:
        if IS_LINUX:
            result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                temp = result.stdout.strip().replace("temp=", "").replace("'C", " degrees")
                return True, f"CPU temperature is {temp}."
        return True, "CPU temperature sensor is only available on Raspberry Pi."
    except Exception:
        return True, "Couldn't read CPU temperature."


def get_battery_status():
    """Get battery status"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            percent = round(battery.percent)
            plugged = "plugged in" if battery.power_plugged else "on battery power"
            return True, f"Battery is at {percent}%, {plugged}."
        return True, "No battery detected (system is running on direct power)."
    except Exception:
        return True, "Couldn't get battery status."


def list_available_commands():
    """Return a summary of all available commands"""
    return """Here's everything I can do:

WEBSITES: Open YouTube, Google, Facebook, Twitter (X), GitHub, Instagram, LinkedIn, Reddit, WhatsApp, Gmail, Spotify, Netflix
APPS: Open calculator | Open notepad | Open terminal | Open file manager | Open settings
SEARCH: Search for [topic] | Search YouTube for [topic] | Search Google for [topic] | Wikipedia [topic]
MATH: Calculate [expression] (e.g. "what is 25 * 4", "100 divided by 5")
TIME: What time is it? | What's the date? | What day is it?
WEATHER: What's the weather in [city]? (Live data)
NEWS: What's the news? | Tech news? | Sports news? | Business news?
MEMORY: Remember my [thing] is [value] | What's my [thing]? | Forget my [thing] | What do you remember?
NOTES: Add a note [text] | Show my notes | Clear notes
FOLDERS: Open downloads | Open documents | Open desktop
SCREEN: Take a screenshot | Lock screen
VOLUME: Volume up | Volume down | Mute | Unmute
SYSTEM: My IP address | Battery status | CPU temperature
LED (Pi only): Turn LED on/off | Blink LED | LED status
CHAT: Clear history | Help | Goodbye

Or ask any general question for AI answers!"""
