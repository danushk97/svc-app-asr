from appscommon.flaskutils.http.middleware import error_filter

from asr import constants
from asr.config import Config
from asr.bootstrap import bootstrap
from asr.adapters.datasources.mongo import MongoClient
from asr.adapters.respositories.asr_translate_feed_repository import \
    ASRTranslateFeedRespositoy
from asr.application.services.asr_feed_upload_service import \
    ASRFeedUploadService
from asr.adapters.datasources.http_client import ExternalAPIClient


_services = bootstrap()


@error_filter
def feed_to_asr_translate(file):
    db_connection = MongoClient.get_connection()
    repo = ASRTranslateFeedRespositoy(db_connection)
    asr_feed = _services[constants.ASR_TRNASLATE_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService(Config.ASR_TRANSLATE_FEED_LOCATION)
    ).upload_feed_content_and_save_feed(
        file.read(),
        file.filename
    )

    return asr_feed


@error_filter
def feed_to_asr_translate_from_urls(body):
    db_connection = MongoClient.get_connection()
    repo = ASRTranslateFeedRespositoy(db_connection)
    asr_feeds = _services[constants.ASR_TRNASLATE_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService(Config.ASR_TRANSLATE_FEED_LOCATION)
    ).upload_feed_content_and_save_feed_from_urls(
        body["audio_urls"]
    )

    return {
        "asr_translate_feeds": asr_feeds
    }


@error_filter
def retrieve_translate_feeds_grouped_by_status():
    db_connection = MongoClient.get_connection()
    repo = ASRTranslateFeedRespositoy(db_connection)
    feed_ids_by_status = _services[constants.ASR_TRNASLATE_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService(Config.ASR_TRANSLATE_FEED_LOCATION)
    ).retrieve_feed_ids_grouped_by_status()

    return feed_ids_by_status


@error_filter
def retrieve_translate_feed(feed_id):
    db_connection = MongoClient.get_connection()
    repo = ASRTranslateFeedRespositoy(db_connection)
    asr_feed = _services[constants.ASR_TRNASLATE_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService(Config.ASR_TRANSLATE_FEED_LOCATION)
    ).retrieve_feed(
        feed_id
    )

    return asr_feed
