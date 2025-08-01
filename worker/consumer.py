import json
import time
from typing import Callable

from config import Config
from genius import GeniusService
from logger import setup_logger
from pika import BlockingConnection, URLParameters
from pika.exceptions import AMQPConnectionError
from store import Store
from tasks import Tasks

logger = setup_logger(__name__)


CallbackFunc = Callable[[str], None]


def provide_rabbitmq_handler(key: str, func: CallbackFunc):
    def handler(ch, method, properties, body):
        try:
            logger.info(body)
            message = json.loads(body.decode())
            func(message[key])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.info(f"Error in {key}: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return handler


def connect(url: str) -> BlockingConnection | None:
    parameters = URLParameters(url)
    attempts = 5
    connection = None

    logger.info("Connecting to RabbitMQ...")
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
        return None

    return connection


def consume():
    genius_service = GeniusService(
        Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN
    )
    store = Store()

    tasks = Tasks(genius_service, store)

    handle_search_artists = provide_rabbitmq_handler(
        "artist_name", tasks.search_artists
    )
    handle_get_artist_songs = provide_rabbitmq_handler(
        "artist_id", tasks.get_artist_songs
    )

    connection = connect(Config.BROKER_URL)
    channel = connection.channel()

    channel.queue_declare(queue=Config.QUEUE_SEARCH_ARTISTS, durable=True)
    channel.queue_declare(queue=Config.QUEUE_GET_ARTIST_SONGS, durable=True)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=Config.QUEUE_SEARCH_ARTISTS, on_message_callback=handle_search_artists
    )
    channel.basic_consume(
        queue=Config.QUEUE_GET_ARTIST_SONGS, on_message_callback=handle_get_artist_songs
    )

    logger.info("[*] Waiting for messages in both queues. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    consume()
