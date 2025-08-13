import random
import time
from typing import Any, Protocol

from common.logger import setup_logger
from common.models import ArtistData, SongData
from worker.genius import Genius
from worker.scraper import Scraper

logger = setup_logger(__name__)

_STORE_WRITE_BATCH_SIZE = 50
_SLEEP_MIN_MAX = (1, 2)


class Store(Protocol):
    def save_artists(self: list[ArtistData]): ...

    def save_songs(self: list[SongData]): ...

    def save_lyrics(self: str, lyrics: str): ...


class Publisher(Protocol):
    def send_message(self: str, message: dict[str, Any]): ...


class Tasks:
    def __init__(self, service: Genius, scraper: Scraper, store: Store, publisher: Publisher, scraper_queue: str):
        self.service = service
        self.scraper = scraper
        self.store = store
        self.publisher = publisher
        self.scraper_queue = scraper_queue

    def search_artists(self, artist_name: str):
        artists_found = self.service.search_artists(artist_name)
        for artist in artists_found:
            logger.info(
                "Search Artists result: Name: %s GeniusArtistId: %s",
                artist.name,
                artist.external_artist_id,
            )
        self.store.save_artists(artists_found)

    def get_artist_songs(self, artist_id: str):
        logger.info("Retrieving songs for artist_id: %s", artist_id)
        get_songs = self.service.artist_song_retriever(artist_id)
        batch: list[SongData] = []
        for song in get_songs:
            time.sleep(random.uniform(*_SLEEP_MIN_MAX))  # noqa: S311
            if len(batch) >= _STORE_WRITE_BATCH_SIZE:
                self._save_songs_batch(batch, self.scraper_queue)
            batch.append(song)

        if batch:
            self._save_songs_batch(batch, self.scraper_queue)

    def _save_songs_batch(self, songs: list[SongData], queue_name: str):
        self.store.save_songs(songs)
        for song in songs:
            self.publisher.send_message(
                queue_name=queue_name,
                message={"lyrics_url": song.lyrics_url, "song_id": song.external_song_id},
            )

    def scrape_lyrics(self, song_id: str, song_url: str):
        time.sleep(random.uniform(*_SLEEP_MIN_MAX))  # noqa: S311
        lyrics = self.scraper.get_lyrics(song_url)
        logger.info("Scraped Lyrics for song URL: %s, Lyrics: %s...", song_url, lyrics[:50])
        self.store.save_lyrics(song_id, lyrics)
