from valkey import Valkey

_ARTIST_NAME_SEARCH_TERM_PREFIX = "artist_name_search_term"


class ValkeyCache:
    def __init__(self, connection_url: str):
        self.cache = Valkey.from_url(connection_url)

    def get_artist_ids_from_search_term(self, search_term: str) -> list[str]:
        return self.cache.get(f"{_ARTIST_NAME_SEARCH_TERM_PREFIX}:{search_term}") or []

    def cache_artist_ids_for_search_term(self, search_term: str, artist_ids: list[str]) -> None:
        self.cache.set(f"{_ARTIST_NAME_SEARCH_TERM_PREFIX}:{search_term}", artist_ids)


if __name__ == "__main__":
    cache = ValkeyCache("valkey://localhost:6666")
