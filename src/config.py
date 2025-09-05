import os


class Config:
    GENIUS_BASE_URL = "https://api.genius.com"
    GENIUS_CLIENT_ID = os.getenv("GENIUS_CLIENT_ID")
    GENIUS_CLIENT_SECRET = os.getenv("GENIUS_CLIENT_SECRET")
    GENIUS_CLIENT_ACCESS_TOKEN = os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")

    BROKER_URL = os.getenv("BROKER_URL")
    QUEUE_SEARCH_ARTISTS = "search_artists"
    QUEUE_GET_ARTIST_SONGS = "get_artist_songs"
    QUEUE_SCRAPE_LYRICS_URL = "scrape_lyrics_url"

    DATABASE_URL = os.getenv("DATABASE_URL")
