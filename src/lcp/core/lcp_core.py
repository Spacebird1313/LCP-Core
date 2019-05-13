# lcp Core
# iMagineLab - Living Character Program
from lcp.core.module_loader import ModuleLoader
from lcp.core.lcp_system_configurator import SystemConfigurator
import time


class LCPCore(object):
    __version = "0.1"

    def __init__(self):
        print("LCP Core - Version", self.__version)
        print(">> Initialising system...")
        self.__SystemConfig = SystemConfigurator()
        self.__SystemConfig.load_config("..\\..\\..\\resources\\config.ini")

        print(">> Loading character configuration...")
        # lcp character configuration

        print(">> Start module loader...")
        self.__MLoader = ModuleLoader(self.__SystemConfig.get_module_config('ModuleLoader'))
        self.__MLoader.load_modules(self.__SystemConfig)

    def start(self):
        print(">> Booting core...")

        print(">> Booting modules...")
        self.__MLoader.start_modules()

        time.sleep(1)

        print(">> System ready")

        while 1:
            time.sleep(1)


if __name__ == "__main__":
    LCPCore = LCPCore()
    LCPCore.start()
