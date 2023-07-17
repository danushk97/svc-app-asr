from dataclasses import dataclass, asdict, field


@dataclass
class ASRFeedResult:
    transcript: str = ''
    conversation: list = field(default_factory=list)
    entities: list = field(default_factory=list)
    overall_sentiment: str = ''


@dataclass
class ASRFeed:
    id: str
    filename: str
    result: ASRFeedResult

    def to_dict(self):
        return asdict(self)
