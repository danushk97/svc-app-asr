import time
import platform

from appscommon.logconfig import init_logging
from dotenv import load_dotenv
from nemo.collections.nlp.models import TokenClassificationModel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from asr.config import Config
from asr.adapters.respositories.asr_feed_repository import ASRFeedRepository
from asr.adapters.datasources.mongo import MongoClient
from asr.domain.entities.asr_feed import ASRFeed, ASRFeedResult
from asr import constants


speech_recognizer = None
entity_recognizer = None
text_classifier = None
db_connection = None
cdr_collection = None


class ASRFeedHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path and not event.src_path.endswith(".mp3"):
            return

        try:
            print(f"Incoming {event.src_path}")
            asr_feeds = ASRFeedRepository(MongoClient.get_connection())
            file_path = event.src_path
            root_path, incoming_file_name = file_path.rsplit('/', 1)
            feed_id = incoming_file_name.split(".", 1)[0]
            skill = cdr_collection.find_one({
                "uuid": feed_id
            })['skill']
            asr_feed = ASRFeed(
                file_path,
                constants.PENDING,
                ASRFeedResult(),
                feed_id,
                skill
            )
            asr_feeds.add(asr_feed)
            cdr_collection.update_one(
                {
                    'uuid': feed_id
                },
                {
                    '$set': {'asr_notify': "success"}
                }
            )
        except Exception as e:
            cdr_collection.update_one(
                {
                    '_id': feed_id
                },
                {
                    '$set': {'asr_notify': "failed"}
                }
            )
            print(f"Failed to process feed with exception: {e}")


if __name__ == '__main__':
    load_dotenv()
    init_logging()
    Config.init_config()
    db_connection = MongoClient.get_connection()
    cdr_collection = db_connection.get_collection('cdr')

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
