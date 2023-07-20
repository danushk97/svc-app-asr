from logging import getLogger
from typing import BinaryIO
from bson import ObjectId

from asr import constants
from asr.domain.repositories.abstract_asr_feed_respository import \
    AbstractASRFeedRepository
from asr.domain.datasources.abstract_http_client import AbstractHTTPClient
from asr.domain.entities.asr_feed import ASRFeed, ASRFeedResult
from asr.domain.services.abstract_asr_feed_upload_service import \
    AbstractASRFeedUploadService


_logger = getLogger(__name__)


class ASRFeedService:
    def __init__(
        self,
        repository: AbstractASRFeedRepository,
        http_client: AbstractHTTPClient,
        asr_feed_upload_service: AbstractASRFeedUploadService
    ) -> None:
        self.__asr_feeds = repository
        self.__http_client = http_client
        self.__asr_feed_upload_service = asr_feed_upload_service

    def __save_feed(self, asr_feed: ASRFeed):
        self.__asr_feeds.add(asr_feed)

    def upload_feed_content_and_save_feed(
        self,
        feed_content: BinaryIO,
        file_name: str,
        source=''
    ) -> ASRFeed:
        asr_result = ASRFeedResult()
        asr_feed = ASRFeed(file_name, constants.PENDING, asr_result, source)

        self.__asr_feed_upload_service.upload(
            feed_content,
            f"{asr_feed._id}_{file_name}"
        )

        self.__save_feed(asr_feed)

        return asr_feed

    def upload_feed_content_and_save_feed_from_urls(
        self,
        audio_urls: list
    ) -> None:
        feeds_to_upload_and_save = list()
        uploaded_and_saved_feeds = list()

        for url in audio_urls:
            raw_content = self.__http_client.send_request(constants.GET, url)
            file_name = url.rsplit('/', 1)[1]
            feeds_to_upload_and_save.append((raw_content, file_name, url))

        for feed in feeds_to_upload_and_save:
            uploaded_and_saved_feeds.append(
                self.upload_feed_content_and_save_feed(*feed)
            )

        return uploaded_and_saved_feeds

    def retrieve_feed_ids_grouped_by_status(self) -> dict:
        return self.__asr_feeds.list_by_status()

    def retrieve_feed(self, feed_id) -> dict:
        return self.__asr_feeds.find(ObjectId(feed_id))

    def update_feed_status(self, feed_id: str, status: str):
        return self.__asr_feeds.find_and_update_feed_status(feed_id, status)

    def update_feed_result(self, feed_id: str, feed_result: ASRFeedResult):
        return self.__asr_feeds.find_and_update_feed_result_and_status(
            feed_id,
            feed_result
        )
