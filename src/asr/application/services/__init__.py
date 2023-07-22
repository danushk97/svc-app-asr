from asr.application.services.asr_feed_service import ASRFeedService
from asr.application.services.asr_translate_feed_service import \
    ASRTranslateFeedService
from asr import constants


SERVICES = {
    constants.ASR_FEED_SERVICE: ASRFeedService,
    constants.ASR_TRNASLATE_FEED_SERVICE: ASRTranslateFeedService
}
