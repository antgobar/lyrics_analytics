import os

from lyrics_analytics.background.task import Task


if __name__ == "__name__":
    task = Task(
        broker_url=os.getenv("BROKER_URL", "amqp://guest:guest@localhost:5672/"),
        cache_host=os.getenv("CACHE_HOST", "localhost")
    )
    task.start_worker()
