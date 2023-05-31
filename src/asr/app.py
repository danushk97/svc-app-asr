from flask import Flask

from appscommon.flaskutils.confighelper import register_blueprints
from appscommon.logconfig import init_logging

# from asr.application.speech_recognizer import SpeechRecognizer
# from asr.application.text_classifier import TextClassifier
# from asr.application.ner import Ner
from asr.bootstrap import bootstrap
from asr.config import Config
from asr.entrypoints.http import ROUTE_MODULES


def main():
    init_logging()
    bootstrap()
    Config.init_config()
    app = Flask(__name__)
    register_blueprints(app, ROUTE_MODULES)

    return app
    # sr = SpeechRecognizer()
    # sr.set_audio_detail('/Users/danush/dev/svc-app-asr/src/asr/incoming/audio-7.wav')
    # data = sr.transcribe_audio()['audio-7']

    # for sentence in data['sentences']:
    #     print(f'{sentence["speaker"]}: {sentence["text"]}')

    # text_classifier = TextClassifier.load_from_checkpoint(Config.TEXT_CLASSIFIER_MODEL_PATH)
    # TextClassifier.predict_labels(
    #     [data['transcription']],
    #     text_classifier
    # )
    # ner_model = Ner.restore_from('bert_ner.nemo')
    # results = ner_model.add_predictions(queries)
    # queries = [
    #     "The Adventures of Tom Sawyer by Mark Twain is an 1876 novel about a young boy growing up along the Mississippi River."
    # ]
    # for query, result in zip(queries, results):
    #     print()
    #     print(f'Query : {query}')
    #     print(f'Result: {result.strip()}\n')


if __name__ == '__main__':
    main()
