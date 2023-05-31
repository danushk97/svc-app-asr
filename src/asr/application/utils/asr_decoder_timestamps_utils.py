from nemo.collections.asr.parts.utils.decoder_timestamps_utils import ASRDecoderTimeStamps
from nemo.collections.asr.parts.utils.speaker_utils import audio_rttm_map
from nemo.collections.asr.parts.utils.manifest_utils import create_manifest


class MyASRDecoderTimeStamps(ASRDecoderTimeStamps):
    def __init__(self, cfg_diarizer):
        self.params = cfg_diarizer.asr.parameters
        self.ctc_decoder_params = cfg_diarizer.asr.ctc_decoder_parameters
        self.ASR_model_name = cfg_diarizer.asr.model_path
        self.nonspeech_threshold = self.params.asr_based_vad_threshold
        self.root_path = None
        self.run_ASR = None
        self.encdec_class = None
        self.manifest_filepath = None
        self.AUDIO_RTTM_MAP = None
    
    def set_audio_detail(self, maifest_filepath):
        self.manifest_filepath = maifest_filepath
        self.AUDIO_RTTM_MAP = audio_rttm_map(self.manifest_filepath)
        self.audio_file_list = [value['audio_filepath'] for _, value in self.AUDIO_RTTM_MAP.items()]
