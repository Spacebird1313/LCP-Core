from lcp.core.interfaces.module import Module
from lcp.modules.worldmodel.world_model import WorldModel
from lcp.modules.guiwindowmanager.gui_window_manager import GUIWindowManager
import PySimpleGUI as sgui


class WorldViewer(Module):
    __name = "World Viewer"
    __version = "1.0"
    __dependencies = [WorldModel, GUIWindowManager]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__world_model = []
        self.__window_manager = []
        self.__window = []

    def install(self, modules):
        modules = super().install(modules)
        self.__world_model = modules['WorldModel']
        self.__window_manager = modules['GUIWindowManager']

    def start(self):
        self.__create_window()

    def __event_callback(self, event, values):
        if event is '__TIMEOUT__':
            pass
        elif event is None or event == 'Quit':
            return

    def __create_window(self):
        top_view_column_layout = [[sgui.Text('Top', font=("Helvetica", 13))], [sgui.Graph(canvas_size=(400, 300), graph_bottom_left=(0, 0), graph_top_right=(400, 300), background_color='black', key='top_graph')]]
        front_view_column_layout = [[sgui.Text('Front', font=("Helvetica", 13))], [sgui.Graph(canvas_size=(400, 300), graph_bottom_left=(0, 0), graph_top_right=(400, 300), background_color='black', key='front_graph')]]
        left_view_column_layout = [[sgui.Text('Left', font=("Helvetica", 13))], [sgui.Graph(canvas_size=(400, 300), graph_bottom_left=(0, 0), graph_top_right=(400, 300), background_color='black', key='left_graph')]]

        layout = [[sgui.Column(top_view_column_layout), sgui.Column(front_view_column_layout)], [sgui.Column(left_view_column_layout)]]

        self.__window = self.__window_manager.create_window('World Viewer', layout, self.__event_callback)
