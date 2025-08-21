import json
import traceback
from collections.abc import Callable
from threading import Thread
from typing import Protocol

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from pydantic import BaseModel

from common.broker import Connection
from common.logger import setup_logger

logger = setup_logger(__name__)


class CallbackFunc(Protocol):
    def __call__(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None: ...


class Consumer:
    def __init__(self, queue_name: str, handler: CallbackFunc):
        self.queue_name = queue_name
        self.handler = handler
        self.channel: BlockingChannel | None = None


class Subscriber:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.consumers: list[Consumer] = []

    def register_consumers(self, consumers: list[Consumer]):
        for consumer in consumers:
            consumer.channel = self.connection.connect()
            self.consumers.append(consumer)

    def consume(self):
        threads = []

        for queue in self.consumers:
            thread = Thread(target=self._start_consumer, args=(queue,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def _start_consumer(self, consumer: Consumer):
        try:
            consumer.channel.queue_declare(queue=consumer.queue_name, durable=True)
            consumer.channel.basic_qos(prefetch_count=1)
            consumer.channel.basic_consume(queue=consumer.queue_name, on_message_callback=consumer.handler)

            logger.info("[*] Thread waiting for messages in queue: %s. To exit press CTRL+C", consumer.queue_name)
            consumer.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Interrupted consumer for queue: %s", consumer.queue_name)
            consumer.channel.stop_consuming()
        finally:
            consumer.channel.close()

    @staticmethod
    def provide_handler(func: Callable[..., str], model: type[BaseModel]) -> CallbackFunc:
        def handler(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):  # noqa: ARG001
            try:
                message = json.loads(body.decode())
                if not message:
                    logger.info("Empty message received: %s", body)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    return
                func(**model.model_validate(message).model_dump())
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                tb = traceback.format_exc()
                logger.info("Error in message: %s: %s\n%s", message, e, tb)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        return handler
