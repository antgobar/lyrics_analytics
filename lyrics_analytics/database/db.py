import json
from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo import MongoClient

from lyrics_analytics.config import Config


class MongoDb:
    _instance = None

    def __new__(cls, uri: str) -> MongoClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance = MongoClient(uri)
        return cls._instance


def mongo_collection(collection: str):
    client = MongoDb(Config.MONGO_URI)
    database = client["lyrics_analytics"]
    return database[collection]


def parse_mongo(result) -> dict | list[dict]:
    return json.loads(MongoJSONEncoder().encode(result))


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
