import serial
import time

class SerialDataReader:
    def __init__(self):
        #74124 74105
        self.serial_data = {}
        self.timeout_duration = 0.5

        self.ser = serial.Serial(
            port='/dev/serial0',
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        """self.serial_data[74124] = {
            "battery_voltage": 2.95,
            "learn_status": True,
            "battery_low_voltage": False,
            "rssi": 236,
            "last_input_statuses": [{
            "Up": 0,
            "Down": 1,
            "Idle": 0
            },{
            "Up": 0,
            "Down": 0,
            "Idle": 0
            }          ],
            "last_input_time": time.time(),
            "current_state": "Down"
        }"""

    def read_serial_data(self):
        data = self.ser.readline()
        self.check_for_timeouts()
        if len(data) < 8:
            return

        serial_no = int.from_bytes(data[0:3], byteorder='big')
        input_status_byte = data[3]
        battery_voltage = 1.75 + (data[5] * 0.05)
        learn_battery_status = data[6]
        rssi = data[7]

        # Initialize device data if it doesn't exist
        if serial_no not in self.serial_data:
            self.serial_data[serial_no] = {
                "battery_voltage": battery_voltage,
                "learn_status": False,
                "battery_low_voltage": False,
                "rssi": rssi,
                "last_input_statuses": [],
                "last_input_time": time.time(),
                "current_state": "Idle"
            }
        else:
            # Update existing device data
            self.serial_data[serial_no]["battery_voltage"] = battery_voltage
            #self.serial_data[serial_no]['learn_battery_status'] = learn_battery_status
            self.serial_data[serial_no]["rssi"] = rssi
            self.serial_data[serial_no]["last_input_time"] = time.time()

        # Update the input status for the transmitter
        input_status = self.parse_input_status(input_status_byte)
        self.serial_data[serial_no]["last_input_statuses"].append(input_status)

        learn_status, low_battery = self.parse_learn_and_battery_status(learn_battery_status)
        self.serial_data[serial_no]["learn_status"] = bool(learn_status)
        self.serial_data[serial_no]["battery_low_voltage"] = bool(low_battery)

        # Limit the list to the last two entries
        values_kept = 2 # Increase value if receiver is dropping packets. This will also increase winch control latency
        if len(self.serial_data[serial_no]["last_input_statuses"]) > values_kept:
            self.serial_data[serial_no]["last_input_statuses"].pop(0)

        self.update_device_state(serial_no)

        return self.serial_data
            
    def parse_input_status(self, input_status_byte: bytes):
        input_1 = (input_status_byte & 0x01) >> 0  # Bit 0
        input_2 = (input_status_byte & 0x02) >> 1  # Bit 1
        input_3 = (input_status_byte & 0x04) >> 2  # Bit 2

        inputs_dict = {
            "Up": input_1,
            "Down": input_2,
            "Idle": input_3
            }        
        return inputs_dict
        
    def update_device_state(self, serial_no: int):  
        last_input_statuses = self.serial_data[serial_no]["last_input_statuses"]
        
        #Set state to first true value found in last input statuses
        for status in last_input_statuses:
            for label, value in status.items():
                if value:
                    self.serial_data[serial_no]['current_state'] = label
                    return

        # If no true values are found set state to Idle
        self.serial_data[serial_no]['current_state'] = "Idle"

    def check_for_timeouts(self):
        for values in self.serial_data.values():
            if time.time() - values["last_input_time"] > self.timeout_duration:
                values["current_state"] = "TimedOut"

    def parse_learn_and_battery_status(self, learn_battery_status_byte: bytes):
        # Extract the bits
        low_battery = (learn_battery_status_byte & 0x01) >> 0  # Bit 0
        learn_status = (learn_battery_status_byte & 0x02) >> 1  # Bit 1
        #print(f"battery:{low_battery} learn:{learn_status}")
        return learn_status, low_battery
