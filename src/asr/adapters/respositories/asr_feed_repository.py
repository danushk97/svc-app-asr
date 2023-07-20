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
        return self.__connection.find_one({constants._ID: id})

    def list(self):
        return [data for data in self.__connection.find()]

    def list_by_status(self):
        pipeline = [
            {
                "$group": {
                    constants._ID: "$status",
                    constants.FEEDS: {
                        "$push": {
                            constants._ID: "$_id",
                            constants.FILENAME: "$filename",
                            constants.STATUS: "$status",
                            constants.SOURCE: "$source",
                            constants.CREATED_AT: "$created_at",
                            constants.UPDATED_AT: "$updated_at",
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
            id = data[constants._ID]
            for data in data[constants.FEEDS]:
                feeds_by_stautus[id].append(data)

        return feeds_by_stautus

    def find_and_update_feed_result_and_status(self, feed_id, result, status):
        self.__connection.update_one({"_id": feed_id}, {
            "$set": {
                constants.RESULT: result.to_dict(),
                constants.STATUS: status,
                constants.UPDATED_AT: datetime.utcnow()
            }
        }, upsert=False)

    def find_and_update_feed_status(self, feed_id, status):
        self.__connection.update_one({"_id": feed_id}, {
            "$set": {
                constants.STATUS: status,
                constants.UPDATED_AT: datetime.utcnow()
            }
        }, upsert=False)
