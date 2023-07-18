import json
import os
import shutil
import time

import requests
from appscommon.logconfig import init_logging
from dotenv import load_dotenv
from nemo.collections.nlp.models import TokenClassificationModel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from asr import constants
from asr.config import Config
from asr.model.diarizer import diarize
from asr.domain.asr_feed import ASRFeed, ASRFeedResult


speech_recognizer = None
entity_recognizer = None
text_classifier = None


class InputFeedEvenHandler(FileSystemEventHandler):
    def on_created(self, event):
        start = time.perf_counter()
        file_path = event.src_path
        if not os.path.isdir(file_path):
            return

        feed_id = file_path.rsplit('/', 1)[1]
        file_name = os.listdir(file_path)[0]

        try:
            file_path = shutil.move(
                file_path,
                Config.ASR_INPUT_PROCESSING_LOCATION
            )
            feed_result = ASRFeedResult()

            start_asr_perf = time.perf_counter()
            diarizer_result = diarize(os.path.join(
                file_path, file_name
            ))
            print(f'Diarizer took {time.perf_counter() - start_asr_perf} seconds')

            feed_result.transcript = diarizer_result['transcript']

            start_emotion_perf = time.perf_counter()
            response = requests.post(
                'http://127.0.0.1:5000/classify',
                json=diarizer_result
            )
            classifier_result = response.json()
            print(f'Emotion classifier took {time.perf_counter() - start_emotion_perf} seconds')

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
            # response = requests.post(
            #     'http://127.0.0.1:6000/ner',
            #     json={'inputs': [feed_result.transcript]}
            # )
            # response_data = response.json()['entities']
            entities = entity_recognizer.add_predictions([feed_result.transcript])[0]
            for token in entities.split():
                if '[' in token:
                    entity = token.split('[')
                    feed_result.entities.append(
                        (entity[0], entity[1].replace(']', ''))
                    )
            print(f'Entity extraction took {time.perf_counter() - start_entity_perf} seconds')

            shutil.move(file_path, Config.ASR_RESULTS_LOCATION)
            result_location = os.path.join(
                Config.ASR_RESULTS_LOCATION,
                feed_id
            )
            asr_feed = ASRFeed(feed_id, file_name, feed_result)
            with open(
                os.path.join(result_location, f'{feed_id}.json'),
                'w'
            ) as f:
                json.dump(asr_feed.to_dict(), f)

            print(f'{feed_id} Processed successfully.It took {time.perf_counter() - start} seconds')

        except Exception as e:
            print(f'Failed to process {feed_id} with error: {e}')
            shutil.move(file_path, f'{Config.ASR_FAILED_LOCATION}')


if __name__ == '__main__':
    load_dotenv()
    init_logging()
    Config.init_config()

    entity_recognizer = TokenClassificationModel.from_pretrained("ner_en_bert")
    # entity_recognizer.cfg['dataset']['num_workers'] = 0

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
