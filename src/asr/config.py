import os
from logging import getLogger

from dotenv import load_dotenv


_logger = getLogger(__name__)


REQUIRED_ENVS = [
    "ASR_FEED_LOCATION",
    "ASR_TRANSLATE_FEED_LOCATION",
    "MONGO_URL",
    "MONGO_DB_NAME"
]


class Config:
    CWD = os.getcwd()
    ASR_FEED_LOCATION = None
    ASR_TRANSLATE_FEED_LOCATION = None

    MONGO_URL = None
    MONGO_DB_NAME = None

    @classmethod
    def init_config(cls):
        load_dotenv()
        missing_configs = []
        for key in REQUIRED_ENVS:
            val = os.environ.get(key)
            if val is None:
                missing_configs.append(key)
                continue

            if 'LOCATION' in key or 'PATH' in key:
                val = os.path.join(cls.CWD, val)

            setattr(cls, key, val)

        if missing_configs:
            _logger.critical(
                f"Aborting application start up due to "
                f"missing configs {missing_configs}"
            )
            os._exit(1)
