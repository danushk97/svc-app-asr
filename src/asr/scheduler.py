import time
from os import environ
from logging import getLogger
from datetime import datetime, timedelta

import schedule
from pymongo import MongoClient
from dotenv import load_dotenv
from appscommon.logconfig import init_logging

from asr.config import Config
from asr.application.services.asr_feed_service import ASRFeedService
from asr.application.services.asr_feed_upload_service import \
    ASRFeedUploadService
from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository
from asr.adapters.datasources.http_client import ExternalAPIClient


init_logging()
Config.init_config()
load_dotenv('schedule.env')
logger = getLogger(__name__)


cdr_collection = MongoClient(
    environ.get('RECORDINGS_DB_URL')
)[environ.get('RECORDINGS_DB_NAME')].get_collection('cdr')
asr_feed_db = MongoClient()['myFirstDatabase']
pipeline = [
    {
        '$project': {
            '_id': 1,
            'recordURL': 1,
            'asr_notify': 1,
            'time': {
                '$toDate': '$startstamp'
            }
        }
    },
    {
        '$match': {
            'recordURL': {
                '$exists':  True
            },
            'asr_notify': {
                '$ne': 'success'
            },
            'time': {
                '$gte': ''
            }
        }
    }
]


def _extract_recordings():
    one_hour_ago = datetime.now() - timedelta(hours=1)
    pipeline[1]['$match']['time']['$gte'] = one_hour_ago

    return cdr_collection.aggregate(pipeline)


def extract_and_load():
    logger.info('Starting Extraction')
    repo = ASRFeedRepository(asr_feed_db)
    asr_feeds = ASRFeedService(
        repo,
        ExternalAPIClient(),
        ASRFeedUploadService(Config.ASR_FEED_LOCATION)
    )
    records = list(_extract_recordings())
    logger.info(f'Fetch and processing {len(records)} records.')

    for data in records:
        asr_notify = 'success'

        try:
            asr_feeds.upload_feed_content_and_save_feed_from_urls(
                [data['recordURL']]
            )
        except Exception as e:
            logger.error(e, exc_info=True)
            asr_notify = 'failed'

        cdr_collection.update_one(
            {
                '_id': data['_id']
            },
            {
                '$set': {'asr_notify': asr_notify}
            }
        )
    logger.info('Completed Uploading to asr feed.')


def main():
    try:
        extract_and_load()
    except Exception as err:
        logger.error(f'Feed upload failed with exception:{err}', exc_info=True)


schedule.every(30).minutes.do(main)


while True:
    schedule.run_pending()
    time.sleep(1)
