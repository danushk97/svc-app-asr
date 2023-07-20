from appscommon.flaskutils.http.middleware import error_filter

from asr.bootstrap import bootstrap
from asr.adapters.datasources.mongo import MongoClient
from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository
from asr.application.services.asr_feed_upload_service import \
    ASRFeedUploadService
from asr.adapters.datasources.http_client import ExternalAPIClient
from asr import constants


_services = bootstrap()


@error_filter
def feed_to_asr(file):
    db_connection = MongoClient.get_connection()
    repo = ASRFeedRepository(db_connection)
    asr_feed = _services[constants.ASR_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService()
    ).upload_feed_content_and_save_feed(
        file.read(),
        file.filename
    )

    return asr_feed


@error_filter
def feed_to_asr_from_urls(body):
    db_connection = MongoClient.get_connection()
    repo = ASRFeedRepository(db_connection)
    asr_feeds = _services[constants.ASR_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService()
    ).upload_feed_content_and_save_feed_from_urls(
        body["audio_urls"]
    )

    return {
        "asr_feeds": asr_feeds
    }


@error_filter
def retrieve_feeds_grouped_by_status():
    db_connection = MongoClient.get_connection()
    repo = ASRFeedRepository(db_connection)
    feed_ids_by_status = _services[constants.ASR_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService()
    ).retrieve_feed_ids_grouped_by_status()

    return feed_ids_by_status


@error_filter
def retrieve_feed(feed_id):
    db_connection = MongoClient.get_connection()
    repo = ASRFeedRepository(db_connection)
    asr_feed = _services[constants.ASR_FEED_SERVICE](
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService()
    ).retrieve_feed(
        feed_id
    )

    return asr_feed
