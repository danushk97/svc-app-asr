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


db_connection = MongoClient(
    environ.get('MONGO_DB_URL')
)[environ.get('DB_NAME')]


cdr_collection = db_connection.get_collection('cdr')
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
    past_time = datetime.now() - timedelta(minutes=45)
    pipeline[1]['$match']['time']['$gte'] = past_time

    return cdr_collection.aggregate(pipeline)


def extract_and_load():
    logger.info('Starting Extraction')
    repo = ASRFeedRepository(db_connection)
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
