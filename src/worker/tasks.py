import random
import time
from typing import Protocol

from services.cache.repository import Cache
from services.logger import setup_logger
from services.models import ArtistData, BaseModel, ScrapeSongLyricsRequest, SongData
from services.retrieval.repository import Retrieval
from services.scraper.repository import Scraper

logger = setup_logger(__name__)

_STORE_WRITE_BATCH_SIZE = 2
_SLEEP_MIN_MAX = (1, 2)


class Store(Protocol):
    def save_artists(self: list[ArtistData]): ...

    def save_songs(self: list[SongData]): ...

    def save_lyrics(self: str, lyrics: str): ...


class Publisher(Protocol):
    def send_message(self, queue_name: str, data: BaseModel): ...


def search_artists_task(retrieval: Retrieval, store: Store, cache: Cache):
    def search_artists(artist_name: str):
        artists_found = retrieval.search_artists(artist_name)
        store.save_artists(artists_found)
        cache.cache_artist_ids_for_search_term(
            artist_name,
            [a.external_artist_id for a in artists_found],
        )

    return search_artists


def scrape_lyrics_task(scraper: Scraper, store: Store):
    def scrape_lyrics(song_id: str, lyrics_url: str):
        time.sleep(random.uniform(*_SLEEP_MIN_MAX))  # noqa: S311
        lyrics = scraper.get_lyrics(lyrics_url)
        logger.info("Scraped Lyrics for song URL: %s, Lyrics: %s...", lyrics_url, lyrics[:50])
        store.save_lyrics(song_id, lyrics)

    return scrape_lyrics


def get_artist_songs_task(
    retrieval: Retrieval,
    store: Store,
    publisher: Publisher,
    scraper_queue: str,
):
    def _save_songs_batch(songs: list[SongData]):
        store.save_songs(songs)
        for song in songs:
            publisher.send_message(
                queue_name=scraper_queue,
                data=ScrapeSongLyricsRequest(song_id=song.external_song_id, lyrics_url=song.lyrics_url),
            )

    def get_artist_songs(artist_id: str):
        logger.info("Retrieving songs for artist_id: %s", artist_id)
        get_songs = retrieval.artist_song_retriever(artist_id)
        batch: list[SongData] = []

        for song in get_songs:
            time.sleep(random.uniform(*_SLEEP_MIN_MAX))  # noqa: S311
            batch.append(song)

            if len(batch) >= _STORE_WRITE_BATCH_SIZE:
                _save_songs_batch(batch)
                batch.clear()

        if batch:
            _save_songs_batch(batch)

    return get_artist_songs
