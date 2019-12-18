from lcp.core.interfaces.module import Module
from lcp.modules.audiomixer.audio_mixer import AudioMixer
from lcp.modules.wakeworddetector.wake_word_detector import WakeWordDetector
from lcp.modules.googleassistant.lcp_assistant import LCPAssistant
from . import audio_helper
from . import device_helper
import json
import uuid
import pathlib
import os

import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5


class GoogleAssistant(Module):
    __name = "Google Assistant"
    __version = "1.0"
    __dependencies = [AudioMixer]
    __optional_dependencies = [WakeWordDetector]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies, self.__optional_dependencies)
        self.__audio_mixer = None
        self.__wake_word_detector = None
        self.__credentials_file = "..\\..\\..\\resources\\google\\" + config.get('credentials_file', fallback='credentials.json')
        self.__device_config_file = "..\\..\\..\\resources\\google\\" + config.get('device_config_file', fallback='device.json')
        self.__language_code = config.get('language_code', fallback='en-US')
        self.__project_id = config.get('project_id', fallback=None)
        self.__device_model_id = config.get('device_model_id', fallback='lcp-core')
        self.__api_endpoint = config.get('assistant_api_endpoint', fallback=ASSISTANT_API_ENDPOINT)
        self.__device_id = None
        self.__conversation_stream = None
        self.__conversation_state = None
        self.__assistant = None
        self.__deadline = None
        self.__channel = None
        self.__credentials = None
        self.__audio_device = None
        self.__device_handler = None

    def install(self, modules):
        modules = super().install(modules)
        self.__audio_mixer = modules['AudioMixer']

        try:
            self.__wake_word_detector = modules['WakeWordDetector']
            self.__wake_word_detector.register_callback(self.__trigger_conversation)
        except:
            # Optional module - skip
            pass

        try:
            with open(self.__credentials_file, 'r') as f:
                self.__credentials = google.oauth2.credentials.Credentials(token=None, **json.load(f))
                http_request = google.auth.transport.requests.Request()
                self.__credentials.refresh(http_request)
        except Exception as e:
            raise Exception("Failed to load Google credentials!", e)

        self.__channel = google.auth.transport.grpc.secure_authorized_channel(
            self.__credentials, http_request, self.__api_endpoint
        )

        audio_device = audio_helper.SoundDeviceStream(
            sample_rate=audio_helper.DEFAULT_AUDIO_SAMPLE_RATE,
            sample_width=audio_helper.DEFAULT_AUDIO_SAMPLE_WIDTH,
            block_size=audio_helper.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
            flush_size=audio_helper.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
        )

#        audio_sink = audio_helper.SoundDeviceStream(
#            sample_rate=audio_helper.DEFAULT_AUDIO_SAMPLE_RATE,
#            sample_width=audio_helper.DEFAULT_AUDIO_SAMPLE_WIDTH,
#            block_size=audio_helper.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
#            flush_size=audio_helper.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
#        )

        audio_sink = self.__audio_mixer.create_front_channel('SPEECH', audio_helper.DEFAULT_AUDIO_SAMPLE_RATE)

        self.__conversation_stream = audio_helper.ConversationStream(
            source=audio_device,
            sink=audio_sink,
            iter_size=audio_helper.DEFAULT_AUDIO_ITER_SIZE,
            sample_width=audio_helper.DEFAULT_AUDIO_SAMPLE_WIDTH
        )

        self.__device_registration()

        self.__device_handler = device_helper.DeviceRequestHandler(self.__device_id)

        self.__assistant = LCPAssistant(self.__language_code, self.__device_model_id, self.__device_id, self.__conversation_stream, self.__channel, self.__deadline, self.__device_handler)

    def start(self):
        if not self.__wake_word_detector:
            while True:
                self.__trigger_conversation()
        else:
            self.__wake_word_detector.activate()

    def __trigger_conversation(self):
        if self.__wake_word_detector:
            self.__wake_word_detector.deactivate()

        continue_conversation = True
        while continue_conversation:
            continue_conversation = self.__assistant.assist()

        if self.__wake_word_detector:
            self.__wake_word_detector.activate()

    def __device_registration(self):
        try:
            with open(self.__device_config_file) as f:
                config = json.load(f)
                self.__device_id = config['id']
        except Exception as e:
            if not self.__project_id:
                raise Exception("Could not register LCP core at the Google Assistant service. Missing project_id!")

            device_base_url = (
                'https://%s/v1alpha2/projects/%s/devices' % (self.__api_endpoint, self.__project_id)
            )

            self.__device_id = str(uuid.uuid1())
            payload = {
                'id': self.__device_id,
                'model_id': self.__device_model_id,
                'client_type': 'SDK_SERVICE'
            }

            session = google.auth.transport.requests.AuthorizedSession(
                credentials=self.__credentials
            )

            request = session.post(device_base_url, data=json.dumps(payload))
            if request.status_code != 200:
                raise Exception('Failed to register device at the Google Assistant service. %s', request.text)

            pathlib.Path(os.path.dirname(self.__device_config_file)).mkdir(exist_ok=True)
            with open(self.__device_config_file, 'w') as f:
                json.dump(payload, f)
