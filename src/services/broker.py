import time

from pika import BlockingConnection, URLParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError

from services.logger import setup_logger

_CONNECTION_WAIT_TIME_S = 1
_CONNECTION_ATTEMPTS = 5

logger = setup_logger(__name__)


class Connection:
    def __init__(self, broker_url: str):
        self.broker_url = broker_url

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
                logger.info("AMQPConnectionError raised - attempts left %s", attempts)
                time.sleep(_CONNECTION_WAIT_TIME_S)
        else:
            logger.info("❌ Could not connect to RabbitMQ after 5 tries — exiting")
            raise ConnectionError("Could not connect to RabbitMQ after 5 attempts")

        return connection.channel()
