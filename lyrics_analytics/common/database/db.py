import json
from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo import MongoClient
from pymongo.results import (
    BulkWriteResult,
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)

from lyrics_analytics.config import Config


TO_SERIALISE = [
    ObjectId,
    datetime,
    BulkWriteResult,
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
]


class MongoDb:
    _instance = None

    def __new__(cls, uri: str) -> MongoClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance = MongoClient(uri)
        return cls._instance


def parse_mongo(result) -> dict | list[dict]:
    return json.loads(MongoJSONEncoder().encode(result))


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        for serialise_object in TO_SERIALISE:
            if isinstance(obj, serialise_object):
                return str(obj)
        return json.JSONEncoder.default(self, obj)


class DbClient:
    def __init__(self):
        client = MongoDb(Config.MONGO_URI)
        self.database = client[Config.DATABASE_NAME]

    def collection(self, collection_name):
        return self.database[collection_name]
