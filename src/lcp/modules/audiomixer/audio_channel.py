import time


class AudioChannel:
    def __init__(self, mixer_module, channel_id, name, sample_rate):
        self.channel_id = channel_id
        self.name = name
        self.__sample_rate = sample_rate
        self.__mixer_module = mixer_module
        self.__buffer = bytearray()

    def get_buffer(self):
        return self.__buffer

    def write(self, buf):
        """Write bytes to the stream."""
        self.__buffer = bytearray(buf)

        while len(self.__buffer) > 0:
            time.sleep(0.01)

        return len(buf)
        # return self.__mixer_module.write(buf)

    def flush(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass

    @property
    def sample_rate(self):
        return self.__sample_rate
