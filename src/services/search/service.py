from services.cache import Cache
from services.models import SearchArtistRequest
from services.publisher import Publisher


class SearchService:
    def __init__(self, cache: Cache, publisher: Publisher):
        self.cache = cache
        self.publisher = publisher

    def search_artist_by_name(self, term: str) -> list[str]:
        artist_ids = self.cache.get_artist_ids_from_search_term(term)
        if artist_ids:
            return artist_ids

        self.publisher.search_artist(SearchArtistRequest(artist_name=term))
