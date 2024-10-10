from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

class WinchController:
    def __init__(self):
        self.winch_state = "Idle" # Up, Down, Idle
        self.current_value = -1
        self.timeout_duration = 0.5  # Timeout duration in seconds
        self.last_input_time = 0

        factory = PiGPIOFactory()
        self.winch = Servo(21, initial_value=self.current_value, pin_factory=factory)

    def rotate_winch(self):
        if self.winch_state == "Up":
            self.winch.value = 1
        elif self.winch_state == "Down":
            self.winch.value = -1
        else:
            self.winch.detach()

    def handle_state(self, serial_data: dict):
        up_count = 0
        down_count = 0

        if not serial_data:
            self.winch_state = "Idle" 
            return
        
        for data in serial_data.values():
            state = data["current_state"]
            transmitter_is_paired = data["learn_status"]
            if state == "Up" and transmitter_is_paired:
                up_count += 1
            elif state == "Down" and transmitter_is_paired:
                down_count += 1

        if up_count > 0 and down_count == 0:
            self.winch_state = "Up"
        elif down_count > 0 and up_count == 0:
            self.winch_state = "Down"
        else:
            self.winch_state = "Idle"
