import requests
from os import environ

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv('schedule.env')
db_connection = MongoClient(
    environ.get('MONGO_DB_URL')
)[environ.get('MONGO_DB_NAME')]


collection = db_connection.get_collection('asr_feeds')

for i, data in enumerate(collection.find({})):
    print(f'Processing record {i}')
    try:
        text = data["result"]["translation"]
        response = requests.post(
            'http://127.0.0.1:8000/classify',
            json={
                'transcript': text
            }
        )
        sentiment = response.json()['overall_sentiment']
        collection.update_one(
            {'_id': data['_id']},
            {'$set': {'result.overall_sentiment': sentiment}}
        )
    except Exception as e:
        print(f"Failed for {data['_id']}", e)
