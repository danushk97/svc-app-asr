import json
from io import BytesIO
from logging import getLogger
from os import path
from time import time

from nemo.collections.asr.parts.utils.diarization_utils import OfflineDiarWithASR

from asr.application.utils.asr_decoder_timestamps_utils import MyASRDecoderTimeStamps
from asr.application.utils.speech_recognizer_utils import build_file_name
from asr.config import Config


logger = getLogger(__name__)


class SpeechRecognizer(OfflineDiarWithASR):
    def __init__(self, config=None) -> None:
        self._config = config or Config.ASR
        super().__init__(self._config.diarizer)
        self._asr_ts = MyASRDecoderTimeStamps(self._config.diarizer)
        self._asr_model = self._asr_ts.set_asr_model()
        self.word_ts_anchor_offset = self._asr_ts.word_ts_anchor_offset

    def make_file_lists(self):
        if self.manifest_filepath:
            return super().make_file_lists()

    def transcribe_audio(self):
        if not self._asr_ts.audio_file_list:
            print('No audio is set to transcribe.')

        words, words_ts = self._asr_ts.run_ASR(self._asr_model)
        diarization_result, diarization_score = self.run_diarization(self._config, words_ts)
        data = self.get_transcript_with_speaker_labels(diarization_result, words, words_ts)
        
        return data
    
    def set_audio_detail(self, path_to_audio_file):
        self._create_manifest(path_to_audio_file)
        self._asr_ts.set_audio_detail(self.manifest_filepath)
    
    def _create_manifest(self, path_to_audio_file):
        meta = {
            'audio_filepath': path_to_audio_file, 
            'offset': 0, 
            'duration':None, 
            'label': 'infer', 
            'text': '-', 
            'num_speakers': None, 
            'rttm_filepath': None, 
            'uem_filepath' : None
        }
        basename = path.basename(path_to_audio_file).split('.')[0]
        manifest_filepath = path.join(Config.INPUT_DETAIL_PATH, f'{basename}.json')
        with open(manifest_filepath, 'w') as fp:
            json.dump(meta,fp)
            fp.write('\n')
        self.manifest_filepath = manifest_filepath 
        self._config.diarizer.manifest_filepath = self.manifest_filepath
        self.make_file_lists()

    @staticmethod
    def feed(audio_bytes: BytesIO, file_name: str) -> bool:
        base_file_name, ext = file_name.rsplit('.', 1)
        file_name = build_file_name(base_file_name, ext)
        with open(path.join(Config.ASR_INPUT_FEED_LOCATION, file_name), 'wb') as f: 
            f.write(audio_bytes.read())
        logger.info(f'File {file_name} uploaded successfully.')

        return True
