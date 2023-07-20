from dataclasses import dataclass, asdict, field
from datetime import datetime

from bson import ObjectId

from asr.domain.entities.entity import Entity


@dataclass
class ASRFeedResult:
    transcript: str = ""
    conversation: list = field(default_factory=list)
    entities: list = field(default_factory=list)
    overall_sentiment: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class ASRFeed(Entity):
    filename: str
    status: str
    result: ASRFeedResult
    source: str = ''
    _id: str = field(default_factory=ObjectId)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = None
