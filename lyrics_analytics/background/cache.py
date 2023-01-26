import json

from redis import Redis


class RedisCache:
    def __init__(self, connection_url: str=None) -> None:
        self.connection_url = connection_url
        self.red = Redis()
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

    def set_task(self, task_id):
        self.red.set(task_id, "PENDING")

    def update_task(self, task_id, result):
        self.red.set(task_id, json.dumps(result))

    def get_task_result(self, task_id):
        return self.red.get(task_id)
