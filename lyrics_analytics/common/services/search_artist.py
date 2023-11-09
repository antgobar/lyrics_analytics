from lyrics_analytics.config import Config
from lyrics_analytics.common.services.genius import GeniusService


def search_artist_by_name(name):
    genius = GeniusService(Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    return genius.find_artists(name)
