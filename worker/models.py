from datetime import date

from pydantic import BaseModel as Base
from pydantic import ConfigDict


class BaseModel(Base):
    model_config = ConfigDict(coerce_numbers_to_str=True)


class SongData(BaseModel):
    name: str
    genius_artist_id: str
    song_id: str
    title: str
    album: str | None
    release_date: date
    lyrics_url: str | None


class ArtistData(BaseModel):
    genius_artist_id: str
    name: str


class SearchArtistRequest(BaseModel):
    artist_name: str


class GetArtistSongsRequest(BaseModel):
    artist_id: str


class ScrapeSongLyricsRequest(BaseModel):
    song_id: str
    song_url: str
