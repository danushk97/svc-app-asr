from asr.application.services.asr_feed_service import ASRFeedService
from asr.domain.entities.asr_translate_feed import ASRTranslateFeed, \
    ASRTranslateFeedResult
from asr import constants


class ASRTranslateFeedService(ASRFeedService):
    def upload_feed_content_and_save_feed(
        self,
        feed_content: bytes,
        file_name: str,
        source=""
    ) -> ASRTranslateFeed:
        asr_translation_result = ASRTranslateFeedResult()
        asr_translation_feed = ASRTranslateFeed(
            file_name,
            constants.PENDING,
            asr_translation_result,
            source
        )

        self._upload_feed_content_and_save_feed(
            feed_content,
            file_name,
            asr_translation_feed
        )

        return asr_translation_feed
