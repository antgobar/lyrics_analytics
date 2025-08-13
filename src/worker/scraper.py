import re

import httpx
from bs4 import BeautifulSoup

_REPLACE_CHARS = ("\n", ",", ".", "(", ")", "/", '"', "\\", "-")


class Scraper:
    @classmethod
    def get_lyrics(cls, url: str) -> str:
        page = httpx.get(url)
        page_content = page.content.decode().replace("<br/>", "\n").encode()
        html = BeautifulSoup(page_content, "html.parser")
        div = html.find("div", class_=re.compile(r"^lyrics$|Lyrics__Root"))
        if div is None:
            return ""
        return div.get_text()

    @staticmethod
    def clean(lyrics: str) -> str:
        lyrics = re.sub(r"(\[.*?])*", "", lyrics)
        lyrics = re.sub(r"\n{2}", "\n", lyrics)
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
    lyrics = Scraper.get_lyrics("https://genius.com/Lukas-graham-7-years-lyrics")
