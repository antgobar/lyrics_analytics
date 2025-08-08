import json
import time
import traceback
from collections.abc import Callable
from threading import Thread
from typing import Any, Protocol

from pika import BlockingConnection, URLParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from pika.spec import Basic, BasicProperties
from pydantic import BaseModel

from common.logger import setup_logger

_CONNECTION_WAIT_TIME_S = 1
_CONNECTION_ATTEMPTS = 5

logger = setup_logger(__name__)


class CallbackFunc(Protocol):
    def __call__(
        self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes
    ) -> None: ...


class Queue:
    def __init__(self, name: str, handler: CallbackFunc):
        self.name = name
        self.handler = handler
        self.channel: BlockingChannel | None = None


class Broker:
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.queues: list[Queue] = []

    def connect(self) -> BlockingChannel:
        parameters = URLParameters(self.broker_url)
        attempts = _CONNECTION_ATTEMPTS
        connection = None

        logger.info("Connecting process to RabbitMQ...")
        while attempts > 0:
            try:
                connection = BlockingConnection(parameters)
                if connection is None:
                    time.sleep(_CONNECTION_WAIT_TIME_S)
                    continue
                logger.info("✅ Connected to RabbitMQ")
                break
            except AMQPConnectionError:
                attempts -= 1
                logger.info(f"AMQPConnectionError raised - attempts left {attempts}")
                time.sleep(_CONNECTION_WAIT_TIME_S)
        else:
            logger.info("❌ Could not connect to RabbitMQ after 5 tries — exiting")
            raise ConnectionError("Could not connect to RabbitMQ after 5 attempts")

        return connection.channel()

    def register_queues(self, queues: list[Queue]):
        for queue in queues:
            queue.channel = self.connect()
            self.queues.append(queue)

    def consume(self):
        threads = []

        for queue in self.queues:
            thread = Thread(target=self._start_consumer, args=(queue,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def _start_consumer(self, queue: Queue):
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
        queue = next((q for q in self.queues if q.name == queue_name), None)
        if not queue:
            raise ValueError(f"Queue {queue_name} not registered")

        channel = self.connect()
        try:
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(body).encode("utf-8"))
        finally:
            channel.close()


def provide_handler(func: Callable[..., str], model: type[BaseModel]) -> CallbackFunc:
    def handler(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        try:
            message = json.loads(body.decode())
            if not message:
                logger.info(f"Empty message received: {body}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            print(f"Received message: {message}")
            func(**model.model_validate(message).model_dump())
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            tb = traceback.format_exc()
            logger.info(f"Error in message: {message}: {e}\n{tb}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return handler
