from lcp.core.interfaces.module import Module
from lcp.modules.servocontrol.servo_control import ServoControl
import PySimpleGUI as sgui
import _thread


class ServoSliderGUI(Module):
    __name = "Servo Slider GUI"
    __version = "1.0"
    __dependencies = [ServoControl]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__servo_control = []
        self.__window = []
        self.__update_gui_thread = []

    def install(self, modules):
        modules = super().install(modules)
        self.__servo_control = modules['ServoControl']

    def start(self):
        self.__update_gui_thread = _thread.start_new_thread(self.__update_gui, ())

    def __update_gui(self):
        self.__draw_gui()

        while True:
            event, values = self.__window.Read()
            print(event, values)

    def __draw_gui(self):
        layout = [[sgui.Text('Servo Slider Control', font=("Helvetica", 13))]]

        for servo_channel in self.__servo_control.get_channels().values():
            channel_row = [sgui.Text(servo_channel.name, size=(12, 1)),
                           sgui.Slider(range=(servo_channel.min_range, servo_channel.max_range), orientation='h', size=(30, 15), default_value=servo_channel.default, enable_events=True),
                           sgui.Checkbox('Overwrite controls', enable_events=True),
                           sgui.RButton('Reset')]

            layout.append(channel_row)

        layout.append([sgui.RButton('Reset all channels')])

        self.__window = sgui.Window('LCP Servo Control', layout)
