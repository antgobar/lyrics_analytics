import re

import requests
from bs4 import BeautifulSoup


class Scraper:
    @classmethod
    def get_lyrics(cls, url: str) -> str:
        raw_lyrics = cls.scrape(url)
        return cls.clean(raw_lyrics)

    @staticmethod
    def scrape(url: str):
        page = requests.get(url)
        page_content = page.content.decode().replace('<br/>', '\n').encode()
        html = BeautifulSoup(page_content, "html.parser")
        div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
        return div.get_text()
    
    @staticmethod
    def clean(lyrics: str) -> str:
        lyrics = re.sub(r'(\[.*?])*', '', lyrics)
        lyrics = re.sub('\n{2}', '\n', lyrics)
        lyrics = lyrics.strip("\n").lower()

        replace_chars = ("\n", ",", ".")
        for char in replace_chars:
            lyrics = lyrics.replace(char, " ")
            
        lyrics = lyrics.replace("  ", " ")
        lyrics = lyrics.split("lyrics ")
        if len(lyrics) == 1:
            return lyrics[0]
        return " lyrics ".join(lyrics[1:])
