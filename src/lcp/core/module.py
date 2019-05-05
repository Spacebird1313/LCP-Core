class Module:
    def __init__(self, name, version, dependencies=[]):
        self.name = name
        self.version = version
        self.dependencies = dependencies

    def install(self, modules):
        self.__check_dependencies(modules)

    def __check_dependencies(self, modules):
        missing_dependencies = []
        for dependency in self.dependencies:
            resolved = False
            for module in modules:
                if isinstance(module, dependency):
                    resolved = True
                    break

            if not resolved:
                missing_dependencies.append(dependency.__name__)

        if len(missing_dependencies) != 0:
            raise Exception('Depended modules not loaded! {}'.format(missing_dependencies))

    def start(self):
        pass
