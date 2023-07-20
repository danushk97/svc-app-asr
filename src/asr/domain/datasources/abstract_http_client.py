from abc import ABC, abstractmethod


class AbstractHTTPClient(ABC):
    @abstractmethod
    def send_request(
        self,
        http_method: str,
        url: str,
        return_raw_response=True,
        **kwagrs
    ):
        raise NotImplementedError
