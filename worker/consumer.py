import json

from broker import Broker, Queue
from config import Config
from genius import Genius
from logger import setup_logger
from scraper import Scraper
from store import Store
from tasks import Tasks

logger = setup_logger(__name__)


def consume():
    genius = Genius(Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    store = Store(Config.DATABASE_URL)
    broker = Broker(Config.BROKER_URL)
    scraper = Scraper()
    tasks = Tasks(service=genius, store=store, scraper=scraper, broker=broker)

    broker.register_queues(
        [
            Queue(
                name=Config.QUEUE_SEARCH_ARTISTS,
                handler=provide_search_artists(tasks),
            ),
            Queue(
                name=Config.QUEUE_GET_ARTIST_SONGS,
                handler=provide_get_artist_songs(tasks, Config.QUEUE_SCRAPE_LYRICS_URL),
            ),
            Queue(
                name=Config.QUEUE_SCRAPE_LYRICS_URL,
                handler=provide_scrape_lyrics(tasks),
            ),
        ]
    )
    broker.consume()


def provide_search_artists(tasks: Tasks):
    def handler(ch, method, properties, body):
        try:
            logger.info(body)
            message = json.loads(body.decode())
            if not message:
                logger.info(f"Empty message received: {body}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            tasks.search_artists(message["artist_name"])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.info(f"Error in message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return handler


def provide_get_artist_songs(tasks: Tasks, scraper_queue: str):
    def handler(ch, method, properties, body):
        try:
            logger.info(body)
            message = json.loads(body.decode())
            tasks.get_artist_songs(message["artist_id"], scraper_queue)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.info(f"Error in message: {message}: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return handler


def provide_scrape_lyrics(tasks: Tasks):
    def handler(ch, method, properties, body):
        try:
            logger.info(body)
            message = json.loads(body.decode())
            tasks.scrape_lyrics(message["song_id"], message["lyrics_url"])
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.info(f"Error in message: {message}: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return handler


if __name__ == "__main__":
    consume()
