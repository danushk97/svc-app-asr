from logging import getLogger

from asr.domain.datasources.abstract_http_client import AbstractHTTPClient

import requests


_logger = getLogger(__name__)


class ExternalAPIClient(AbstractHTTPClient):
    def send_request(
        self,
        http_method: str,
        url: str,
        return_raw_response=True,
        **kwagrs
    ):
        try:
            response = getattr(
                requests,
                http_method.lower()
            )(url, **kwagrs)
            response.raise_for_status()
        except requests.HTTPError as err:
            _logger.error(err, exc_info=True)
        except requests.RequestException as req_err:
            _logger.error(req_err, exc_info=True)

        if not return_raw_response:
            return response.json()

        return response.content
