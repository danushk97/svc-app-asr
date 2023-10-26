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


init_logging()
Config.init_config()
load_dotenv('schedule.env')
logger = getLogger(__name__)
speech_recognizer = None
entity_recognizer = None
text_classifier = None
entity_recognizer = TokenClassificationModel.from_pretrained("ner_en_bert")
if platform.system() == "Darwin":
    entity_recognizer.cfg['dataset']['num_workers'] = 0

db_connection = MongoClient(
    environ.get('MONGO_DB_URL')
)[environ.get('DB_NAME')]


cdr_collection = db_connection.get_collection('cdr')
pipeline = [
    {
        '$project': {
            '_id': 1,
            'skill': 1,
            'filename': 1
        }
    }
]


def _extract_recordings():
    return db_connection.get_collection('asr_feeds').find(
        {
            'status': 'pending'
        },
        {
            '_id': 1,
            'skill': 1,
            'filename': 1
        }
    ).limit(100)


def extract_and_load():
    logger.info('Starting Extraction')
    records = list(_extract_recordings())
    logger.info(f'Fetch and processing {len(records)} records.')

    for data in records:
        try:
            if data['skill'] == 'telesales_goa':
                asr_feed_processor(
                    data['_id'],
                    data['filename'],
                    entity_recognizer
                )
            elif data['skill'] == '':
                asr_translate_feed_processor(data['_id'], data['filename'])
        except Exception as e:
            logger.error(e, exc_info=True)

    logger.info('Completed Uploading to asr feed.')


def main():
    try:
        extract_and_load()
    except Exception as err:
        logger.error(f'Feed upload failed with exception:{err}', exc_info=True)


schedule.every(1).day.do(main)


while True:
    schedule.run_pending()
    time.sleep(1)
