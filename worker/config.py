import os


class Config:
    GENIUS_BASE_URL = os.getenv("GENIUS_BASE_URL")
    GENIUS_CLIENT_ID = os.getenv("GENIUS_CLIENT_ID")
    GENIUS_CLIENT_SECRET = os.getenv("GENIUS_CLIENT_SECRET")
    GENIUS_CLIENT_ACCESS_TOKEN = os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")

    BROKER_URL = os.getenv("BROKER_URL")
    QUEUE_SEARCH_ARTISTS = "search_artists_queue"
    QUEUE_GET_ARTIST_SONGS = "get_artist_songs_queue"
