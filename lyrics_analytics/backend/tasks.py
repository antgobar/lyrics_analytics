import os
from dataclasses import asdict

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from lyrics_analytics.config import Config
from lyrics_analytics.services.genius import GeniusService
from lyrics_analytics.backend import db


@shared_task(bind=True, base=AbortableTask)
def find_artists(self, artist_name):
    search_log_collection = db.get_collection("lyrics_analytics", "search_log_collection")
    been_searched = search_log_collection.find_one({"search_name": artist_name})
    if been_searched:
        return been_searched["found_artists"]

    genius = GeniusService("http://api.genius.com", Config.GENIUS_CLIENT_ACCESS_TOKEN)
    found_artists = genius.find_artists(artist_name)
    search_log_collection.insert_one(
        {
            "search_name": artist_name,
            "found_artists": found_artists
        }
    )
    return found_artists


@shared_task(bind=True, base=AbortableTask)
def artist_song_data(self, artist_id):
    genius = GeniusService("http://api.genius.com", Config.GENIUS_CLIENT_ACCESS_TOKEN)

    artist_data = genius.get_artist_data(artist_id)
    artists_collection = db.get_collection("lyrics_analytics", "artists")
    artists_collection.insert_one(
        {
            "genius_artist_id": artist_data["id"],
            "name": artist_data["name"],
            "ready": False
        }
    )

    songs = [asdict(song) for song in genius.get_artist_songs(artist_id)]

    song_stats_collection = db.get_collection("lyrics_analytics", "song_stats")
    song_stats_collection.insert_many(songs)

    artists_collection.update_one(
        {"genius_artist_id": int(artist_id)},
        {"$set": {"ready": True}}
    )

    return {"genius_artist_id": artist_id, "name": artist_data["name"], "total": len(songs), "ready": True}
