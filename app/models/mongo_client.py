import pymongo
import sys
from tqdm import tqdm

from settings.data_config import Config
from models.singleton import Singleton


class MyMongoClient(metaclass=Singleton):

    def __init__(self):
        config = Config.get_instance()
        mongo_db_url = MyMongoClient.get_mongo_url(config.MONGO.USER, config.MONGO.PASSWORD, config.MONGO.SERVER, config.MONGO.PORT)
        self.__instance = pymongo.MongoClient(mongo_db_url)

    @staticmethod
    def get_mongo_url(mongo_user, mongo_password, mongo_server, mongo_port):
        return "mongodb://%s:%s@%s:%s" % (mongo_user, mongo_password, mongo_server, mongo_port)

    def fetch_all_records(self, database, collection, limit=None, query=None, projection=None):
        records = None
        client = self.__instance
        try:
            query = query or {}
            projection = projection or {'_id': 0}
            if limit is None:
                records = client[database][collection].find(query, projection)
            else:
                records = client[database][collection].find(query, projection).limit(limit)
        except Exception as e:
            print(e)
            sys.exit(1)
        return records

    def fetch_single_record(self, database, collection, limit=None, query=None, projection=None):
        record = None
        client = self.__instance
        try:
            query = query or {}
            projection = projection or {'_id': 0}
            if limit is None:
                record = client[database][collection].find_one(query, projection)
            else:
                record = client[database][collection].find_one(query, projection).limit(limit)
        except Exception as e:
            print(e)
            sys.exit(1)
        return record

    def save_to_mongo(self, documents, db_name, collection_name, refresh=False):
        client = self.__instance
        collection = client[db_name][collection_name]
        if refresh:
            try:
                collection.drop()
            except Exception as exc:
                print("Exception while dropping collection: ", collection, str(exc))

        collection = client[db_name][collection_name]
        bulk_metrics = collection.initialize_unordered_bulk_op()
        try:
            for document in tqdm(documents, desc="Inserting documents to bulk operation"):
                bulk_metrics.insert(document)
        except Exception as exc:
            print("Exception in insert one: ", collection, str(exc))
        try:
            # print("Executing bulk metrics...")
            bulk_metrics.execute()
            # print("Bulk metrics executed")
        except Exception as exc:
            print("Exception in bulk update exec: ", collection, str(exc))

    def update_record(self, db_name, collection_name, _filter, _set_field, upsert=True):
        client = self.__instance
        collection = client[db_name][collection_name]
        try:
            collection.update(_filter, _set_field, upsert=upsert)
        except Exception as exc:
            print("Exception in updating one: ", collection, str(exc))
