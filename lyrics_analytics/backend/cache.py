import json

from redis import Redis


class RedisCache:
    def __init__(self, host="localhost") -> None:
        self.red = Redis(host)
        self.create_search_store()

    def create_search_store(self):
        if self.red.get("searched_artists") is None:
            store = {}
            self.red.set("searched_artists", json.dumps(store))

    def search_cache(self, artist):
        searched = json.loads(self.red.get("searched_artists"))
        if artist not in searched:
            return
        return searched[artist]

    def cache_search(self, search_artist, found_artists):
        searched = json.loads(self.red.get("searched_artists"))
        searched[search_artist] = found_artists
        self.red.set("searched_artists", json.dumps(searched))

    def set_key(self, key, body):
        self.red.set(key, json.dumps(body))

    def get_value(self, key, none_value):
        value = self.red.get(key)
        if value is None:
            return none_value
        return json.loads(value)
