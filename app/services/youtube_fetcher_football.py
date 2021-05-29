from models.youtube import Youtube
from settings.data_config import Config
from models.singleton import Singleton
from services.decorator import retry
from utils.util import get_logger


class YoutubeFootball(Youtube, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self._last_fetched_time = self.get_last_fetched_time('football')

    @retry(Exception, tries=len(Youtube().get_all_api_keys()), logger=get_logger('mismatch'), fallback_func=Youtube().build_client_with_new_api_key)
    def fetch_videos(self):
        super().fetch_videos_for_query('football')
