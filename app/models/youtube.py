from models.singleton import Singleton
from settings.data_config import Config
from models.mongo_client import MyMongoClient
from apiclient.discovery import build
from utils.util import *


# Deciding on whether it should be singleton or not
class Youtube:
    def __init__(self):
        self._config = Config.get_instance()
        self._all_api_keys = self._config.YOUTUBE.API_KEYS
        self._api_key_index = 0
        self._client = build('youtube', self._config.YOUTUBE.API_VERSION,
                             developerKey=self._all_api_keys[self._api_key_index])
        self._mongo_client = MyMongoClient()
        self._db_name = self._config.YOUTUBE_MONGO.DB_NAME
        self._video_collection = self._config.YOUTUBE_MONGO.VIDEO_COLLECTION
        self._index_collection = self._config.YOUTUBE_MONGO.INDEX_COLLECTION
        self._page = 0
        self._oldest_datetime = self._config.OLDEST_DATEIME
        self._last_fetched_time = self.get_last_fetched_time()

    def get_all_api_keys(self):
        return self._all_api_keys

    def build_client_with_new_api_key(self):
        self._api_key_index += 1
        if self._api_key_index == len(self._all_api_keys):
            self._api_key_index = 0
        self._client = build('youtube', self._config.YOUTUBE.API_VERSION,
                             developerKey=self._all_api_keys[self._api_key_index])

    def refresh_client(self, new_key):
        self._client = build('youtube', self._config.YOUTUBE.API_VERSION,
                             developerKey=new_key)

    def configure_json(self, result, query):
        result_json = {
            "video_id": result["id"]["videoId"],
            "title": result["snippet"]["title"],
            "title_hash": str(get_hash_value(clean_string5(result["snippet"]["title"]))),
            "description_hash": str(get_hash_value(clean_string5(result["snippet"]["description"]))),
            "description": result["snippet"]["description"],
            "thumbnails": result["snippet"]["thumbnails"],
            "publishing_time": result["snippet"]["publishTime"],
            "query": query,
            "page": self._page
        }
        return result_json

    def get_last_fetched_time(self, query=None):
        last_fetched_time = None
        mongo_query = {}
        if query:
            mongo_query = {'query': query}
        records = self._mongo_client.fetch_all_records(self._db_name, self._video_collection, query=mongo_query)
        for record in records:
            if not last_fetched_time or record['publishing_time'] < last_fetched_time:
                last_fetched_time = record['publishing_time']
        return last_fetched_time

    def fetch_videos_for_query(self, query, max_results=25, save=True, save_index=True):
        # calling the search.list method to retrieve youtube search results
        if not self._last_fetched_time:
            self._last_fetched_time = get_rfc_3339_date_format()
        search_keyword = self._client.search().list(q=query, part="id, snippet", maxResults=max_results, type='video',
                                                    order='date', publishedBefore=self._last_fetched_time,
                                                    publishedAfter=self._oldest_datetime).execute()

        # extracting the results from search response
        results = search_keyword.get("items", [])
        videos = []
        # extracting required info from each result object
        for result in results:
            # video result object
            if result['id']['kind'] != "youtube#video":
                continue
            if result["snippet"]["publishTime"] >= self._last_fetched_time:
                continue
            self._last_fetched_time = result["snippet"]["publishTime"]
            result_json = self.configure_json(result, query=query)
            videos.append(result_json)
            if save_index:
                video_id = result_json['video_id']
                relevant_word_list = set(get_relevant_word_list(result_json['description']))
                relevant_word_list.update(set(get_relevant_word_list(result_json['title'])))
                self.update_indexes(relevant_word_list, video_id)

        if save:
            self._mongo_client.save_to_mongo(videos, db_name=self._db_name,
                                             collection_name=self._video_collection)
        if videos:
            self._page += 1

    def update_indexes(self, word_list, video_id):
        for word in word_list:
            self._mongo_client.update_record(self._db_name, self._index_collection, {'index_word': word},
                                             {'$addToSet': {'video_ids': video_id}})


def refresh_youtube_client():
    Youtube().build_client_with_new_api_key()


def get_max_retries_count():
    return len(Youtube().get_all_api_keys())
