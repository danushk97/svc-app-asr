import os

from dotenv import dotenv_values
from omegaconf import OmegaConf


Config = None
model_config = None

class Config:
    CWD = os.getcwd()
    ASR = None
    ASR_CONFIG_PATH = None
    ASR_INPUT_FEED_LOCATION = None
    ASR_INPUT_PROCESSING_LOCATION = None
    ASR_RESULTS_LOCATION = None
    ASR_FAILED_LOCATION = None
    INPUT_DETAIL_PATH = None

    TEXT_CLASSIFIER = None
    TEXT_CLASSIFIER_CONFIG_PATH = None
    TEXT_CLASSIFIER_MODEL_PATH = None

    @classmethod
    def init_config(cls):
        for key, val in dotenv_values().items():
            if 'LOCATION' in key or 'PATH' in key:
                val = os.path.join(cls.CWD, val)
                
            setattr(cls, key, val)

        cls.ASR = OmegaConf.load(os.path.join(cls.CWD, cls.ASR_CONFIG_PATH))
        cls.TEXT_CLASSIFIER = OmegaConf.load(os.path.join(cls.CWD, cls.TEXT_CLASSIFIER_CONFIG_PATH))
