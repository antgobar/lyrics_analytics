import re
import logging

import requests
from bs4 import BeautifulSoup


class ScraperService:
    @classmethod
    def get_lyrics(cls, url: str) -> str:
        raw_lyrics = cls.scrape(url)
        logging.info(f"Scraped {url}")
        return cls.clean(raw_lyrics)

    @staticmethod
    def scrape(url: str) -> str:
        page = requests.get(url)
        page_content = page.content.decode().replace('<br/>', '\n').encode()
        html = BeautifulSoup(page_content, "html.parser")
        div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
        if div is None:
            return ""
        return div.get_text()

    @staticmethod
    def replacer(text: str, chars: tuple, replacer: str) -> str:
        for char in chars:
            text = text.replace(char, replacer)
        return text

    @classmethod
    def clean(cls, lyrics: str) -> str:
        lyrics = re.sub(r'(\[.*?])*', '', lyrics)
        lyrics = re.sub('\n{2}', '\n', lyrics)
        lyrics = lyrics.strip("\n").lower()

        lyrics = cls.replacer(lyrics, ("\n", ",", ".", "(", ")", "/", "\"", "\\", "-"), " ")
        lyrics = lyrics.replace("  ", " ")

        lyrics = lyrics.split("lyrics ")
        if len(lyrics) == 1:
            return lyrics[0]
        lyrics = " lyrics ".join(lyrics[1:])

        lyrics = lyrics.split(" ")
        if "embed" in lyrics[-1]:
            lyrics[-1] = lyrics[-1].replace("embed", "")

        return " ".join(lyrics)
