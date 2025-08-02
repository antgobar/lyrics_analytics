from datetime import date

from pydantic import BaseModel


class SongData(BaseModel):
    name: str
    genius_artist_id: str
    genius_song_id: str
    title: str
    album: str | None
    release_date: date
    url: str | None


class ArtistData(BaseModel):
    genius_artist_id: str
    name: str
