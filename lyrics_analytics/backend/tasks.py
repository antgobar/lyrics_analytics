import os

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from lyrics_analytics.services.genius_api import GeniusService


genius = GeniusService("http://api.genius.com", os.getenv("GENIUS_CLIENT_ACCESS_TOKEN"))


@shared_task(bind=True, base=AbortableTask)
def find_artists(self, artist_name):
    return genius.find_artists(artist_name)


@shared_task(bind=True, base=AbortableTask)
def get_artist_songs(self, artist_id):
    return genius.get_artist_songs(artist_id)


