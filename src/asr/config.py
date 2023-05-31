from dotenv import dotenv_values
from omegaconf import OmegaConf


Config = None
model_config = None


class Config:
    ASR = None
    ASR_CONFIG_PATH = None
    ASR_INPUT_FEED_LOCATION = None
    ASR_INPUT_PROCESSING_LOCATION = None
    ASR_RESULTS_LOCATION = None
    INPUT_DETAIL_PATH = None

    TEXT_CLASSIFIER = None
    TEXT_CLASSIFIER_CONFIG_PATH = None
    TEXT_CLASSIFIER_MODEL_PATH = None

    @classmethod
    def init_config(cls):
        for key, val in dotenv_values().items():
            setattr(cls, key, val)

        cls.ASR = OmegaConf.load(cls.ASR_CONFIG_PATH)
        cls.TEXT_CLASSIFIER = OmegaConf.load(cls.TEXT_CLASSIFIER_CONFIG_PATH)
