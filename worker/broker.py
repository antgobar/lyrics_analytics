import json
import time
from collections.abc import Callable
from threading import Thread
from typing import Any

from logger import setup_logger
from pika import BlockingConnection, URLParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from pydantic import BaseModel, ConfigDict

logger = setup_logger(__name__)

CallbackFunc = Callable[[str], None]


class Queue(BaseModel):
    name: str
    handler: CallbackFunc


class ConnectedQueue(Queue):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    channel: BlockingChannel


class Broker:
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.connected_queues: list[ConnectedQueue] = []
        self.publisher = Publisher(self)

    def connect(self) -> BlockingChannel:
        parameters = URLParameters(self.broker_url)
        attempts = 5
        connection = None

        logger.info("Connecting process to RabbitMQ...")
        while attempts > 0:
            try:
                connection = BlockingConnection(parameters)
                if connection is None:
                    time.sleep(1)
                    continue
                logger.info("✅ Connected to RabbitMQ")
                break
            except AMQPConnectionError:
                attempts -= 1
                logger.info(f"AMQPConnectionError raised - attempts left {attempts}")
                time.sleep(1)
        else:
            logger.info("❌ Could not connect to RabbitMQ after 5 tries — exiting")
            raise ConnectionError("Could not connect to RabbitMQ after 5 attempts")

        return connection.channel()

    def register_queues(self, queues: list[Queue]):
        for queue in queues:
            connected_queue = ConnectedQueue(name=queue.name, handler=queue.handler, channel=self.connect())
            self.connected_queues.append(connected_queue)

    def consume(self):
        threads = []

        for queue in self.connected_queues:
            thread = Thread(target=self._start_consumer, args=(queue,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def _start_consumer(self, queue: ConnectedQueue):
        try:
            queue.channel.queue_declare(queue=queue.name, durable=True)
            queue.channel.basic_qos(prefetch_count=1)
            queue.channel.basic_consume(queue=queue.name, on_message_callback=queue.handler)

            logger.info(f"[*] Thread waiting for messages in queue: {queue.name}. To exit press CTRL+C")
            queue.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info(f"Interrupted consumer for queue: {queue.name}")
            queue.channel.stop_consuming()
        finally:
            queue.channel.close()

    def send_message(self, queue_name: str, body: dict[str, Any]):
        queue = next((q for q in self.connected_queues if q.name == queue_name), None)
        if not queue:
            raise ValueError(f"Queue {queue_name} not registered")

        channel = self.connect()
        try:
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(body).encode("utf-8"))
        finally:
            channel.close()


class Publisher:
    def __init__(self, broker: Broker):
        self.channel = broker.connect()
        self.queue_name = None

    def __enter__(self, queue_name, body: dict[str, Any]):
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name, durable=True)

    def __exit__(self):
        self.channel.close()

    def publish(self, body: dict[str, Any]):
        if not self.queue_name:
            raise ValueError("Queue name must be set before publishing")
        self.channel.basic_publish(exchange="", routing_key=self.queue_name, body=json.dumps(body).encode("utf-8"))
