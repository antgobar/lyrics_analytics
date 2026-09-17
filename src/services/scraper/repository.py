from typing import Protocol


class Scraper(Protocol):
    def get_lyrics(self, url: str) -> str: ...

    def clean_lyrics(self, lyrics: str) -> str: ...
