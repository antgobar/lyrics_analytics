from config import Config
from services.broker import RabbitMQBroker
from services.broker.publisher import Producer, Publisher
from services.broker.subscriber import Consumer, Subscriber
from services.cache import ValkeyCache
from services.models import GetArtistSongsRequest, ScrapeSongLyricsRequest, SearchArtistRequest
from services.retrieval.genius import GeniusRetrieval
from services.scraper import GeniusScraper
from services.store import Store
from worker.tasks import get_artist_songs_task, scrape_lyrics_task, search_artists_task


def run():
    retrieval = GeniusRetrieval(Config.GENIUS_API_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    store = Store(Config.DATABASE_URL)
    broker = RabbitMQBroker(Config.BROKER_URL)
    subscriber = Subscriber(broker)
    publisher = Publisher(broker)
    scraper = GeniusScraper()
    cache = ValkeyCache(connection_url=Config.CACHE_URL)

    publisher.register_producer(Producer(queue_name=Config.QUEUE_SCRAPE_LYRICS_URL))

    subscriber.register_consumer(
        Consumer(
            queue_name=Config.QUEUE_SEARCH_ARTISTS,
            handler=subscriber.provide_handler(
                search_artists_task(retrieval=retrieval, store=store, cache=cache), SearchArtistRequest
            ),
        )
    )
    subscriber.register_consumer(
        Consumer(
            queue_name=Config.QUEUE_GET_ARTIST_SONGS,
            handler=subscriber.provide_handler(
                get_artist_songs_task(retrieval, store, publisher, Config.QUEUE_SCRAPE_LYRICS_URL),
                GetArtistSongsRequest,
            ),
        )
    )
    subscriber.register_consumer(
        Consumer(
            queue_name=Config.QUEUE_SCRAPE_LYRICS_URL,
            handler=subscriber.provide_handler(
                scrape_lyrics_task(scraper=scraper, store=store), ScrapeSongLyricsRequest
            ),
        )
    )

    subscriber.consume()


if __name__ == "__main__":
    run()
