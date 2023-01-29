import json

from redis import Redis


class RedisCache:
    def __init__(self, host="localhost") -> None:
        self._redis = Redis(host)

    def create_store(self, name):
        if self._redis.get(name) is None:
            store = {}
            self._redis.set(name, json.dumps(store))

    def search_store(self, store_name, value):
        searched = json.loads(self._redis.get(store_name))
        if value not in searched:
            return
        return searched[value]

    def cache_search(self, search_artist, found_artists):
        searched = json.loads(self._redis.get("searched_artists"))
        searched[search_artist] = found_artists
        self._redis.set("searched_artists", json.dumps(searched))

    def set_key(self, key, body):
        self._redis.set(key, json.dumps(body))

    def get_value(self, key, none_value):
        value = self._redis.get(key)
        if value is None:
            return none_value
        return json.loads(value)
