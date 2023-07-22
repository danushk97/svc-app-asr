from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository


class ASRTranslateFeedRespositoy(ASRFeedRepository):
    def __init__(self, connection=None) -> None:
        self._connection = connection.asr_translate_feeds
