from lcp.core.interfaces.module import Module
from lcp.modules.audiorecorder.audio_recorder import AudioRecorder
import platform
import os
import struct
import pvporcupine


class WakeWordDetector(Module):
    __name = "Wake Word Detector"
    __version = "1.0"
    __dependencies = [AudioRecorder]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__keyword_filename = config.get('keyword_file', fallback='keyword')
        self.__sensitivity = float(config.get('sensitivity', fallback=0.5))
        self.__active = False
        self.__callbacks = []
        self.__detect_handler = []
        self.__audio_recoder = []

    def install(self, modules):
        modules = super().install(modules)
        self.__audio_recoder = modules['AudioRecorder']
        self.__detect_handler = pvporcupine.create(
            #library_path=self.__default_library_path(),
            #model_path=self.__model_file_path(),
            keyword_paths=[self.__keyword_file_path(self.__keyword_filename)],
            sensitivities=[self.__sensitivity])

    def start(self):
        self.__audio_recoder.register_callback(self.__analyse_sample)

    def activate(self):
        self.__active = True

    def deactivate(self):
        self.__active = False

    def register_callback(self, callback):
        self.__callbacks.append(callback)

    def __analyse_sample(self, in_data, frame_count, time_info, status):
        if self.__active and frame_count >= self.__detect_handler.frame_length:
            pcm = struct.unpack_from("h" * self.__detect_handler.frame_length, in_data)
            result = self.__detect_handler.process(pcm)

            if result >= 0:
                for callback in self.__callbacks:
                    callback()

    def __keyword_file_path(self, filename):
        system = platform.system()
        machine = platform.machine()

        if system == 'Darwin':
            return os.path.join(os.path.dirname(__file__), 'lib/mac/keywords/%s' % machine, '%s' % filename)
        elif system == 'Linux':
            if machine == 'x86_64' or machine == 'i386':
                return os.path.join(os.path.dirname(__file__), 'lib/linux/keywords/%s' % machine, '%s' % filename)
            else:
                raise Exception('Cannot autodetect the binary type of the Porcupine library. Please enter the path to the shared object using --library_path command line argument.')
        elif system == 'Windows':
            return os.path.join(os.path.dirname(__file__), 'lib\\windows\\keywords\\%s' % filename)
        raise NotImplementedError('The Porcupine engine is not supported on %s/%s yet!' % (system, machine))

    def __model_file_path(self):
        filename = 'porcupine_params.pv'
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            return os.path.join(os.path.dirname(__file__), 'lib/common/%s' % filename)
        elif system == 'Windows':
            return os.path.join(os.path.dirname(__file__), 'lib\\common\\%s' % filename)
        raise NotImplementedError('The Porcupine engine is not supported on %s yet!' % system)

    def __default_library_path(self):
        system = platform.system()
        machine = platform.machine()

        if system == 'Darwin':
            return os.path.join(os.path.dirname(__file__), 'lib/mac/%s/libpv_porcupine.dylib' % machine)
        elif system == 'Linux':
            if machine == 'x86_64' or machine == 'i386':
                return os.path.join(os.path.dirname(__file__), 'lib/linux/%s/libpv_porcupine.so' % machine)
            else:
                raise Exception('Cannot autodetect the binary type of the Porcupine library. Please enter the path to the shared object using --library_path command line argument.')
        elif system == 'Windows':
            if platform.architecture()[0] == '32bit':
                return os.path.join(os.path.dirname(__file__), 'lib\\windows\\i686\\libpv_porcupine.dll')
            else:
                return os.path.join(os.path.dirname(__file__), 'lib\\windows\\amd64\\libpv_porcupine.dll')
        raise NotImplementedError('The Porcupine engine is not supported on %s/%s yet!' % (system, machine))
