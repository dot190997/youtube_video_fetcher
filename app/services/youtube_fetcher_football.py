from models.youtube import Youtube
from settings.data_config import Config
from models.singleton import Singleton


class YoutubeFootball(Youtube, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.__time_interval = self._config.ASYNC_INTERVAL

    def fetch_videos(self):
        super().fetch_videos_for_query('football')
