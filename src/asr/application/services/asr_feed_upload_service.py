from logging import getLogger
from os import path

from asr.config import Config
from asr.domain.services.abstract_asr_feed_upload_service import \
    AbstractASRFeedUploadService


logger = getLogger(__name__)


class ASRFeedUploadService(AbstractASRFeedUploadService):
    def __init__(
        self, feed_location: str = Config.ASR_INPUT_FEED_LOCATION
    ) -> None:
        self.feed_location = feed_location

    def upload(self, audio: bytes, file_name: str) -> bool:
        destination_path = path.join(self.feed_location, file_name)
        with open(destination_path, 'wb') as f:
            f.write(audio)

        logger.info(f'File {file_name} uploaded successfully.')
