from lcp.core.interfaces.servodriver import ServoDriver
import time


class CharacterSimulator(ServoDriver):
    __name = "Character Simulator"
    __version = "1.0"

    def __init__(self, config):
        super().__init__(self.__name, self.__version)
        self.__serial_port = config.get('serial_port', fallback='/dev/ttyACM0')
        self.__serial_connection = None
        self.__isInitialised = False

    def install(self, modules):
        super().install(modules)

    def start(self):
        pass

    def write(self, *data):
        pass

    def reset_servos(self):
        pass

    def set_position(self, servo, value):
        pass

    def set_speed(self, servo, value):
        pass

    def set_acceleration(self, servo, value):
        pass
