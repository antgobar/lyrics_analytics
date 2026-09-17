import time
from typing import Protocol

from services.models import ArtistData, SearchArtistRequest
from services.store import Store


class Cache(Protocol):
    def get_artist_ids_from_search_term(self, term: str) -> list[str]: ...


class Publisher(Protocol):
    def search_artists(self, request: SearchArtistRequest) -> None: ...


class SearchService:
    def __init__(self, cache: Cache, publisher: Publisher, store: Store) -> None:
        self.cache = cache
        self.publisher = publisher
        self.store = store

    def search_artist_by_name(self, term: str) -> list[ArtistData]:
        if artist_ids := self.cache.get_artist_ids_from_search_term(term):
            return self.store.get_artists_by_id(artist_ids)

        self.publisher.search_artists(SearchArtistRequest(artist_name=term))
        attempts = 3
        delay = 1  # seconds
        for _ in range(attempts):
            if artist_ids := self.cache.get_artist_ids_from_search_term(term):
                return self.store.get_artists_by_id(artist_ids)
            time.sleep(delay)
        return []
