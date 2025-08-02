from genius import Genius
from logger import setup_logger
from models import SongData
from pika import BlockingConnection
from scraper import Scraper
from store import Store

logger = setup_logger(__name__)

_STORE_WRITE_BATCH_SIZE = 50


class Tasks:
    def __init__(self, service: Genius, scraper: Scraper, store: Store, scrape_queue):
        self.service = service
        self.scraper = scraper
        self.store = store
        self.scrape_queue = scrape_queue

    def search_artists(self, artist_name: str):
        artists_found = self.service.search_artists(artist_name)
        for artist in artists_found:
            logger.info(f"Search Artists result: Name: {artist.name} GeniusArtistId: {artist.genius_artist_id})")
        self.store.save_artists(artists_found)

    def get_artist_songs(self, artist_id: str):
        batch: list[SongData] = []
        get_songs = self.service.artist_song_retriever(artist_id)
        for song in get_songs:
            batch.append(song)
            if len(batch) >= _STORE_WRITE_BATCH_SIZE:
                self.store.save_songs(batch)
                batch.clear()
            logger.info(f"Get Songs result: GeniusArtistId: {artist_id}, GeniusSongId: {song.genius_song_id})")

    def scrape_lyrics(self, song_url: str):
        lyrics = self.scraper.get_lyrics(song_url)
        logger.info(f"Scraped Lyrics for song URL: {song_url}, Lyrics: {lyrics[:50]}...")
        self.store.save_lyrics(song_url, lyrics)
