from gpio_controller import GPIO_CONTROLLER, PINS
from time import sleep


def test():
    controller = GPIO_CONTROLLER()
    for pin in PINS:
        print(f"Testing pin {pin}({pin.value})")
        for _ in range(10):
            controller.toggle_pin(pin)
            sleep(0.5)


if __name__ == "__main__":
    test()
