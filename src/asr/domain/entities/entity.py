from dataclasses import dataclass, asdict


@dataclass
class Entity:
    def to_dict(self):
        return asdict(self)
