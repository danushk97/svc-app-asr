import os
import time

import requests
from bson import ObjectId

from asr import constants
from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository
from asr.adapters.datasources.mongo import MongoClient
from asr.domain.entities.asr_feed import ASRFeedResult
from asr.model.diarizer import diarize


def asr_feed_processor(feed_id: ObjectId, file_path: str, entity_recognizer):
    asr_feeds = ASRFeedRepository(MongoClient.get_connection())

    try:
        start = time.perf_counter()
        asr_feeds.find_and_update_feed_status(feed_id, constants.PROCESSING)

        feed_result = ASRFeedResult()
        start_asr_perf = time.perf_counter()
        diarizer_result = diarize(file_path)
        print(
            f'Diarizer took {time.perf_counter() - start_asr_perf}'
            ' seconds'
        )
        feed_result.transcript = diarizer_result['transcript']
        start_emotion_perf = time.perf_counter()
        response = requests.post(
            'http://127.0.0.1:5000/classify',
            json=diarizer_result
        )
        classifier_result = response.json()
        print(
            'Emotion classifier took'
            f'{time.perf_counter() - start_emotion_perf} seconds'
        )
        feed_result.conversation = [
            {
                constants.SPEAKER: sentence[constants.SPEAKER],
                constants.TRANSCRIPT: sentence[constants.TEXT],
                constants.EMOTION: emotion["label"]
            }
            for sentence, emotion in zip(
                diarizer_result['conversation'],
                classifier_result['emotions']
            )
        ]
        feed_result.overall_sentiment = \
            classifier_result['overall_sentiment']
        start_entity_perf = time.perf_counter()
        entities = entity_recognizer.add_predictions(
            [feed_result.transcript]
        )[0]
        for token in entities.split():
            if '[' in token:
                entity = token.split('[')
                feed_result.entities.append(
                    (entity[0], entity[1].replace(']', ''))
                )
        print(
            f'Entity extraction took '
            f'{time.perf_counter() - start_entity_perf} seconds'
        )
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
    finally:
        os.remove(file_path)
        print(f"Removed File: {file_path}")
