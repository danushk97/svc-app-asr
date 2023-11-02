import pymongo

from asr.config import Config


class MongoClient:
    __connection = None

    @classmethod
    def get_connection(cls):
        if cls.__connection is None:
            cls.__connection = pymongo.MongoClient(Config.MONGO_URL)\
                .get_database(Config.MONGO_DB_NAME)

        return cls.__connection
