from common.config import Config
from common.logger import setup_logger
from common.models import GetArtistSongsRequest, ScrapeSongLyricsRequest, SearchArtistRequest
from common.store import Store
from worker.broker import Broker, Queue, provide_handler
from worker.genius import Genius
from worker.scraper import Scraper
from worker.tasks import Tasks

logger = setup_logger(__name__)


def consume():
    genius = Genius(Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    store = Store(Config.DATABASE_URL)
    broker = Broker(Config.BROKER_URL)
    scraper = Scraper()
    tasks = Tasks(
        service=genius, store=store, scraper=scraper, broker=broker, scraper_queue=Config.QUEUE_SCRAPE_LYRICS_URL
    )

    broker.register_queues(
        [
            Queue(
                name=Config.QUEUE_SEARCH_ARTISTS,
                handler=provide_handler(tasks.search_artists, SearchArtistRequest),
            ),
            Queue(
                name=Config.QUEUE_GET_ARTIST_SONGS,
                handler=provide_handler(tasks.get_artist_songs, GetArtistSongsRequest),
            ),
            Queue(
                name=Config.QUEUE_SCRAPE_LYRICS_URL,
                handler=provide_handler(tasks.scrape_lyrics, ScrapeSongLyricsRequest),
            ),
        ]
    )
    broker.consume()


if __name__ == "__main__":
    consume()
