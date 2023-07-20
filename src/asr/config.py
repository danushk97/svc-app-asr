import os

from dotenv import dotenv_values


class Config:
    CWD = os.getcwd()
    ASR_INPUT_FEED_LOCATION = None
    ASR_INPUT_PROCESSING_LOCATION = None
    ASR_RESULTS_LOCATION = None
    ASR_FAILED_LOCATION = None

    MONGO_URL = None
    MONGO_DB_NAME = None

    @classmethod
    def init_config(cls):
        for key, val in dotenv_values().items():
            if 'LOCATION' in key or 'PATH' in key:
                val = os.path.join(cls.CWD, val)

            setattr(cls, key, val)
