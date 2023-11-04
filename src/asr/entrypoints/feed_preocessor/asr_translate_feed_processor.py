import time
import requests

from bson import ObjectId

from asr import constants
from asr.adapters.datasources.mongo import MongoClient
from asr.adapters.respositories.asr_translate_feed_repository import \
    ASRTranslateFeedRespositoy
from asr.domain.entities.asr_translate_feed import ASRTranslateFeedResult
from asr.model.translator import translate


def asr_translate_feed_processor(feed_id: ObjectId, file_path: str):
    asr_feeds = ASRTranslateFeedRespositoy(MongoClient.get_connection())
    try:
        start = time.perf_counter()
        asr_feeds.find_and_update_feed_status(
            feed_id,
            constants.PROCESSING
        )

        feed_result = ASRTranslateFeedResult('')
        start_translation_perf = time.perf_counter()
        translation_result = translate(file_path)
        print(
            f'Translation took {time.perf_counter() - start_translation_perf}'
            ' seconds'
        )
        feed_result.translation = translation_result['text']
        start_emotion_perf = time.perf_counter()
        response = requests.post(
            'http://127.0.0.1:8000/classify',
            json={
                'transcript': translation_result['text'],
                'messages': []
            }
        )
        print(
            'Emotion classifier took'
            f'{time.perf_counter() - start_emotion_perf} seconds'
        )
        if response.status_code == 200:
            response = response.json()
            feed_result.overall_sentiment = response.get('overall_sentiment', '')

        asr_feeds.find_and_update_feed_result_and_status(
            feed_id, feed_result, constants.COMPLETED
        )
        print(
            f'{file_path} was Processed successfully.It took '
            f'{time.perf_counter() - start} seconds'
        )
    except Exception as e:
        print(f'Failed to process {feed_id} with error: {e}')
        asr_feeds.find_and_update_feed_status(feed_id, constants.FAILED)
