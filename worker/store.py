from flask import json
from models import ArtistData, SongData


class Store:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def save_artists(self, artists: list[ArtistData]):
        # Implement saving logic here
        pass

    def save_songs(self, songs: list[SongData]):
        with open("songs.txt", "a") as f:
            for song in songs:
                f.write(song.model_dump_json() + "\n")

    def save_lyrics(self, song_id: str, lyrics: str):
        with open("lyrics.txt", "a") as f:
            f.write(json.dumps({"song_id": song_id, "lyrics": lyrics[:100]}) + "\n")
