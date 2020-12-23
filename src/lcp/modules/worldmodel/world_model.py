from lcp.core.interfaces.module import Module


class WorldModel(Module):
    __name = "World Model"
    __version = "1.0"

    def __init__(self, config):
        super().__init__(self.__name, self.__version)

    def install(self, modules):
        pass

    def start(self):
        pass
