import json
from typing import Any

from pika.adapters.blocking_connection import BlockingChannel

from common.broker import Connection


class Producer:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.channel: BlockingChannel | None = None


class Publisher:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.producers: list[Producer] = []

    def register_producers(self, producers: list[Producer]):
        for producer in producers:
            producer.channel = self.connection.connect()
            self.producers.append(producer)

    def send_message(self, queue_name: str, body: dict[str, Any]):
        queue = next((q for q in self.producers if q.queue_name == queue_name), None)
        if not queue:
            raise ValueError(f"Queue {queue_name} not registered")

        queue.channel.queue_declare(queue=queue_name, durable=True)
        queue.channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(body).encode("utf-8"))
