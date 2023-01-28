import uuid
import json
from threading import Thread

from lyrics_analytics.background.cache import RedisCache
from lyrics_analytics.background.message_broker import MessageBroker
from lyrics_analytics.background.register import REGISTERED_SERVICES


class Task:
    def __init__(self, broker_url=None, cache_host=None) -> None:
        self.cache = RedisCache(host=cache_host)
        self.broker = MessageBroker(broker_url, callback_handler=self.callback_handler)
        self.services = REGISTERED_SERVICES

    def run_task(self, name, *args, **kwargs):
        tasks = {task.__name__: task for task in self.services}
        return tasks[name](*args, **kwargs)

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

    def callback_handler(self, body):
        task_def = json.loads(body)
        self.cache.set_task(task_def["id"])

        result = self.run_task(
            task_def["name"],
            *task_def.get("args"),
            **task_def.get("kwargs")
        )

        self.cache.update_task(task_def["id"], result)
        return result

    def start_worker(self):
        worker_thread = Thread(target=self.broker.consumer, args=("task_queue", ))
        worker_thread.start()

    def get_task_result(self, task_id):
        return self.cache.get_task(task_id)
