import os


class Config:
    GENIUS_CLIENT_ID = os.getenv("GENIUS_CLIENT_ID")
    GENIUS_CLIENT_SECRET = os.getenv("GENIUS_CLIENT_SECRET")
    GENIUS_CLIENT_ACCESS_TOKEN = os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")

    QUEUE_SEARCH = "search_artists_queue"
    QUEUE_GET_SONGS = "get_artist_songs_queue"
