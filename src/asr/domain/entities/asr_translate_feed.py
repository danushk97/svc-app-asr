from dataclasses import dataclass, asdict

from asr.domain.entities.asr_feed import ASRFeed


@dataclass
class ASRTranslateFeedResult:
    translation: str = ''

    def to_dict(self):
        return asdict(self)


@dataclass
class ASRTranslateFeed(ASRFeed):
    result: ASRTranslateFeedResult
