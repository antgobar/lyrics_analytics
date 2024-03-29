from dataclasses import asdict

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from lyrics_analytics.config import Config
from lyrics_analytics.database.queries import TaskQueries
from lyrics_analytics.services.genius import GeniusService


task_queries = TaskQueries()


@shared_task(bind=True, base=AbortableTask)
def find_artists(self, artist_name: str) -> list[dict]:
    genius = GeniusService(Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    found_artists = genius.find_artists(artist_name)
    return found_artists


@shared_task(bind=True, base=AbortableTask)
def artist_song_data(self, artist_id: int | str):
    genius = GeniusService(Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    songs = [asdict(song) for song in genius.get_artist_songs(artist_id)]
    return task_queries.insert_many_songs_update_status(songs, artist_id)
