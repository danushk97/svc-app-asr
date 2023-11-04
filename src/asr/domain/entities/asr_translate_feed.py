from dataclasses import dataclass, asdict

from asr.domain.entities.asr_feed import ASRFeed


@dataclass
class ASRTranslateFeedResult:
    translation: str = ''
    overall_sentiment: str = ''

    def to_dict(self):
        return asdict(self)


@dataclass
class ASRTranslateFeed(ASRFeed):
    result: ASRTranslateFeedResult
