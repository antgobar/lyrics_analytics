from datetime import date

from pydantic import BaseModel as Base
from pydantic import ConfigDict


class BaseModel(Base):
    model_config = ConfigDict(coerce_numbers_to_str=True)


class SongData(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True, frozen=False)
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
