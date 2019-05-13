from lcp.core.interfaces.module import Module
from lcp.modules.webservice.web_service import WebService


class SystemDiagnostics(Module):
    __name = "System Diagnostics"
    __version = "1.0"
    __dependencies = [WebService]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)

    def install(self, modules):
        super().install(modules)

    def start(self):
        pass
