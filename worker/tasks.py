import random
import time

from broker import Broker
from genius import Genius
from logger import setup_logger
from models import SongData
from scraper import Scraper
from store import Store

logger = setup_logger(__name__)

_STORE_WRITE_BATCH_SIZE = 50
_SLEEP_MIN_MAX = (1, 2)


class Tasks:
    def __init__(self, service: Genius, scraper: Scraper, store: Store, broker: Broker, scraper_queue: str):
        self.service = service
        self.scraper = scraper
        self.store = store
        self.broker = broker
        self.scraper_queue = scraper_queue

    def search_artists(self, artist_name: str):
        artists_found = self.service.search_artists(artist_name)
        for artist in artists_found:
            logger.info(f"Search Artists result: Name: {artist.name} GeniusArtistId: {artist.genius_artist_id})")
        self.store.save_artists(artists_found)

    def get_artist_songs(self, artist_id: str):
        logger.info(f"Retrieving songs for artist_id: {artist_id}")
        get_songs = self.service.artist_song_retriever(artist_id)
        batch: list[SongData] = []
        for song in get_songs:
            time.sleep(random.uniform(*_SLEEP_MIN_MAX))
            if len(batch) >= _STORE_WRITE_BATCH_SIZE:
                self._save_songs_batch(batch, self.scraper_queue)
            batch.append(song)

        if batch:
            self._save_songs_batch(batch, self.scraper_queue)

    def _save_songs_batch(self, songs: list[SongData], queue_name: str):
        self.store.save_songs(songs)
        for song in songs:
            self.broker.send_message(queue_name, {"lyrics_url": song.lyrics_url, "song_id": song.song_id})

    def scrape_lyrics(self, song_id: str, song_url: str):
        time.sleep(random.uniform(*_SLEEP_MIN_MAX))
        lyrics = self.scraper.get_lyrics(song_url)
        logger.info(f"Scraped Lyrics for song URL: {song_url}, Lyrics: {lyrics[:50]}...")
        self.store.save_lyrics(song_id, lyrics)
