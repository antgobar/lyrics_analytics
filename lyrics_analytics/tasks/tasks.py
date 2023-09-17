from dataclasses import asdict

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from lyrics_analytics.config import Config
from lyrics_analytics.database.queries import (
    artist_previously_searched,
    insert_many_songs_update_status,
    update_search_log,
)
from lyrics_analytics.services.genius import GeniusService


@shared_task(bind=True, base=AbortableTask)
def find_artists(self, artist_name: str) -> list[dict]:
    been_searched = artist_previously_searched(artist_name)
    if been_searched:
        return been_searched["found_artists"]

    genius = GeniusService("http://api.genius.com", Config.GENIUS_CLIENT_ACCESS_TOKEN)
    found_artists = genius.find_artists(artist_name)
    update_search_log(artist_name, found_artists)
    return found_artists


@shared_task(bind=True, base=AbortableTask)
def artist_song_data(self, artist_id: int | str):
    genius = GeniusService("http://api.genius.com", Config.GENIUS_CLIENT_ACCESS_TOKEN)
    songs = [asdict(song) for song in genius.get_artist_songs(artist_id)]
    return insert_many_songs_update_status(songs, artist_id)
