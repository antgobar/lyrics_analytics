from threading import Thread

from lyrics_analytics.background.cache import RedisCache
from lyrics_analytics.background.message_broker import MessageBroker
from lyrics_analytics.background.register import REGISTERED_SERVICES


class Task:
    def __init__(self, broker_url: str=None, cache_url: str=None) -> None:
        self.cache = RedisCache()
        self.broker = MessageBroker(task_runner=self.run_task, cache=self.cache)
        self.services = REGISTERED_SERVICES

    def run_task(self, name, *args, **kwargs):
        tasks = {task.__name__: task for task in self.services}
        return tasks[name](*args, **kwargs)

    def start_worker(self):
        worker_thread = Thread(target=self.broker.worker, args=("task_queue", ))
        worker_thread.start()

    def send_task(self, name, *args, **kwargs):
        self.broker.submit_task(self, "task_queue", name, *args, **kwargs)
