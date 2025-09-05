from valkey import Valkey

_ARTIST_NAME_SEARCH_TERM_PREFIX = "artist_name_search_term"


class ValkeyCache:
    def __init__(self, host: str, port: int, password: str):
        self._cache = Valkey(host=host, port=port, password=password)

    def get_artist_ids_from_search_term(self, search_term: str) -> list[str]:
        return self._cache.get(f"{_ARTIST_NAME_SEARCH_TERM_PREFIX}:{search_term}") or []

    def cache_artist_ids_for_search_term(self, search_term: str, artist_ids: list[str]) -> None:
        self._cache.set(f"{_ARTIST_NAME_SEARCH_TERM_PREFIX}:{search_term}", artist_ids)
