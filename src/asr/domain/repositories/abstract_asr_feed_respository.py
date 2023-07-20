from abc import abstractmethod

from asr.domain.repositories.abstract_repositoty import AbtractRespository
from asr.domain.entities.asr_feed import ASRFeed


class AbstractASRFeedRepository(AbtractRespository):
    @abstractmethod
    def list_by_status():
        raise NotImplementedError

    @abstractmethod
    def find_and_update_feed_status(self, feed_id: str, feed_status: str):
        raise NotImplementedError

    @abstractmethod
    def find_and_update_feed_result_and_status(
        self,
        feed_id,
        feed_result: ASRFeed
    ):
        raise NotImplementedError
