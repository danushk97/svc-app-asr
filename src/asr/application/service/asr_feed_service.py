import json
import os

from http import HTTPStatus
from io import BytesIO
from logging import getLogger

from asr.application.service.exceptions import ASRServiceException
from asr.application.speech_recognizer import SpeechRecognizer
from asr.config import Config
from asr import constants


_logger = getLogger(__name__)


class ASRFeedService:
    def feed(self, audio_bytes: BytesIO, file_name: str) -> None:
        try:
            assert SpeechRecognizer.feed(audio_bytes, file_name) is True
        except AssertionError as err:
            raise ASRServiceException() from err
    
    def feed_status(self) -> dict:
        paths = {
            constants.PENDING: Config.ASR_INPUT_FEED_LOCATION, 
            constants.PROCESSING: Config.ASR_INPUT_PROCESSING_LOCATION, 
            constants.COMPLETED: Config.ASR_RESULTS_LOCATION,
            constants.FAILED: Config.ASR_FAILED_LOCATION
        }
        result = {}
        for status, path in paths.items():
            result[status] = os.listdir(path)
        
        return result
    
    def feed_result(self, file_name) -> dict:
        if not file_name in os.listdir(Config.ASR_RESULTS_LOCATION):
            message = 'Invalid file name.'
            raise ASRServiceException(title=message, detail=message, status=HTTPStatus.BAD_REQUEST)
        
        data = {}

        base_file_name = file_name.rsplit('.', 1)[0]
        with open(os.path.join(Config.ASR_RESULTS_LOCATION, file_name, f'{base_file_name}.json')) as f:
            data = json.load(f)

        return data
    