from lcp.core.interfaces.module import Module
from lcp.modules.animationplayer.animation_player import AnimationPlayer
import _thread
import time
import traceback

from random import randrange
from pydub import AudioSegment
from pydub.playback import play


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
        #_thread.start_new_thread(self.__sing_a_song, ())

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
                    self.__animation_player.play_animation(animation_file, blocking=True, priority=1)

        self.__active = False


    def __sing_a_song(self):
        SONG_ANIMATIONS = ['..//..//..//resources//songs//parrotslife.csv',
                           '..//..//..//resources//songs//SomeoneIsWatchingMe.csv',
                           '..//..//..//resources//songs//ImToSexy.csv',
                           '..//..//..//resources//songs//MoveLikeJagger.csv',
                           '..//..//..//resources//songs//WeWishYou.csv',
                           '..//..//..//resources//songs//WhiteChristmas.csv',
                           '..//..//..//resources//songs//LastChristmas.csv']
        SONG_AUDIO = ['..//..//..//resources//songs//parrotslife.wav',
                      '..//..//..//resources//songs//Someoneiswatchingme.wav',
                      '..//..//..//resources//songs//Imtoosexy.wav',
                      '..//..//..//resources//songs//MoveLikeJagger.wav',
                      '..//..//..//resources//songs//Wewishyou.wav',
                      '..//..//..//resources//songs//WhiteChristmas.wav',
                      '..//..//..//resources//songs//LastChristmas.wav']

        if self.__animation_player is None:
            return

        while True:
            try:
                time.sleep(5)
                random_index = randrange(len(SONG_ANIMATIONS))
                animation_file = SONG_ANIMATIONS[random_index]
                audio_file = SONG_AUDIO[random_index]
                _thread.start_new_thread(self.__audio_play, (audio_file,))
                self.__animation_player.play_animation(animation_file, blocking=True, priority=500, overwrite=True)

                time.sleep(10)
            except Exception as e:
                print("Failed to play song audio!", e)
                traceback.print_exc()

    def __audio_play(self, audio_file_location):
        audio_file = AudioSegment.from_wav(audio_file_location)
        play(audio_file)
