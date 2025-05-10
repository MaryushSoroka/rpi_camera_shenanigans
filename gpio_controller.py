from enum import Enum
import gpiod
from gpiod.line import Direction, Value


class PINS(Enum):
    LEFT = 14
    RIGHT = 15
    TOP = 18
    BOTTOM = 23
    CAMERA = 24


class GPIO_CONTROLLER:
    def __init__(self):
        # Initialize all pins to INACTIVE aka False
        self.pin_states = {pin_num: False for pin_num in PINS}
        self.lines = gpiod.request_lines(
            "/dev/gpiochip0",
            config={l.value: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE) for l in PINS}
        )

    def toggle_pin(self, pin_num):
        assert pin_num in PINS
        old_state = self.pin_states[pin_num]
        self.lines.set_value(pin_num.value, Value.INACTIVE if old_state else Value.ACTIVE)
        print(f"Toggle gpio {pin_num}({pin_num.value}): {old_state}->{not old_state}")
        self.pin_states[pin_num] = not old_state

    def __del__(self):
        self.lines.release()
