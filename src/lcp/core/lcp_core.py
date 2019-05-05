# lcp Core
# iMagineLab - Living Character Program
from lcp.core.module_loader import ModuleLoader
import time


class LCPCore(object):
    __version = "0.1"

    def __init__(self):
        print("LCP Core - Version", self.__version)
        print(">> Initialising system...")

        print(">> Loading figure configuration...")

        print(">> Start module loader...")
        self.__MLoader = ModuleLoader()
        self.__MLoader.load_modules()

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
