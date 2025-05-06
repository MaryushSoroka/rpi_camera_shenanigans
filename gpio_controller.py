from enum import Enum
import RPi.GPIO as GPIO

class PINS(Enum):
    LEFT = 14
    RIGHT = 15
    TOP = 18
    BOTTOM = 23
    CAMERA = 24

class GPIO_CONTROLLER:
    def __init__(self):
        # Initialize all pins to GPIO.LOW aka False
        self.pin_states = {pin_num: False for pin_num in PINS}
        GPIO.setmode(GPIO.BOARD)
        for pin_num in PINS:
            GPIO.setup(pin_num, GPIO.OUT, initial=GPIO.LOW)

    def toggle_pin(self, pin_num):
        assert pin_num in PINS
        old_state = self.pin_states[pin_num]
        GPIO.output(pin_num, GPIO.LOW if old_state else GPIO.HIGH)
        print(f"Toggle gpio {pin_num}({pin_num.value}): {old_state}->{not old_state}")
        self.pin_states[pin_num] = not old_state
