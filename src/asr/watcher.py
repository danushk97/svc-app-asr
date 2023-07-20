import time
import os

import requests
from bson import ObjectId
from appscommon.logconfig import init_logging
from dotenv import load_dotenv
from nemo.collections.nlp.models import TokenClassificationModel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from asr import constants
from asr.config import Config
from asr.model.diarizer import diarize
from asr.domain.entities.asr_feed import ASRFeedResult
from asr.adapters.datasources.mongo import MongoClient
from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository


speech_recognizer = None
entity_recognizer = None
text_classifier = None


class InputFeedEvenHandler(FileSystemEventHandler):
    def on_created(self, event):
        start = time.perf_counter()
        file_path = event.src_path

        incoming_file_name = file_path.rsplit('/', 1)[1]
        feed_id, file_name = incoming_file_name.split("_", 1)
        asr_feeds = ASRFeedRepository(MongoClient.get_connection(
            Config.MONGO_DB_NAME
        ))

        try:
            asr_feeds.find_and_update_feed_status(
                ObjectId(feed_id),
                constants.PROCESSING
            )

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
                ObjectId(feed_id), feed_result, constants.COMPLETED
            )
            print(
                f'{feed_id} Processed successfully.It took '
                f'{time.perf_counter() - start} seconds'
            )

        except Exception as e:
            print(f'Failed to process {feed_id} with error: {e}')
            asr_feeds.find_and_update_feed_status(
                ObjectId(feed_id),
                constants.FAILED
            )
        finally:
            os.remove(file_path)
            print(f"Removed File: {file_path}")


if __name__ == '__main__':
    load_dotenv()
    init_logging()
    Config.init_config()

    entity_recognizer = TokenClassificationModel.from_pretrained("ner_en_bert")
    entity_recognizer.cfg['dataset']['num_workers'] = 0

    event_handler = InputFeedEvenHandler()
    observer = Observer()
    observer.schedule(
        event_handler,
        Config.ASR_INPUT_FEED_LOCATION,
        recursive=True
    )
    observer.start()
    print("Listening for feeds....")
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
