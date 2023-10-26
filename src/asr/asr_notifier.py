import time
from os import path

import schedule
from appscommon.logconfig import init_logging
from dotenv import load_dotenv
from logging import getLogger

from asr.config import Config
from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository
from asr.adapters.respositories.asr_translate_feed_repository import \
    ASRTranslateFeedRespositoy
from asr.adapters.datasources.mongo import MongoClient
from asr.domain.entities.asr_feed import ASRFeed, ASRFeedResult
from asr.domain.entities.asr_translate_feed import ASRTranslateFeed, \
    ASRTranslateFeedResult
from asr import constants


init_logging()
Config.init_config()
load_dotenv('schedule.env')
logger = getLogger(__name__)
skills = [
    "telesales_goa",
    "telesale_goa",
    "telesale_bang",
    "LSQINTERNATIONAL",
    "LSQKCE2",
    "LSQINTERNATIONAL",
    "MMTBANG",
    "goa1",
    "goa2",
    "goa3",
    "offsite1",
    "offsite2",
    "goa1",
    "goa2",
    "goa3",
    "offsite",
    "Admin_BCC",
    "Admin_GCC",
    "LAQDIGITAL"
]
skills = [skill.lower() for skill in skills]

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
        skill = data.get("skill", "")
        try:
            if skill.lower() in skills:
                asr_translate_feed_repo = ASRTranslateFeedRespositoy(
                    MongoClient.get_connection()
                )
                asr_translate_feed = ASRTranslateFeed(
                    filename=path.join(Config.ASR_FEED_LOCATION, file_name),
                    status=constants.PENDING,
                    result=ASRTranslateFeedResult(),
                    cdr_id=cdr_id,
                    skill=data.get("skill", "")
                )
                asr_translate_feed_repo.add(asr_translate_feed)
            else:
                asr_feeds = ASRFeedRepository(MongoClient.get_connection())
                asr_feed = ASRFeed(
                    path.join(Config.ASR_FEED_LOCATION, file_name),
                    constants.PENDING,
                    ASRFeedResult(),
                    cdr_id,
                    data.get("skill", "")
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
main()

while True:
    schedule.run_pending()
    time.sleep(1)
