import json

from redis import Redis


class CacheService:
    def __init__(self, host="localhost") -> None:
        self._redis = Redis(host)

    def get_store(self, store):
        if self._redis.get(store) is None:
            self._redis.set(store, "{}")
        return json.loads(self._redis.get(store))

    def is_stored(self, store_name, value):
        store = self.get_store(store_name)

        if value in store:
            return True
        return False

    def update_store(self, store_name, key, value):
        store = self.get_store(store_name)
        store[key] = value
        self._redis.set(store_name, json.dumps(store))

    def get_value(self, store_name, key):
        store = self.get_store(store_name)
        return store[key]
