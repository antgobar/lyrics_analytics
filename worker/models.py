from datetime import datetime

from pydantic import BaseModel


class SongData(BaseModel):
    name: str
    genius_artist_id: str
    genius_song_id: str
    title: str
    album: str
    release_date: datetime
    lyrics: str
