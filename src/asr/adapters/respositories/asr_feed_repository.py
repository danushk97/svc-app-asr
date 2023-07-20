from datetime import datetime

from asr import constants
from asr.domain.entities.asr_feed import ASRFeed
from asr.domain.repositories.abstract_asr_feed_respository import \
    AbstractASRFeedRepository


class ASRFeedRepository(AbstractASRFeedRepository):
    def __init__(self, connection=None) -> None:
        self.__connection = connection.asr_feeds

    def add(self, asr_feed: ASRFeed) -> str:
        return self.__connection.insert_one(asr_feed.to_dict()).inserted_id

    def find(self, id: str):
        return self.__connection.find_one({"_id": id})

    def list(self):
        return [data for data in self.__connection.find()]

    def list_by_status(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "feeds": {
                        "$push": {
                            "_id": "$_id",
                            "filename": "$filename",
                            "status": "$status",
                            "source": "$source"
                        }
                    }
                }
            }
        ]
        result_set = self.__connection.aggregate(pipeline)
        feeds_by_stautus = {
            constants.COMPLETED: [],
            constants.PENDING: [],
            constants.PROCESSING: [],
            constants.FAILED: []
        }

        for data in result_set:
            id = data["_id"]
            for data in data["feeds"]:
                feeds_by_stautus[id].append(data)

        return feeds_by_stautus

    def find_and_update_feed_result_and_status(self, feed_id, result, status):
        self.__connection.update_one({"_id": feed_id}, {
            "$set": {
                "result": result.to_dict(),
                "status": status,
                "updated_at": datetime.utcnow()
            }
        }, upsert=False)

    def find_and_update_feed_status(self, feed_id, status):
        self.__connection.update_one({"_id": feed_id}, {
            "$set": {
                "status": status,
                "updated_at": datetime.utcnow()
            }
        }, upsert=False)
