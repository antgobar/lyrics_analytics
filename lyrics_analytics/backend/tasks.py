import os

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from lyrics_analytics.services.genius import GeniusService
from lyrics_analytics.backend.db import df_writer

genius = GeniusService("http://api.genius.com", os.getenv("GENIUS_CLIENT_ACCESS_TOKEN"))


@shared_task(bind=True, base=AbortableTask)
def find_artists(self, artist_name):
    return genius.find_artists(artist_name)


@shared_task(bind=True, base=AbortableTask)
def get_artist_songs(self, artist_id):
    data = genius.get_artist_songs(artist_id)
    df_writer(data, "lyrics_stats")
    return data
