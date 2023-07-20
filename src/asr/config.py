import os

from dotenv import load_dotenv


REQUIRED_ENVS = [
    "ASR_INPUT_FEED_LOCATION",
    "MONGO_URL",
    "MONGO_DB_NAME"
]


class Config:
    CWD = os.getcwd()
    ASR_INPUT_FEED_LOCATION = None

    MONGO_URL = None
    MONGO_DB_NAME = None

    @classmethod
    def init_config(cls):
        load_dotenv()

        for key in REQUIRED_ENVS:
            val = os.environ.get(key)
            if 'LOCATION' in key or 'PATH' in key:
                val = os.path.join(cls.CWD, val)

            setattr(cls, key, val)
