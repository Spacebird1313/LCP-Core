class Module:
    def __init__(self, name, version, dependencies=[], optional_dependencies=[]):
        self.name = name
        self.version = version
        self.dependencies = dependencies
        self.optional_dependencies = optional_dependencies

    def install(self, modules):
        return self.__check_dependencies(modules)

    def __check_dependencies(self, modules):
        missing_dependencies = []
        dependencies = {}
        for dependency in self.dependencies:
            resolved = False
            for module in modules:
                if isinstance(module, dependency):
                    resolved = True
                    dependencies.update({dependency.__name__: module})
                    break

            if not resolved:
                missing_dependencies.append(dependency.__name__)

        if len(missing_dependencies) != 0:
            raise Exception('Depended modules not loaded! {}'.format(missing_dependencies))

        for dependency in self.optional_dependencies:
            for module in modules:
                if isinstance(module, dependency):
                    dependencies.update({dependency.__name__: module})
                    break

        return dependencies

    def start(self):
        pass
