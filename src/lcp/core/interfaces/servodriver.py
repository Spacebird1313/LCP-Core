from lcp.core.interfaces.module import Module


class ServoDriver(Module):
    def __init__(self, name, version, dependencies=[]):
        super().__init__(name, version, dependencies)

    def install(self, modules):
        return super().install(modules)

    def start(self):
        pass

    def write(self, *data):
        pass

    def reset_servos(self):
        pass

    def set_position(self, servo, value):
        pass

    def set_speed(self, servo, value):
        pass

    def set_acceleration(self, servo, value):
        pass
