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
            'status': 'pending'
        },
        {
            '_id': 1,
            'skill': 1,
            'filename': 1
        }
    ).limit(1000)


def extract_and_load():
    logger.info('Starting Extraction!!!!!')
    asr_feeds = list(_extract_recordings('asr_feeds'))
    asr_translate_feeds = list(_extract_recordings('asr_translate_feeds'))
    logger.info(
        f'Fetch and processing {len(asr_feeds + asr_translate_feeds)} records.'
    )

    for data in asr_feeds:
        try:
            asr_feed_processor(
                data['_id'],
                data['filename'],
                entity_recognizer
            )
        except Exception as e:
            logger.error(e, exc_info=True)

    for data in asr_translate_feeds:
        try:
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
schedule.every(1).hour.do(main)


while True:
    schedule.run_pending()
    time.sleep(1)
