import time
import platform

from bson import ObjectId
from appscommon.logconfig import init_logging
from dotenv import load_dotenv
from nemo.collections.nlp.models import TokenClassificationModel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from asr.config import Config
from asr.entrypoints.feed_preocessor.asr_feed_processor import \
    asr_feed_processor
from asr.entrypoints.feed_preocessor.asr_translate_feed_processor import \
    asr_translate_feed_processor


speech_recognizer = None
entity_recognizer = None
text_classifier = None


class ASRFeedHandler(FileSystemEventHandler):
    def on_created(self, event):
        try:
            file_path = event.src_path
            root_path, incoming_file_name = file_path.rsplit('/', 1)
            feed_id = incoming_file_name.split("_", 1)[0]
            feed_id = ObjectId(feed_id)

            if root_path == Config.ASR_FEED_LOCATION:
                asr_feed_processor(
                    feed_id,
                    file_path,
                    entity_recognizer
                )
            elif root_path == Config.ASR_TRANSLATE_FEED_LOCATION:
                asr_translate_feed_processor(feed_id, file_path)
        except Exception as e:
            print(f"Failed to process feed with exception: {e}")


if __name__ == '__main__':
    load_dotenv()
    init_logging()
    Config.init_config()

    entity_recognizer = TokenClassificationModel.from_pretrained("ner_en_bert")
    if platform.system() == "Darwin":
        entity_recognizer.cfg['dataset']['num_workers'] = 0

    observers = []
    event_handler = ASRFeedHandler()

    for loc in [Config.ASR_FEED_LOCATION, Config.ASR_TRANSLATE_FEED_LOCATION]:
        observer = Observer()
        observers.append(observer)
        observer.schedule(event_handler, loc)
        observer.start()

    print("Listening for feeds....")
    try:
        while True:
            time.sleep(1)
    finally:
        for observer in observers:
            observer.stop()
            observer.join()
