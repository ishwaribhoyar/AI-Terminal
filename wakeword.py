# wakeword.py - Wake Word Detection for IVERI AI
# Falls back to keyboard activation if Picovoice is unavailable

import os
import time

try:
    import config
    ACCESS_KEY = getattr(config, 'PICOVOICE_ACCESS_KEY', '') or os.getenv('PICOVOICE_ACCESS_KEY', '')
except Exception:
    ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY', '')

# Check if Porcupine is available
PORCUPINE_AVAILABLE = False
try:
    import pvporcupine
    from pvrecorder import PvRecorder
    PORCUPINE_AVAILABLE = True
except ImportError:
    pass


class WakeWordDetector:
    """Wake word detection using Porcupine"""
    
    def __init__(self, custom_keyword_path=None):
        self.porcupine = None
        self.recorder = None
        self.use_keyboard = False
        
        # Check if we should use keyboard fallback
        if not PORCUPINE_AVAILABLE:
            print("INFO: Porcupine not installed. Using keyboard activation.")
            self.use_keyboard = True
            return
            
        if not ACCESS_KEY or ACCESS_KEY.startswith('your') or len(ACCESS_KEY) < 20:
            print("INFO: No Picovoice key configured. Using keyboard activation (Press ENTER to talk).")
            self.use_keyboard = True
            return
        
        try:
            if custom_keyword_path and os.path.exists(custom_keyword_path):
                self.porcupine = pvporcupine.create(
                    access_key=ACCESS_KEY,
                    keyword_paths=[custom_keyword_path]
                )
                print("Using custom wake word file.")
            else:
                self.porcupine = pvporcupine.create(
                    access_key=ACCESS_KEY,
                    keywords=["jarvis"]
                )
                print("Using wake word: 'Jarvis' (say 'Jarvis' to activate IVERI)")
            
            self.recorder = PvRecorder(
                device_index=-1,
                frame_length=self.porcupine.frame_length
            )
            
        except Exception as e:
            print(f"Wake word init failed: {e}")
            print("INFO: Falling back to keyboard activation")
            self.use_keyboard = True
            self.cleanup()
    
    def listen_for_wake_word(self):
        """Listen for wake word or keyboard input"""
        
        if self.use_keyboard:
            print("\n>>> Press ENTER to speak to IVERI (or type 'quit' to exit)...")
            try:
                user_input = input()
                if user_input.lower().strip() in ['quit', 'exit', 'q']:
                    return False
                return True
            except (KeyboardInterrupt, EOFError):
                return False
        
        # Porcupine wake word detection
        print("Waiting for wake word... Say 'Jarvis' to activate IVERI")
        try:
            self.recorder.start()
            while True:
                pcm = self.recorder.read()
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    print("Wake word detected!")
                    return True
                
                time.sleep(0.01)
                    
        except KeyboardInterrupt:
            return False
        except Exception as e:
            print(f"Wake word listening error: {e}")
            return False
        finally:
            try:
                if self.recorder:
                    self.recorder.stop()
            except Exception:
                pass
    
    def cleanup(self):
        """Release resources safely"""
        try:
            if self.recorder:
                self.recorder.stop()
        except Exception:
            pass
        
        try:
            if self.porcupine:
                self.porcupine.delete()
        except Exception:
            pass
        
        self.porcupine = None
        self.recorder = None


# Global detector instance
_detector = None


def wait_for_wake_word(custom_keyword_path=None):
    """Wait until wake word is detected or Enter is pressed"""
    global _detector
    
    try:
        if _detector is None:
            _detector = WakeWordDetector(custom_keyword_path=custom_keyword_path)
        
        return _detector.listen_for_wake_word()
        
    except Exception as e:
        print(f"Wake word error: {e}")
        # Fallback to keyboard
        print("\n>>> Press ENTER to speak to IVERI...")
        try:
            input()
            return True
        except Exception:
            return False


def cleanup():
    """Clean up wake word detector resources"""
    global _detector
    if _detector:
        _detector.cleanup()
        _detector = None


def is_using_keyboard():
    """Check if we're using keyboard activation"""
    global _detector
    return _detector is None or _detector.use_keyboard
