import uuid
import json
from threading import Thread
import time

from lyrics_analytics.backend.cache import RedisCache
from lyrics_analytics.backend.message_broker import MessageBroker

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
    def __init__(self, message_broker_url, cache_host, services) -> None:
        self._message_broker = MessageBroker(message_broker_url)
        self._message_broker.callback_handler = self.callback_handler
        self._cache = RedisCache(cache_host)
        self.services = services

    def send_task(self, main, method, *args, **kwargs):
        return self.submit_task("task_queue", main, method, *args, **kwargs)

    def submit_task(self, queue, main, method, *args, **kwargs):
        task_id = str(uuid.uuid4())
        func_def = {
            "main": main,
            "method": method,
            "args": args,
            "kwargs": kwargs,
            "id": task_id
        }
        self._message_broker.send_message(queue, json.dumps(func_def))
        return task_id

    def run_task(self, main, method, *args, **kwargs):
        for service in self.services:
            service_definition = service.service()
            if main in service_definition:
                return service_definition[main][method](*args, **kwargs)

    def callback_handler(self, body):
        task_def = json.loads(body)
        self._cache.set_key(task_def["id"], {"status": "PENDING", "data": None})

        result = self.run_task(
            task_def["main"],
            task_def["method"],
            *task_def.get("args"),
            **task_def.get("kwargs")
        )

        self._cache.set_key(task_def["id"], {"status": "SUCCESS", "data": result})
        return result

    def get_task_result(self, task_id, get_now=False):
        if get_now:
            while True:
                result = self._cache.get_value(task_id, {"status": None, "data": None})
                if result["status"] == "SUCCESS":
                    return result
                time.sleep(0.5)
        return self._cache.get_value(task_id, {"status": None, "data": None})

    def start_worker(self):
        worker_thread = Thread(target=self._message_broker.consumer, args=("task_queue", ))
        worker_thread.start()
