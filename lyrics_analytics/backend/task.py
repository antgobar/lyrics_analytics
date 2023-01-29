import uuid
import json
from threading import Thread

from lyrics_analytics.backend.cache import RedisCache
from lyrics_analytics.backend.message_broker import MessageBroker
from lyrics_analytics.services.genius_api import genius_service


def services():
    genius = genius_service()
    return {
        genius.find_artists.__name__: genius.find_artists,
        genius.get_artist_songs.__name__: genius.get_artist_songs
    }


# Do something with this
# class SomeClass:
#     def do_something(self):
#         return "some stuff"
#
# some = SomeClass()
# some.__dict__
# dir(some)
# SomeClass.__dict__


class Task:
    def __init__(self, broker_url=None, cache_host=None) -> None:
        self.broker = MessageBroker(broker_url)
        self.broker.callback_handler = self.callback_handler
        self.cache = RedisCache(host=cache_host)
        self.services = services()

    def send_task(self, name, *args, **kwargs):
        return self.submit_task("task_queue", name, *args, **kwargs)

    def submit_task(self, queue, name, *args, **kwargs):
        task_id = str(uuid.uuid4())
        func_def = {
            "name": name,
            "args": args,
            "kwargs": kwargs,
            "id": task_id
        }
        self.broker.send_message(queue, json.dumps(func_def))
        return task_id

    def run_task(self, name, *args, **kwargs):
        return self.services[name](*args, **kwargs)

    def callback_handler(self, body):
        task_def = json.loads(body)
        self.cache.set_key(task_def["id"], {"status": "PENDING", "data": None})

        result = self.run_task(
            task_def["name"],
            *task_def.get("args"),
            **task_def.get("kwargs")
        )

        self.cache.set_key(task_def["id"], {"status": "SUCCESS", "data": result})
        return result

    def get_task_result(self, task_id):
        return self.cache.get_value(task_id, {"status": None, "data": None})

    def start_worker(self):
        worker_thread = Thread(target=self.broker.consumer, args=("task_queue", ))
        worker_thread.start()
