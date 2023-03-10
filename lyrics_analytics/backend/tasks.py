import os

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from lyrics_analytics.config import Config
from lyrics_analytics.services.genius import GeniusService
from lyrics_analytics.backend.db import mongo_collection


@shared_task(bind=True, base=AbortableTask)
def find_artists(self, artist_name):
    genius = GeniusService("http://api.genius.com", Config.GENIUS_CLIENT_ACCESS_TOKEN, healthcheck=False)
    return genius.find_artists(artist_name)


@shared_task(bind=True, base=AbortableTask)
def get_artist_songs(self, artist_id):
    genius = GeniusService("http://api.genius.com", Config.GENIUS_CLIENT_ACCESS_TOKEN, healthcheck=False)

    artist_data = genius.get_artist_data(artist_id)
    artists_collection = mongo_collection("lyrics_analytics", "artists")
    artists_collection.insert_one(
        {
            "genius_artist_id": artist_data["id"],
            "name": artist_data["name"],
            "ready": False
        }
    )

    songs = genius.get_artist_songs(artist_id)
    song_stats_collection = mongo_collection("lyrics_analytics", "song_stats")
    song_stats_collection.insert_many(songs)

    artists_collection.update_one(
        {"genius_artist_id": artist_id},
        {"$set": {"ready": True}}
    )

    return {"genius_artist_id": artist_id, "name": artist_data["name"], "total": len(songs), "ready": True}
