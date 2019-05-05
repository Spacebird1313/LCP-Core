from lcp.core.module import Module
from lcp.modules.webservice.web_service import WebService


class WebConfig(Module):
    __name = "Web Configurator"
    __version = "1.0"
    __dependencies = [WebService]

    def __init__(self):
        super().__init__(self.__name, self.__version, self.__dependencies)

    def install(self, modules):
        super().install(modules)

    def start(self):
        pass
