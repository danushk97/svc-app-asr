import time
from os import environ
import platform
from logging import getLogger

import schedule
from pymongo import MongoClient
from dotenv import load_dotenv
from appscommon.logconfig import init_logging
from nemo.collections.nlp.models import TokenClassificationModel

from asr.config import Config
from asr.entrypoints.feed_preocessor.asr_feed_processor import \
    asr_feed_processor
from asr.entrypoints.feed_preocessor.asr_translate_feed_processor import \
    asr_translate_feed_processor


load_dotenv('schedule.env')
init_logging()
Config.init_config()
logger = getLogger(__name__)
entity_recognizer = TokenClassificationModel.from_pretrained("ner_en_bert")
if platform.system() == "Darwin":
    entity_recognizer.cfg['dataset']['num_workers'] = 0
db_connection = MongoClient(
    environ.get('MONGO_DB_URL')
)[environ.get('MONGO_DB_NAME')]


def _extract_recordings(collection_name):
    return db_connection.get_collection(collection_name).find(
        {
            "$and": [
                {
                    "cdr_id": {
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
                },
                {
                    "status": "pending"
                }
            ]
        },
        {
            "_id": 1,
            "skill": 1,
            "filename": 1,
            "conversation": 1
        }
    )


def extract_and_load():
    logger.info('Starting Extraction!!!!!')
    asr_feeds = list(_extract_recordings('asr_feeds'))
    logger.info(
        f'Fetch and processing {len(asr_feeds)} records.'
    )

    for data in asr_feeds:
        try:
            if data["conversation"]:
                asr_feed_processor(
                    data['_id'],
                    data['filename'],
                    entity_recognizer
                )
            else:
                asr_translate_feed_processor(data['_id'], data['filename'])
        except Exception as e:
            logger.error(e, exc_info=True)

    logger.info('Completed Uploading to asr feed.')


def main():
    try:
        extract_and_load()
    except Exception as err:
        logger.error(f'Feed upload failed with exception:{err}', exc_info=True)


main()
schedule.every(5).minutes.do(main)


while True:
    schedule.run_pending()
    time.sleep(1)
