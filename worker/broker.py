import json
import time
from collections.abc import Callable
from multiprocessing import Process
from typing import Any

from logger import setup_logger
from pika import BlockingConnection, URLParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from pydantic import BaseModel

logger = setup_logger(__name__)

CallbackFunc = Callable[[str], None]


class Queue(BaseModel):
    name: str
    handler: CallbackFunc


class ConnectedQueue(Queue):
    channel: BlockingChannel


class Broker:
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.connected_queues: list[ConnectedQueue] = []

    def _connect(self) -> BlockingChannel:
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
            connected_queue = ConnectedQueue(name=queue.name, handler=queue.handler, channel=self._connect())
            self.connected_queues.append(connected_queue)

    def consume(self):
        processes = []

        for queue in self.connected_queues:
            process = Process(target=self._start_consumer, args=(queue,))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

    @staticmethod
    def _start_consumer(queue: ConnectedQueue):
        try:
            queue.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Interrupted")
            queue.channel.stop_consuming()
        finally:
            queue.channel.close()

    def send_message(self, queue_name: str, body: dict[str, Any]):
        queue = next((q for q in self.connected_queues if q.name == queue_name), None)
        if not queue:
            raise ValueError(f"Queue {queue_name} not registered")

        channel = self._connect()
        try:
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_publish(routing_key=queue_name, body=json.dumps(body))
        finally:
            channel.close()
