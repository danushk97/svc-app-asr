import json
import os
import shutil
import time

import requests
from appscommon.logconfig import init_logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

from asr import constants
from asr.application.speech_recognizer import SpeechRecognizer
from asr.config import Config


speech_recognizer = None
entity_recognizer = None
text_classifier = None


class InputFeedEvenHandler(FileSystemEventHandler):
    def on_created(self, event):
        start = time.perf_counter()
        file_path = event.src_path
        file_name = file_path.rsplit('/', 1)[1]
        base_file_name, ext = file_name.rsplit('.', 1)

        try:
            file_path = shutil.move(file_path, f'{Config.ASR_INPUT_PROCESSING_LOCATION}/{file_name}')
            result = {
                'transcription': [],
                'entities': {
                    'query': '',
                    'result': []
                }
            }

            start_asr_perf = time.perf_counter()
            speech_recognizer.set_audio_detail(file_path)
            data = speech_recognizer.transcribe_audio()[base_file_name]
            print(f'ASR took {time.perf_counter() - start_asr_perf} seconds')

            start_emotion_perf = time.perf_counter()
            response = requests.post('http://127.0.0.1:5000/classify', json={'inputs': data['sentences']})
            response_data = response.json()['data']
            print(f'Emotion classifier took {time.perf_counter() - start_emotion_perf} seconds')

            result['transcription'] = [
                {
                    constants.SPEAKER: sentence[constants.SPEAKER],
                    constants.TRANSCRIPT: sentence[constants.TEXT],
                    constants.EMOTION: emotion["label"]
                }
                for sentence, emotion in zip(data['sentences'], response_data)
            ]
            # for sentence in data['sentences']:
            #     print(f'{sentence["speaker"]}: {sentence["text"]}')

            transcription_list = [data['transcription']]
            # result['classification'] = TextClassifier.predict_labels(transcription_list, text_classifier)

            # queries = [
            #     'The Adventures of Tom Sawyer by Mark Twain is an 1876 novel about a young boy growing up along the Mississippi River.'
            # ]
            start_entity_perf = time.perf_counter()
            result['entities']['query'] = transcription_list[0]
            response = requests.post('http://127.0.0.1:6000/ner', json={'inputs': transcription_list})
            response_data = response.json()['data']
            for token in response_data[0].split():
                if '[' in token:
                    entity = token.split('[')
                    result['entities']['result'].append((entity[0], entity[1].replace(']', '')))
            print(f'Entity extraction took {time.perf_counter() - start_entity_perf} seconds')

            result_location = os.path.join(Config.ASR_RESULTS_LOCATION, file_name)
            os.makedirs(result_location)
            with open(os.path.join(result_location, f'{base_file_name}.json'), 'w') as f:
                json.dump(result, f)
            shutil.move(file_path, f'{result_location}/{file_name}')

            print(f'{file_name} Processed successfully.It took {time.perf_counter() - start} seconds')
            # for query, result in zip(queries, results):
            #     print()
            #     print(f'Query : {query}')
            #     print(f'Result: {result.strip()}\n')
        except Exception as e:
            print(f'Failed to process {base_file_name} with error: {e}')
            shutil.move(file_path, f'{Config.ASR_FAILED_LOCATION}/{file_name}')

if __name__ == '__main__':
    load_dotenv()
    init_logging()
    Config.init_config()
    speech_recognizer = SpeechRecognizer()
    # entity_recognizer = Ner.from_pretrained('ner_en_bert')
    # text_classifier = TextClassifier.load_from_checkpoint(Config.TEXT_CLASSIFIER_MODEL_PATH)
    event_handler = InputFeedEvenHandler()
    observer = Observer()
    observer.schedule(event_handler, Config.ASR_INPUT_FEED_LOCATION, recursive=True)
    observer.start()
    print("Listening for feeds....")
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
