import torch
from nemo.collections import nlp
from omegaconf import DictConfig
from pytorch_lightning import Trainer
from typing import Dict, List


class TextClassifier(nlp.models.TextClassificationModel):
    def __init__(self, cfg: DictConfig, trainer: Trainer = None):
        super().__init__(cfg, trainer)

    def _setup_infer_dataloader(self, cfg: Dict, queries: List[str], max_seq_length: int = -1) -> 'torch.utils.data.DataLoader':
        cfg['num_workers'] = 0

        return super()._setup_infer_dataloader(cfg, queries, max_seq_length)
    
    @staticmethod
    def predict_labels(queries, model):
        if torch.cuda.is_available():
            model.to("cuda")
        else:
            model.to("cpu")

           
        # max_seq_length=512 is the maximum length BERT supports.       
        results = model.classifytext(queries=queries, batch_size=1, max_seq_length=512)

        print('The prediction results of some sample queries with the trained model:')
        return results
    