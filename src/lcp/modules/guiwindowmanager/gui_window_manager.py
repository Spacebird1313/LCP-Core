from lcp.core.interfaces.module import Module
from lcp.modules.guiwindowmanager.window import Window
import _thread


class GUIWindowManager(Module):
    __name = "GUI Window Manager"
    __version = "1.0"

    def __init__(self, config):
        super().__init__(self.__name, self.__version)
        self.__windows = []
        self.__window_event_thread = []

    def install(self, modules):
        super().install(modules)

    def start(self):
        self.__window_event_thread = _thread.start_new_thread(self.__handle_window_events, ())

    def create_window(self, title, layout, event_callback):
        new_window = Window(title, layout, event_callback)
        self.__windows.append(new_window)

        return new_window

    def __handle_window_events(self):
        while True:
            for window in self.__windows:
                window.process_event_callback()
