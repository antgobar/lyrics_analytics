from typing import Callable
import logging
from datetime import date
from dataclasses import dataclass

import requests
from requests.models import Response
from dotenv import dotenv_values

from lyrics_analytics.services.scraper import ScraperService


@dataclass
class SongData:
    name: str
    genius_artist_id: str
    genius_song_id: str
    title: str
    lyrics_count: int
    distinct_count: int
    album: str
    release_date: date

    @property
    def distinct_coefficient(self):
        return self.distinct_count / self.lyrics_count


TITLE_FILTERS = (
    "(", "[", ")", "]", "demo", "tour",
    "award", "speech", "annotated", "transcript", "discography"
)

REPLACE_PATTERNS = ("\u2014", )


class GeniusService:
    def __init__(self, _base_url: str, access_token: str, healthcheck=True) -> None:
        self._base_url = _base_url
        if access_token is None:
            access_token = dotenv_values(".env").get("GENIUS_CLIENT_ACCESS_TOKEN")
        self._base_params = {"access_token": access_token}
        self.titles = []
        self.artist_data = None
        if healthcheck:
            self.ping()

    def ping(self):
        response = requests.get(f"{self._base_url}/songs/1", params=self._base_params)
        if response.ok and response.json()["meta"]["status"] == 200:
            logging.info("Genius connected")
            return True
        else:
            raise ConnectionError("Unable to connect")

    @staticmethod
    def handle_response(func) -> Callable:
        def wrapper(*args, **kwargs) -> dict:
            response = func(*args, **kwargs)
            if response.ok and response.json()["meta"]["status"] == 200:
                return response.json()["response"]
            raise ConnectionError("Unable to connect")
        return wrapper

    @handle_response
    def _search_artist(self, artist_name: str) -> Response or dict:
        url = f"{self._base_url}/search"
        params = self._base_params
        params["q"] = artist_name
        return requests.get(url=url, params=params)

    @staticmethod
    def _find_artists_iter(hit_result: dict, artist_name: str) -> dict | None:
        if artist_name.lower() in hit_result["result"]["primary_artist"]["name"].lower():
            artist_data = hit_result["result"]["primary_artist"]
            return {"id": artist_data["id"], "name": artist_data["name"]}

    def find_artists(self, artist_name: str) -> list[dict] | None:
        response = self._search_artist(artist_name)
        if response is None:
            logging.info(f"Not found: {artist_name}")
            return []
        artists_found = [self._find_artists_iter(result, artist_name) for result in response["hits"]]
        artists_found = [found for found in artists_found if found is not None]

        return list({artist["id"]: artist for artist in artists_found}.values())

    @handle_response
    def _get_artist_song_page(self, artist_id: int, page_no: int) -> Response or dict:
        url = f"{self._base_url}/artists/{artist_id}/songs"
        params = self._base_params
        params["page"] = page_no
        params["per_page"] = 50  # max per page
        return requests.get(url=url, params=params)

    @handle_response
    def _get_artist(self, artist_id: int) -> Response or str:
        url = f"{self._base_url}/artists/{artist_id}"
        return requests.get(url, params=self._base_params)

    @handle_response
    def _get_song(self, song_id):
        url = f"{self._base_url}/songs/{song_id}"
        return requests.get(url, params=self._base_params)

    def get_artist_data(self, artist_id: int):
        self.artist_data = self._get_artist(artist_id)["artist"]
        return self.artist_data

    def get_artist_songs(self, artist_id: int) -> list:
        if self.artist_data is None:
            artist_name = self.get_artist_data(artist_id)["name"].lower()
        else:
            artist_name = self.artist_data["name"].lower()
        page_no = 1

        while True:
            response = self._get_artist_song_page(artist_id, page_no)
            for song in response["songs"]:
                passed_filter = self._title_filter(song["title"])
                is_primary_artist = artist_name == song["primary_artist"]["name"].lower()
                if song["lyrics_state"] != "complete" or not passed_filter or not is_primary_artist:
                    continue

                song_data = self._get_song_data(song)
                if song_data.album is None:
                    continue

                yield song_data

            if response["next_page"] is None:
                break
            
            page_no += 1

        self.titles = []

    @staticmethod
    def _parse_date(date_component_data: dict | str) -> str | date:
        if type(date_component_data) is not dict:
            date_component_data = {}
        year = date_component_data.get("year") or 1
        month = date_component_data.get("month") or 1
        day = date_component_data.get("day") or 1
        return date(year, month, day).strftime("%Y-%m-%d")

    @staticmethod
    def _parse_album(album_data: dict) -> str | None:
        return album_data if album_data is None else album_data.get("name")

    def _get_song_data(self, song_response: dict) -> SongData:
        song = self._get_song(song_response["id"])["song"]
        lyrics = ScraperService.get_lyrics(song_response["url"]).split(" ")
        return SongData(
            name=song_response["primary_artist"]["name"],
            genius_artist_id=str(song_response["primary_artist"]["id"]),
            genius_song_id=str(song_response["id"]),
            title=song_response["title"],
            lyrics_count=len(lyrics),
            distinct_count=len(set(lyrics)),
            album=self._parse_album(song.get("album")),
            release_date=self._parse_date(song_response.get("release_date_components"))
        )

    def _title_filter(self, title: str) -> bool:
        title = title.lower()

        for pattern in REPLACE_PATTERNS:
            title = title.replace(pattern, " ")

        for pattern in TITLE_FILTERS:
            if pattern in title:
                return False
        
        if title in self.titles:
            return False
        
        self.titles.append(title)
        return True
