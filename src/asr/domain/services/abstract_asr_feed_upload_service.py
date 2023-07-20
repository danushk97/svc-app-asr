from abc import ABC


class AbstractASRFeedUploadService(ABC):
    def upload(self, feed_content: bytes, file_name: str) -> None:
        raise NotImplementedError
