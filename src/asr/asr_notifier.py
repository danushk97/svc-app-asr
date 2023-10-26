import time
from os import path

import schedule
from appscommon.logconfig import init_logging
from dotenv import load_dotenv
from logging import getLogger

from asr.config import Config
from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository
from asr.adapters.datasources.mongo import MongoClient
from asr.domain.entities.asr_feed import ASRFeed, ASRFeedResult
from asr import constants


init_logging()
Config.init_config()
load_dotenv('schedule.env')
logger = getLogger(__name__)

db_connection = MongoClient.get_connection()
timestamp = 1698330720

cdr_collection = db_connection.get_collection('cdr')


def _extract_recordings():
    return cdr_collection.find(
        {
            'timestamp': {'$gt': timestamp},
            'asr_notify': {'$exists': False}
        }
    )


def extract_and_load():
    logger.info('Starting Extraction')
    records = list(_extract_recordings())
    logger.info(f'Fetch and processing {len(records)} records.')

    for data in records:
        if "recordURL" not in data:
            continue

        record_url = data['recordURL']
        file_name = record_url.rsplit('/', 1)[1]
        cdr_id = file_name.split('.')[0]

        try:
            asr_feeds = ASRFeedRepository(MongoClient.get_connection())
            asr_feed = ASRFeed(
                path.join(Config.ASR_FEED_LOCATION, file_name),
                constants.PENDING,
                ASRFeedResult(),
                cdr_id,
                data["skill"]
            )
            asr_feeds.add(asr_feed)
            cdr_collection.update_one(
                {
                    'uuid': cdr_id
                },
                {
                    '$set': {'asr_notify': "success"}
                }
            )
        except Exception as e:
            cdr_collection.update_one(
                {
                    'uuid': cdr_id
                },
                {
                    '$set': {'asr_notify': "false"}
                }
            )
            logger.error(e, exc_info=True)

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