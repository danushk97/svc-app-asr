from io import BytesIO

from appscommon.flaskutils.http.middleware import error_filter

from asr.bootstrap import bootstrap
from asr import constants


_services = bootstrap()


@error_filter
def feed_input(file):
    audio_bytes = BytesIO(file.read())
    _services[constants.ASR_FEED_SERVICE]().feed(
        audio_bytes,
        file.filename
    )
    return {
        'message': 'Input feed was successful.'
    }


@error_filter
def feed_input_from_urls(body):
    _services[constants.ASR_FEED_SERVICE]().feed_from_urls(
        body["audio_urls"]
    )
    return {
        'message': 'Input feed was successful.'
    }


@error_filter
def retrieve_feeds_grouped_by_status():
    feed_status = _services[constants.ASR_FEED_SERVICE]().\
        retrieve_feeds_grouped_by_status()
    return feed_status


@error_filter
def retrieve_feed(feed_id):
    feed_result = _services[constants.ASR_FEED_SERVICE]().retrieve_feed(
        feed_id
    )
    return feed_result
