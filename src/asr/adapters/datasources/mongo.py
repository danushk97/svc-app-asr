import pymongo

from asr.config import Config


class MongoClient:
    __connection = None

    @classmethod
    def get_connection(cls, db_name: str = Config.MONGO_DB_NAME):
        if cls.__connection is None:
            print(Config.MONGO_URL)
            cls.__connection = pymongo.MongoClient(Config.MONGO_URL)

        return cls.__connection[db_name]
