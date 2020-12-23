from lcp.core.interfaces.module import Module


class SpeechSynthesizer(Module):
    __name = "Speech Synthesizer"
    __version = "1.0"
    __dependencies = []

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)

    def install(self, modules):
        pass

    def start(self):
        pass