from settings.data_config import Config
from models.mongo_client import MyMongoClient
from models.singleton import Singleton
from utils.util import get_relevant_word_list, get_hash_value, clean_string5


class MasterAPISupport(metaclass=Singleton):
    def __init__(self):
        self._config = Config.get_instance()
        self._mongo_client = MyMongoClient()
        self._db_name = self._config.YOUTUBE_MONGO.DB_NAME
        self._video_collection = self._config.YOUTUBE_MONGO.VIDEO_COLLECTION
        self._index_collection = self._config.YOUTUBE_MONGO.INDEX_COLLECTION

    def fetch_paginated_videos(self, page_number=0):
        query = {'page': int(page_number)}
        records_cursor = self._mongo_client.fetch_all_records(self._db_name, self._video_collection, query=query)
        records = []
        for record in records_cursor:
            records.append(record)
        return records

    def get_videos_by_title(self, query, query_type):
        hash_string = str(get_hash_value(clean_string5(query)))
        records = self._mongo_client.fetch_all_records(self._db_name, self._video_collection,
                                                       query={'{}_hash'.format(query_type): hash_string})
        for record in records:
            if clean_string5(query) in [clean_string5(record['title']), clean_string5(record['description'])]:
                return [record]
        return []

    def get_videos_for_query(self, query, top_results=5, query_type='query'):
        if query_type in ['description', 'title']:
            return self.get_videos_by_title(query, query_type)
        relevant_word_list = get_relevant_word_list(query)
        video_id_to_match_word_length = dict()
        for word in relevant_word_list:
            record = self._mongo_client.fetch_single_record(self._db_name, self._index_collection, query={'index_word': word})
            if not record:
                continue
            for video_id in record['video_ids']:
                video_id_to_match_word_length.setdefault(video_id, 0)
                video_id_to_match_word_length[video_id] += 1
        relevant_video_ids = []
        if top_results:
            relevant_sorted_ids = sorted(video_id_to_match_word_length.items(), key=lambda x: x[1], reverse=True)
            id_count = min(int(top_results), len(relevant_sorted_ids))
            for relevant_id_pair in relevant_sorted_ids[:id_count]:
                relevant_video_ids.append(relevant_id_pair[0])
        else:
            relevant_video_ids = list(video_id_to_match_word_length.keys())

        final_records = []
        for video_id in relevant_video_ids:
            record = self._mongo_client.fetch_single_record(self._db_name, self._video_collection, query={'video_id': video_id})
            if not record:
                continue
            final_records.append(record)

        final_records = sorted(final_records, key=lambda x: x['publishing_time'], reverse=True)
        return final_records
