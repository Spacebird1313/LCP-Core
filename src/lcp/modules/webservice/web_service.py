from lcp.core.module import Module
from pyramid.config import Configurator
from pyramid.response import Response
from waitress import serve
import _thread


class WebService(Module):
    __name = "Web Service"
    __version = "1.0"

    def __init__(self):
        super().__init__(self.__name, self.__version)
        self.__app = []
        self.__server_thread = []

    def install(self, modules):
        super().install(modules)

    def start(self):
        self.__configure_app()
        _thread.start_new_thread(self.__run_server, ())

    def add_page(self, name, route_name):
        pass

    def __configure_app(self):
        with Configurator() as config:
            config.add_route('home', '/')
            config.add_view(self.__page_home, route_name='home')
            self.__app = config.make_wsgi_app()

    def __run_server(self):
        serve(self.__app, host='0.0.0.0', port=1313)

    def __page_home(self, request):
        return Response('<body><h1>Hello World!</h1></body>')
