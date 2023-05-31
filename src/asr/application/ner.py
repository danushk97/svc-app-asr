from nemo.collections.nlp.models import TokenClassificationModel
from omegaconf import DictConfig
from pytorch_lightning import Trainer


class Ner(TokenClassificationModel):
    def __init__(self, cfg: DictConfig, trainer: Trainer = None):
        super().__init__(cfg, trainer)
    