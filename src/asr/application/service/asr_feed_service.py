import json
import os

from http import HTTPStatus
from io import BytesIO
from logging import getLogger

from asr.application.service.exceptions import ASRServiceException
from asr.application.asr_feeder import ASRFeeder
from asr.config import Config
from asr import constants


_logger = getLogger(__name__)


class ASRFeedService:
    def feed(self, audio_bytes: BytesIO, file_name: str) -> None:
        try:
            assert ASRFeeder.feed(audio_bytes, file_name) is True
        except AssertionError as err:
            raise ASRServiceException() from err

    def feed_from_urls(self, audio_urls: list) -> None:
        try:
            assert ASRFeeder.feed_from_urls(audio_urls) is True
        except AssertionError as err:
            raise ASRServiceException() from err

    def retrieve_feeds_grouped_by_status(self) -> dict:
        paths = {
            constants.PENDING: Config.ASR_INPUT_FEED_LOCATION,
            constants.PROCESSING: Config.ASR_INPUT_PROCESSING_LOCATION,
            constants.COMPLETED: Config.ASR_RESULTS_LOCATION,
            constants.FAILED: Config.ASR_FAILED_LOCATION
        }
        result = {}
        for status, path in paths.items():
            result[status] = [
                feed_id
                for feed_id in os.listdir(path) 
                if feed_id.lower() != '.ds_store'
            ]

        return result

    def retrieve_feed_result(self, feed_id) -> dict:
        if feed_id not in os.listdir(Config.ASR_RESULTS_LOCATION):
            message = 'Invalid file name.'
            raise ASRServiceException(
                title=message, detail=message,
                status=HTTPStatus.BAD_REQUEST
            )

        data = {}
        result_dir = os.path.join(Config.ASR_RESULTS_LOCATION, feed_id)
        result_file = None
        for root, _, files in os.walk(result_dir):
            for file in files:
                if file.endswith(".json"):
                    result_file = os.path.join(root, file)

        with open(os.path.join(result_dir, result_file)) as f:
            data = json.load(f)

        return data
