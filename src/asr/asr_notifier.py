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
timestamp = 1698823964

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
        cdr_id = data.get("uuid", "")
        file_name = f"{cdr_id}.mp3"
        skill = data.get("skill", "").lower()
        is_conversation = skill not in skills

        try:
            asr_feeds = ASRFeedRepository(MongoClient.get_connection())
            asr_feed = ASRFeed(
                path.join(Config.ASR_FEED_LOCATION, file_name),
                constants.PENDING,
                ASRFeedResult() if is_conversation else ASRTranslateFeedResult(),
                cdr_id,
                skill,
                skill not in skills,
                "english" if is_conversation else "hindi",
                data.get("recordURL")
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


schedule.every(5).minutes.do(main)
main()

while True:
    schedule.run_pending()
    time.sleep(1)
