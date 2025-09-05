from typing import Type

from pika.adapters.blocking_connection import BlockingChannel
from pydantic import BaseModel

from services.broker import Connection


class Producer:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.channel: BlockingChannel | None = None
        self.model: Type[BaseModel] | None = None


class Publisher:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.producers: list[Producer] = []

    def register_producers(self, producers: list[Producer]):
        for producer in producers:
            producer.channel = self.connection.connect()
            self.producers.append(producer)

    def send_message(self, queue_name: str, data: BaseModel):
        producer = next((q for q in self.producers if q.queue_name == queue_name), None)
        if not producer or not producer.channel:
            raise ValueError(f"Queue {queue_name} not registered")

        producer.channel.queue_declare(queue=queue_name, durable=True)
        producer.channel.basic_publish(exchange="", routing_key=queue_name, body=data.model_dump_json().encode("utf-8"))

    def __getattr__(self, name: str):
        def dynamic_method(data: BaseModel):
            self.send_message(name.lower(), data)

        return dynamic_method
