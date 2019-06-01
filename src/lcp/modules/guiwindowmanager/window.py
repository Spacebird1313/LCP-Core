import PySimpleGUI as sgui


class Window:
    def __init__(self, title, layout, event_callback):
        self.title = title
        self.layout = layout
        self.event_callback = event_callback
        self.__gui_window = sgui.Window(title, layout)

    def get_events(self):
        return self.__gui_window.Read(timeout=0)

    def process_event_callback(self):
        event, values = self.get_events()

        self.event_callback(event, values)

    def get_gui_window(self):
        return self.__gui_window
