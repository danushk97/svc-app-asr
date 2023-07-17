import requests
from io import BytesIO
from logging import getLogger
from os import path, makedirs
from typing import Union
from uuid import uuid4

from asr.application.exceptions import ASRFeederException
from asr.config import Config


logger = getLogger(__name__)


class ASRFeeder:
    @staticmethod
    def feed(audio: Union[BytesIO, bytes], file_name: str) -> bool:
        input_dir = path.join(Config.ASR_INPUT_FEED_LOCATION, str(uuid4()))
        makedirs(input_dir)
        with open(path.join(input_dir, file_name), 'wb') as f:
            if isinstance(audio, bytes):
                f.write(audio)
            else:
                f.write(audio.read())

        logger.info(f'File {file_name} uploaded successfully.')

        return True

    @classmethod
    def feed_from_urls(cls, urls: list) -> bool:
        responses = []
        for url in urls:
            file_name = url.split("/")[-1]
            try:
                response = requests.get(url)
                response.raise_for_status()
                responses.append(response)
            except requests.RequestException as err:
                logger.error(err)
                raise ASRFeederException() from err

        for response in responses:
            try:
                cls.feed(response.content, file_name)
            except Exception as err:
                logger.error(err)
                raise ASRFeederException() from err

        logger.info(f'File {file_name} uploaded successfully.')

        return True
