from lcp.core.interfaces.module import Module
from lcp.modules.servocontrol.servo_control import ServoControl
from lcp.modules.guiwindowmanager.gui_window_manager import GUIWindowManager
import PySimpleGUI as sgui


class ServoSliderGUI(Module):
    __name = "Servo Slider GUI"
    __version = "1.0"
    __dependencies = [ServoControl, GUIWindowManager]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__channel_priority_value = 999
        self.__servo_control = []
        self.__window_manager = []
        self.__window = []

    def install(self, modules):
        modules = super().install(modules)
        self.__servo_control = modules['ServoControl']
        self.__window_manager = modules['GUIWindowManager']

    def start(self):
        self.__create_window()

    def __event_callback(self, event, values):
        if event is '__TIMEOUT__':
            pass
        elif event is None or event == 'Quit':
            return
        elif 'reset_all_ch' in event:
            self.__reset_all_channels()
        elif 'slider_ch_' in event:
            channel_id = int(event[-1:])
            channel_position = values[event]
            channel_overwrite = values['overwrite_ch_' + str(channel_id)]
            self.__channel_slider_moved(channel_id, channel_position, channel_overwrite)
        elif 'overwrite_ch_' in event:
            channel_id = int(event[-1:])
            channel_position = values['slider_ch_' + str(channel_id)]
            toggle_value = values[event]
            self.__channel_overwrite_toggle(channel_id, channel_position, toggle_value)
        elif 'reset_ch_' in event:
            channel_id = int(event[-1:])
            self.__channel_reset(channel_id)
        else:
            print('Error: Unknown event:', event, 'detected in ServoSliderGUI!')

        self.__update_sliders()

    def __update_sliders(self):
        channels = self.__servo_control.get_channels()

        for channel_id in channels:
            channel_position = channels[channel_id].position
            self.__window.get_gui_window().Element('slider_ch_' + str(channel_id)).Update(channel_position)

    def __reset_all_channels(self):
        self.__servo_control.reset_all_channel_positions()

    def __channel_slider_moved(self, channel_id, value, channel_overwrite):
        priority = (0, self.__channel_priority_value)[channel_overwrite]
        self.__servo_control.set_channel_position(channel_id, value, priority)

    def __channel_overwrite_toggle(self, channel_id, channel_position, channel_overwrite):
        if channel_overwrite:
            self.__channel_slider_moved(channel_id, channel_position, channel_overwrite)
        else:
            self.__servo_control.release_channel_priority(channel_id, self.__channel_priority_value)

    def __channel_reset(self, channel_id):
        self.__servo_control.reset_channel_position(channel_id)

    def __create_window(self):
        layout = [[sgui.Text('Servo Slider Control', font=("Helvetica", 13))]]

        for servo_channel in self.__servo_control.get_channels().values():
            channel_row = [sgui.Text(servo_channel.name, size=(12, 1)),
                           sgui.Slider(range=(servo_channel.min_range, servo_channel.max_range), orientation='h', size=(30, 15), default_value=servo_channel.default, enable_events=True, key=('slider_ch_' + str(servo_channel.channel_id))),
                           sgui.Checkbox('Overwrite controls', enable_events=True, key=('overwrite_ch_' + str(servo_channel.channel_id))),
                           sgui.RButton('Reset', key=('reset_ch_' + str(servo_channel.channel_id)))]

            layout.append(channel_row)

        layout.append([sgui.RButton('Reset all channels', key='reset_all_ch')])

        self.__window = self.__window_manager.create_window('LCP Servo Control', layout, self.__event_callback)
