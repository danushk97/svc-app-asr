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
from asr.application.text_classifier import TextClassifier
from asr.application.ner import Ner
from asr.config import Config


speech_recognizer = None
entity_recognizer = None
text_classifier = None


class InputFeedEvenHandler(FileSystemEventHandler):
    def on_created(self, event):
        file_path = event.src_path
        file_name = file_path.rsplit('/', 1)[1]
        base_file_name, ext = file_name.rsplit('.', 1)
        file_path = shutil.move(file_path, f'{Config.ASR_INPUT_PROCESSING_LOCATION}/{file_name}')
        result = {
            'transcription': [],
            'entities': {
                'query': '',
                'result': []
            }
        }

        speech_recognizer.set_audio_detail(file_path)
        data = speech_recognizer.transcribe_audio()[base_file_name]
        
        response = requests.post('http://127.0.0.1:5000/classify', json={'inputs': data['sentences']})
        response_data = response.json()['data']

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
        result['entities']['query'] = transcription_list[0]
        for token in entity_recognizer.add_predictions(transcription_list)[0].split():
            if '[' in token:
                entity = token.split('[')
                result['entities']['result'].append((entity[0], entity[1].replace(']', '')))


        result_location = os.path.join(Config.ASR_RESULTS_LOCATION, file_name)
        os.makedirs(result_location)
        with open(os.path.join(result_location, f'{base_file_name}.json'), 'w') as f:
            json.dump(result, f)
        shutil.move(file_path, f'{result_location}/{file_name}')

        print(f'{file_name} Processed successfully.')
        # for query, result in zip(queries, results):
        #     print()
        #     print(f'Query : {query}')
        #     print(f'Result: {result.strip()}\n')


if __name__ == '__main__':
    load_dotenv()
    init_logging()
    Config.init_config()
    speech_recognizer = SpeechRecognizer()
    entity_recognizer = Ner.restore_from('./models/bert_ner.nemo')
    text_classifier = TextClassifier.load_from_checkpoint(Config.TEXT_CLASSIFIER_MODEL_PATH)
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
