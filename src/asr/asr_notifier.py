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
from asr.domain.entities.asr_translate_feed import ASRTranslateFeedResult
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
            "uuid": {
                "$in": [
                    "81a32db4-4c24-4691-a4b1-8ca3547687bb",
                    "0b1dfb63-b34e-42d6-bd18-242e4d965c5c",
                    "8de82f72-53e4-4728-a941-97054bc19a73",
                    "35ad6c85-9d49-4dac-8cc4-8788b0986caf",
                    "65261e49-6c02-46c7-8805-bad5093eafa8",
                    "2dd63fb7-013c-4828-90f5-967417244593",
                    "9d266def-82c2-4f50-8926-8a10331fd2a6",
                    "85bcc4af-f20c-4828-b4e1-2b002d064987",
                    "962f808b-3309-4336-8980-09c00d91aec4",
                    "123102c5-10ab-483a-a642-5f389824af3b",
                    "b1359e26-07ef-4ae9-a461-04d452413234",
                    "17a350b1-dd0e-40fe-9814-c8f641a89fcd",
                    "fdf3f662-f63f-4a10-b144-fa0952247a3c",
                    "569a7008-2438-402e-b673-f9797b67b514",
                    "20e8ad87-0c20-45e1-82e2-8c0c6b09bd39",
                    "a06ab3e2-9ae3-4860-a360-6cf54072f2b4",
                    "5082366d-a506-4eb0-9606-a0c3f4f6a8c5"
                ]
            }
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
