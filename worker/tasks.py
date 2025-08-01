from genius import GeniusService
from logger import setup_logger

logger = setup_logger(__name__)


class Tasks:
    def __init__(self, service: GeniusService, store):
        self.service = service
        self.store = store

    def search_artists(self, artist_name: str):
        artists_found = self.service.search_artists(artist_name)
        for artist in artists_found:
            logger.info(f"Found artist: {artist.name} (ID: {artist.genius_artist_id})")
        self.store.save_artists(artists_found)

    def get_artist_songs(self, artist_id: str):
        logger.info(f"Retrieving songs for artist ID: {artist_id}")
        get_songs = self.service.artist_song_retriever(artist_id)
        for song in get_songs:
            logger.info(f"Found song: {song.title} (ID: {song.genius_song_id})")


def search_artists(service: GeniusService, store, artist_name: str):
    artists_found = service.search_artists(artist_name)
    for artist in artists_found:
        logger.info(f"Found artist: {artist.name} (ID: {artist.genius_artist_id})")
    store.save_artists(artists_found)


def get_artist_songs(service: GeniusService, store, artist_id: str):
    logger.info(f"Retrieving songs for artist ID: {artist_id}")
    get_songs = service.artist_song_retriever(artist_id)
    for song in get_songs:
        logger.info(f"Found song: {song.title} (ID: {song.genius_song_id})")
