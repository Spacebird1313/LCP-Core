from lcp.core.interfaces.servodriver import ServoDriver
import serial
import time


class PololuDriver(ServoDriver):
    __name = "Pololu Driver"
    __version = "1.0"

    def __init__(self, config):
        super().__init__(self.__name, self.__version)
        self.__serial_port = config.get('serial_port', fallback='/dev/ttyACM0')
        self.__serial_connection = None
        self.__isInitialised = False

    def install(self, modules):
        super().install(modules)

        try:
            self.__serial_connection = serial.Serial(self.__serial_port, 9600, timeout=1)
            self.__serial_connection.close()
            self.__serial_connection.open()
            print("Link to serial port: " + self.__serial_port + " successful")
        except serial.serialutil.SerialException as e:
            raise Exception("Link to serial port: " + self.__serial_port + " failed.", e)

        if not self.__serial_connection.writable():
            self.__serial_connection.close()
            raise Exception("Pololu device is not writable.")

        self.__isInitialised = (self.__serial_connection is not None)
        if self.__isInitialised:
            error_flags = self.get_errors()
            print("Device error status: " + str(error_flags) + ". Flags are cleared...")
        else:
            raise Exception("Pololu driver failed to initialise!")

    def start(self):
        if self.__isInitialised:
            print("Pololu driver is ready")
        else:
            print("Pololu driver failed to initialise!")

    def __write(self, *data):
        if self.__isInitialised:
            for d in data:
                self.__serial_connection.write(d)
            self.__serial_connection.flush()

    def __read(self, num_of_bytes):
        if self.__isInitialised:
            return self.__serial_connection.read(num_of_bytes)
        else:
            return None

    def reset_servos(self):
        self.__write(bytes([0xA2]))

    def set_position(self, servo, value):
        value = value * 4
        posLSB = value & 0x7F
        posMSB = (value >> 7) & 0x7F
        self.__write(bytes([0x84])+bytes([servo])+bytes([posLSB])+bytes([posMSB]))

    def set_speed(self, servo, value):
        speedLSB = value & 0x7F
        speedMSB = (value >> 7) & 0x7F
        self.__write(bytes([0x87])+bytes([servo])+bytes([speedLSB])+bytes([speedMSB]))

    def set_acceleration(self, servo, value):
        accLSB = value & 0x7F
        accMSB = (value >> 7) & 0x7F
        self.__write(bytes([0x89])+bytes([servo])+bytes([accLSB])+bytes([accMSB]))

    def get_moving_state(self):
        self.__write(bytes([0x93]))
        data = self.__read(1)
        if data:
            return ord(data[0])
        else:
            return None

    def wait_until_at_target(self):
        while self.get_moving_state():
            time.sleep(0.1)

    def trigger_script(self, number):
        self.__write(bytes([0xA7])+bytes([number]))

    def stop_script(self):
        self.__write(bytes([0xA4]))

    def get_script_state(self):
        self.__write(bytes([0xAE]))
        data = self.__read(1)
        if data:
            return ord(data[0])
        else:
            return None

    def get_errors(self):
        self.__write(bytes([0xA1]))
        data = self.__read(2)

        if data:
            return data
        else:
            return None
