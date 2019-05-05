# lcp Module Loader
# iMagineLab - Living Character Program
from lcp.core.module import Module
import os
import pathlib
import importlib
import inspect
import glob


class ModuleLoader(Module):
    __name = "Module Loader"
    __version = "1.0"
    __default_module_dir = "..\\modules\\"

    def __init__(self):
        Module.__init__(self, self.__name, self.__version)
        self.__modules = []

    def start_modules(self):
        index = 0
        for module in self.__modules:
            index += 1
            print("> Starting module:", module.name, "[", index, "of", len(self.__modules), "]")
            module.start()

    def load_modules(self):
        print("> Checking for modules...")

        python_modules = self.__get_python_module_list_from_dir(self.__default_module_dir)
        found_modules = self.__get_lcp_modules_from_python_modules(python_modules)
        print("> Found", len(found_modules), "modules")

        index = 0
        loaded_modules = []
        for module in found_modules:
            index += 1
            print("> Loading module:", module.__name__, "[", index, "of", len(found_modules), "]")

            try:
                init_module = module()
                loaded_modules.append(init_module)

            except Exception as e:
                print("Failed to load module!")
                print("Error:", e)

        index = 0
        for module in loaded_modules:
            index += 1
            print("> Installing module:", module.name, "[", index, "of", len(loaded_modules), "]")

            try:
                module.install(loaded_modules)
                self.__modules.append(module)

            except Exception as e:
                print("Failed to install module!")
                print("Error:", e)

        return self.__modules

    @staticmethod
    def __get_lcp_modules_from_python_modules(python_modules):
        modules = []

        for python_module in python_modules:
            for class_member in inspect.getmembers(python_module, inspect.isclass):
                if class_member[1].__module__ == python_module.__name__:
                    module_class = class_member[1]

                    if issubclass(module_class, Module) and module_class is not Module:
                        modules.append(module_class)

        return modules

    @staticmethod
    def __get_python_module_list_from_dir(module_dir):
        modules = []
        py_files = ModuleLoader.__get_file_list_from_dir(module_dir, 'py')

        for py_file in py_files:
            module_package = 'lcp.' + '\\'.join(py_file.split('\\')[1:-1]).replace('\\', '.')
            module_name = pathlib.Path(py_file).stem

            try:
                module = importlib.import_module('.' + module_name, module_package)
            except ImportError as e:
                print("Unable to load module file: " + module_name)
                print("> Error:", e)
                continue

            modules.append(module)

        return modules

    @staticmethod
    def __get_file_list_from_dir(file_dir, extension):
        files = glob.glob(os.path.join(file_dir, '*.' + extension))
        files += glob.glob(os.path.join(file_dir, '**', '*.' + extension))

        return files
