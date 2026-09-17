from collections.abc import Generator
from typing import Protocol

from services.models import ArtistData, SongData


class Retrieval(Protocol):
    def search_artists(self, artist_name: str) -> list[ArtistData]: ...
    def artist_song_retriever(self, artist_id: str) -> Generator[SongData]: ...
