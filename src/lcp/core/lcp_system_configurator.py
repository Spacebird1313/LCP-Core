import configparser


class SystemConfigurator(object):
    __version = "1.0"

    def __init__(self):
        self.__parser = []

    def load_config(self, file):
        self.__parser = configparser.ConfigParser()
        self.__parser.read(file)

    def get_module_config(self, module_name):
        try:
            config = self.__parser[module_name]
        except:
            self.__parser[module_name] = {}
            config = self.__parser[module_name]

        return config
