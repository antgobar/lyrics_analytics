from services.broker import Connection
from services.logger import setup_logger
from services.models import GetArtistSongsRequest, ScrapeSongLyricsRequest, SearchArtistRequest
from services.publisher import Producer, Publisher
from services.store import Store
from src.config import Config
from worker.genius import Genius
from worker.scraper import Scraper
from worker.subscriber import Consumer, Subscriber
from worker.tasks import Tasks

logger = setup_logger(__name__)


def run():
    genius = Genius(Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    store = Store(Config.DATABASE_URL)
    broker = Connection(Config.BROKER_URL)
    subscriber = Subscriber(broker)
    publisher = Publisher(broker)
    scraper = Scraper()
    tasks = Tasks(
        service=genius,
        store=store,
        scraper=scraper,
        publisher=publisher,
        scraper_queue=Config.QUEUE_SCRAPE_LYRICS_URL,
    )

    publisher.register_producers([Producer(queue_name=Config.QUEUE_SCRAPE_LYRICS_URL)])

    subscriber.register_consumers(
        [
            Consumer(
                queue_name=Config.QUEUE_SEARCH_ARTISTS,
                handler=subscriber.provide_handler(tasks.search_artists, SearchArtistRequest),
            ),
            Consumer(
                queue_name=Config.QUEUE_GET_ARTIST_SONGS,
                handler=subscriber.provide_handler(tasks.get_artist_songs, GetArtistSongsRequest),
            ),
            Consumer(
                queue_name=Config.QUEUE_SCRAPE_LYRICS_URL,
                handler=subscriber.provide_handler(tasks.scrape_lyrics, ScrapeSongLyricsRequest),
            ),
        ],
    )
    subscriber.consume()


if __name__ == "__main__":
    run()
