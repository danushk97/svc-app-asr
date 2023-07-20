from abc import ABC, abstractmethod

from asr.domain.entities.entity import Entity


class AbtractRespository(ABC):
    @abstractmethod
    def add(self, entity: Entity):
        raise NotImplementedError

    @abstractmethod
    def find(self, id: str):
        raise NotImplementedError

    @abstractmethod
    def list(self):
        raise NotImplementedError
