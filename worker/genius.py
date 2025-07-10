import logging
import time
from dataclasses import dataclass
from datetime import date
from typing import Callable, Generator, Protocol

import httpx
from httpx import Response

from worker.scraper import LyricsData, get_lyrics_for_url

_SLEEP_LENGTH = 0.2
_REPLACE_PATTERNS = ("\u2014",)
_TITLE_FILTERS = (
    "(",
    "[",
    ")",
    "]",
    "demo",
    "tour",
    "award",
    "speech",
    "annotated",
    "transcript",
    "discography",
    "mix",
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class SongData:
    name: str
    genius_artist_id: str
    genius_song_id: str
    title: str
    album: str
    release_date: date
    lyrics_data: LyricsData


@dataclass
class ArtistData:
    id: str
    name: str


class GeniusRequest(Protocol):
    def __call__(self, *args, **kwargs) -> Response: ...


class GeniusService:
    def __init__(self, _base_url: str, access_token: str, health_check=True) -> None:
        self._base_url = _base_url
        self._base_params = {"access_token": access_token}
        self.titles = []
        self.artist_data = None
        if health_check:
            self.ping()

    def ping(self):
        response = httpx.get(f"{self._base_url}/songs/1", params=self._base_params)
        if response.ok and response.json()["meta"]["status"] == 200:
            logger.info("Genius connected")
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
    def _search_artist(self, artist_name: str) -> Response:
        url = f"{self._base_url}/search"
        params = self._base_params
        params["q"] = artist_name
        return httpx.get(url=url, params=params)

    @staticmethod
    def _parse_artist_search_result(
        hit_result: dict, artist_name: str
    ) -> ArtistData | None:
        if (
            artist_name.lower()
            in hit_result["result"]["primary_artist"]["name"].lower()
        ):
            artist_data = hit_result["result"]["primary_artist"]
            return ArtistData(id=artist_data["id"], name=artist_data["name"])

    @handle_response
    def _get_artist_song_page(self, artist_id: str, page_no: int) -> Response:
        url = f"{self._base_url}/artists/{artist_id}/songs"
        params = self._base_params
        params["page"] = page_no
        params["per_page"] = 50  # max per page
        return httpx.get(url=url, params=params)

    @handle_response
    def _get_artist_name(self, artist_id: str) -> str:
        url = f"{self._base_url}/artists/{artist_id}"
        response = httpx.get(url, params=self._base_params)
        return response["artist"]["name"].lower()

    @handle_response
    def _get_song(self, song_id):
        url = f"{self._base_url}/songs/{song_id}"
        return httpx.get(url, params=self._base_params)

    def search_artists(self, artist_name: str) -> list[ArtistData]:
        response = self._search_artist(artist_name)
        if response is None:
            logger.info(f"Not found: {artist_name}")
            return []

        artists_found = []
        for result in response["hits"]:
            artist_result = result["result"]["primary_artist"]
            if artist_name.lower() not in artist_result["name"].lower():
                continue
            artists_found.append(
                ArtistData(id=artist_result["id"], name=artist_result["name"])
            )

        return artists_found

    def artist_song_retriever(self, artist_id: str) -> Generator[SongData]:
        artist_name = self._get_artist_name(artist_id)
        page_no = 1

        while True:
            response = self._get_artist_song_page(artist_id, page_no)
            for song in response["songs"]:
                passed_filter = self._title_filter(song["title"])
                is_primary_artist = (
                    artist_name == song["primary_artist"]["name"].lower()
                )
                if (
                    song["lyrics_state"] != "complete"
                    or not passed_filter
                    or not is_primary_artist
                ):
                    continue

                song_data = self._get_song_data(song)
                if song_data.album is None:
                    continue

                yield song_data

            if response["next_page"] is None:
                break

            page_no += 1
            time.sleep(_SLEEP_LENGTH)

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
        name = album_data if album_data is None else album_data.get("name")
        if name is None:
            return None
        for to_filter in _TITLE_FILTERS:
            if to_filter.lower() in name.lower():
                return None
        return name

    def _get_song_data(self, song_response: dict) -> SongData:
        song = self._get_song(song_response["id"])["song"]
        lyrics_data = get_lyrics_for_url(song_response["url"])
        return SongData(
            name=song_response["primary_artist"]["name"],
            genius_artist_id=str(song_response["primary_artist"]["id"]),
            genius_song_id=str(song_response["id"]),
            title=song_response["title"],
            album=self._parse_album(song.get("album")),
            release_date=self._parse_date(song_response.get("release_date_components")),
            lyrics_data=lyrics_data,
        )

    def _title_filter(self, title: str) -> bool:
        title = title.lower()

        for pattern in _REPLACE_PATTERNS:
            title = title.replace(pattern, " ")

        for pattern in _TITLE_FILTERS:
            if pattern in title:
                return False

        if title in self.titles:
            return False

        self.titles.append(title)
        return True
