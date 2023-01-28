import json

from redis import Redis


class RedisCache:
    def __init__(self, host: str="localhost") -> None:
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

    def set_task(self, task_id):
        body = {"status": "PENDING", "data": None}
        self.red.set(task_id, json.dumps(body))

    def update_task(self, task_id, result):
        body = {"status": "SUCCESS", "data": result}
        self.red.set(task_id, json.dumps(body))

    def get_task(self, task_id):
        return self.red.get(task_id)
