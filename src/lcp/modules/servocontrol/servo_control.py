from lcp.core.interfaces.module import Module
from lcp.modules.servocontrol.servo_channel import ServoChannel
import time
import _thread


class ServoControl(Module):
    __name = "Servo Control"
    __version = "1.0"
    __dependencies = []

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__servo_driver_class_name = config.get('servo_driver', fallback='ServoDriver')
        self.__servo_driver = []
        self.__channels = self.__set_channels(config)
        self.__driver_sync_thread = []
        print('Initialise', len(self.__channels), 'servo channels')

    def install(self, modules):
        self.__set_driver_class_dependency(modules)
        modules = super().install(modules)
        self.__servo_driver = modules[self.__servo_driver_class_name]

    def start(self):
        self.__driver_sync_thread = _thread.start_new_thread(self.__sync_servo_driver, ())

    def set_channel_position(self, channel, position, priority):
        self.__channels.get(channel).set_position(position, priority)

    def release_channel_priority(self, channel, priority):
        self.__channels.get(channel).release_priority(priority)

    def get_channel_position(self, channel):
        return self.__channels.get(channel).position

    def get_channel_priority(self, channel):
        return self.__channels.get(channel).position_priority

    def get_channels(self):
        return self.__channels

    def reset_channel_position(self, channel):
        self.__channels.get(channel).reset_position()

    def reset_all_channel_positions(self):
        for channel in self.__channels.values():
            channel.reset_position()

    def __set_driver_class_dependency(self, modules):
        driver_module = None

        for module in modules:
            if self.__servo_driver_class_name == module.__class__.__name__:
                driver_module = module.__class__
                break

        if driver_module is not None:
            self.__dependencies.append(driver_module)
        else:
            raise Exception('Could not find servo driver of type: ' + self.__servo_driver_class_name)

    def __sync_servo_driver(self):
        while True:
            for channel_index in self.__channels:
                position = self.__channels[channel_index].position
                self.__servo_driver.set_position(channel_index, int(position))

            time.sleep(.001)

    @staticmethod
    def __set_channels(config):
        new_channels = dict()
        num_servo_channels = int(config.get('servo_channels', fallback=0))

        for i in range(num_servo_channels):
            channel_name = config.get('channel_' + str(i) + '_name', fallback=('channel ' + str(i)))

            try:
                channel_min = int(config.get('channel_' + str(i) + '_min', fallback=None))
            except:
                print('Missing or invalid value for min position of channel ' + str(i))
                continue

            try:
                channel_max = int(config.get('channel_' + str(i) + '_max', fallback=None))
            except:
                print('Missing or invalid value for max position of channel ' + str(i))
                continue

            try:
                channel_default = int(config.get('channel_' + str(i) + '_default', fallback=None))
            except:
                print('Missing or invalid value for default position of channel ' + str(i))
                continue

            new_channel = ServoChannel(i, channel_name, channel_min, channel_max, channel_default)
            new_channels.update({i: new_channel})

        return new_channels
