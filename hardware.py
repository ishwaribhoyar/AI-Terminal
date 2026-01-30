# hardware.py - GPIO Hardware Control for IVERI AI
# NOTE: This module only works on Raspberry Pi with GPIO pins

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️ RPi.GPIO not available. Hardware control disabled.")

import time

# GPIO Pin Definitions (adjust based on your wiring)
LED_PIN = 17          # GPIO 17 (Pin 11) for LED
BUTTON_PIN = 27       # GPIO 27 (Pin 13) for button (optional)
BUZZER_PIN = 22       # GPIO 22 (Pin 15) for buzzer (optional)

# Initialize GPIO if available
if GPIO_AVAILABLE:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)


class HardwareController:
    """Control GPIO hardware components"""
    
    def __init__(self):
        self.led_state = False
    
    def led_on(self):
        """Turn LED on"""
        if not GPIO_AVAILABLE:
            return "Hardware control not available on this system."
        
        GPIO.output(LED_PIN, GPIO.HIGH)
        self.led_state = True
        return "LED is now on."
    
    def led_off(self):
        """Turn LED off"""
        if not GPIO_AVAILABLE:
            return "Hardware control not available on this system."
        
        GPIO.output(LED_PIN, GPIO.LOW)
        self.led_state = False
        return "LED is now off."
    
    def led_toggle(self):
        """Toggle LED state"""
        if self.led_state:
            return self.led_off()
        else:
            return self.led_on()
    
    def led_blink(self, times=3, interval=0.5):
        """
        Blink LED multiple times.
        
        Args:
            times: Number of blinks
            interval: Time between blinks in seconds
        """
        if not GPIO_AVAILABLE:
            return "Hardware control not available on this system."
        
        for _ in range(times):
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(interval)
        
        return f"LED blinked {times} times."
    
    def get_led_status(self):
        """Get current LED status"""
        status = "on" if self.led_state else "off"
        return f"The LED is currently {status}."
    
    def cleanup(self):
        """Clean up GPIO on exit - with safety wrapper"""
        try:
            if GPIO_AVAILABLE:
                GPIO.cleanup()
        except Exception as e:
            print(f"GPIO cleanup warning: {e}")


# Global controller instance
hw = HardwareController()


def handle_hardware_command(user_input):
    """
    Handle hardware-related commands.
    
    Args:
        user_input: User's spoken text
    
    Returns:
        tuple: (handled: bool, response: str)
    """
    text = user_input.lower()
    
    # LED Commands
    if 'led' in text or 'light' in text:
        if 'on' in text or 'turn on' in text:
            return True, hw.led_on()
        
        if 'off' in text or 'turn off' in text:
            return True, hw.led_off()
        
        if 'blink' in text:
            return True, hw.led_blink()
        
        if 'toggle' in text:
            return True, hw.led_toggle()
        
        if 'status' in text:
            return True, hw.get_led_status()
    
    return False, None


def cleanup():
    """Clean up hardware resources"""
    hw.cleanup()


# Wiring Reference:
# -----------------
# LED Circuit:
#   GPIO 17 (Pin 11) → 330Ω Resistor → LED Anode (+)
#   LED Cathode (-) → GND (Pin 6)
#
# Button Circuit:
#   GPIO 27 (Pin 13) → Button → GND
#   (Use internal pull-up in code)
#
# Buzzer Circuit:
#   GPIO 22 (Pin 15) → Buzzer (+)
#   Buzzer (-) → GND
