import json
from datetime import datetime
from typing import Any
from bson import ObjectId

from pymongo import MongoClient

from lyrics_analytics.config import Config


class MongoDb:
    _instance = None

    def __new__(cls, uri):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance = MongoClient(uri)
        return cls._instance


def mongo_collection(collection: str):
    client = MongoDb(Config.MONGO_URI)
    database = client["lyrics_analytics"]
    return database[collection]


def parse_mongo(result):
    return json.loads(MongoJSONEncoder().encode(result))


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)
