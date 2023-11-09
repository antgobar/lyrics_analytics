import sys
from dataclasses import asdict
import logging

from lyrics_analytics.config import Config
from lyrics_analytics.common.database.queries import TaskQueries
from lyrics_analytics.common.services.genius import GeniusService
from lyrics_analytics.common.services.queue import consumer


logging.basicConfig(level=logging.INFO)


def artist_song_data(artist_id: int | str):
    genius = GeniusService(Config.GENIUS_BASE_URL, Config.GENIUS_CLIENT_ACCESS_TOKEN)
    songs = [asdict(song) for song in genius.get_artist_songs(artist_id)]
    result = TaskQueries.insert_many_songs_update_status(songs, artist_id)
    logging.info(f"[x] Task complete, result: {result}")
    logging.info("[x] Waiting for message")


if __name__ == '__main__':
    try:
        consumer(callback=artist_song_data)
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
