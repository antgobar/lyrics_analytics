import json
import time

from lyrics_analytics.background.rabbitmq import RabbitService


task_id = RabbitService.submit_task(
    "find_artists",
    "coldplay"
)
