import logging
import re

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_REPLACE_CHARS = ("\n", ",", ".", "(", ")", "/", '"', "\\", "-")


def get_lyrics_for_url(url: str) -> str:
    return _Scraper.get_lyrics(url)


class _Scraper:
    @classmethod
    def get_lyrics(cls, url: str) -> str:
        return cls.scrape(url)

    @staticmethod
    def scrape(url: str) -> str:
        page = httpx.get(url)
        page_content = page.content.decode().replace("<br/>", "\n").encode()
        html = BeautifulSoup(page_content, "html.parser")
        div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
        if div is None:
            return ""
        return div.get_text()


def clean(lyrics: str) -> str:
    lyrics = re.sub(r"(\[.*?])*", "", lyrics)
    lyrics = re.sub("\n{2}", "\n", lyrics)
    lyrics = lyrics.strip("\n").lower()

    for char in _REPLACE_CHARS:
        lyrics = lyrics.replace(char, " ")

    lyrics = lyrics.replace("  ", " ")
    lyrics = lyrics.split("lyrics ")
    if len(lyrics) == 1:
        return lyrics[0]
    lyrics = " lyrics ".join(lyrics[1:])

    lyrics = lyrics.split(" ")
    if "embed" in lyrics[-1]:
        lyrics[-1] = lyrics[-1].replace("embed", "")

    return " ".join(lyrics)


if __name__ == "__main__":
    # Example usage
    url = "https://genius.com/Lukas-graham-7-years-lyrics"
    lyrics = get_lyrics_for_url(url)
    print(lyrics)
