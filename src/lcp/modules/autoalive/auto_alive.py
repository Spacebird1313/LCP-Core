from lcp.core.interfaces.module import Module
from lcp.modules.animationplayer.animation_player import AnimationPlayer
import _thread


class AutoAlive(Module):
    __name = "Auto Alive"
    __version = "1.0"
    __dependencies = [AnimationPlayer]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__animation_player = []
        self.__interrupt = False
        self.__active = False
        self.__auto_alive_thread = []
        self.__animation_files = [x.strip() for x in config.get('animation_files', fallback='').split(',')]

    def install(self, modules):
        modules = super().install(modules)
        self.__animation_player = modules['AnimationPlayer']

    def start(self):
        self.activate()

    def activate(self):
        if not self.__active:
            self.__auto_alive_thread = _thread.start_new_thread(self.__auto_alive_task, ())

    def deactivate(self):
        if self.__active:
            self.__interrupt = True
            self.__animation_player.stop_animation()
            self.__auto_alive_thread.join()

    def __auto_alive_task(self):
        self.__interrupt = False
        self.__active = True

        while not self.__interrupt:
            for animation in self.__animation_files:
                if not self.__interrupt:
                    animation_file = '..//modules//autoalive//animations//' + animation
                    self.__animation_player.play_animation(animation_file, blocking=True)

        self.__active = False
