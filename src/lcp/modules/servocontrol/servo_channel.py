import threading


class ServoChannel:
    def __init__(self, channel_id, name, min_range, max_range, default):
        self.channel_id = channel_id
        self.name = name
        self.min_range = min_range
        self.max_range = max_range
        self.default = default
        self.position = default
        self.position_priority = 0
        self.__lock = threading.Lock()

    def set_position(self, position, priority):
        self.__lock.acquire()
        self.__set_position_wrapped(position, priority)
        self.__lock.release()

    def __set_position_wrapped(self, position, priority):
        if priority < self.position_priority:
            return
        else:
            self.position_priority = priority

        if position < self.min_range:
            self.position = self.min_range
        elif position > self.max_range:
            self.position = self.max_range
        else:
            self.position = position

    def release_priority(self, priority):
        self.__lock.acquire()
        self.__release_priority_wrapped(priority)
        self.__lock.release()

    def __release_priority_wrapped(self, priority):
        if priority == self.position_priority:
            self.position_priority = 0

    def reset_position(self):
        self.__lock.acquire()
        self.__reset_position_wrapped()
        self.__lock.release()

    def __reset_position_wrapped(self):
        self.position = self.default
        self.position_priority = 0
