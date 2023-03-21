import json
from datetime import datetime
from typing import Any
from bson import ObjectId

from pymongo import MongoClient

from lyrics_analytics.config import Config


class MongoDb:
    _instance = None

    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance = MongoClient(
            f"mongodb://{Config.MONGO_USERNAME}:{Config.MONGO_PASSWORD}@{Config.MONGO_HOST}:27017/"
        )
        return cls._instance


def get_db(db_name):
    client = MongoDb()
    return client[db_name]


def get_collection(db_name, collection_name):
    db = get_db(db_name)
    return db[collection_name]


def parse_mongo(result):
    return json.loads(MongoJSONEncoder().encode(result))


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)
