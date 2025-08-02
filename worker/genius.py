import time
from datetime import date
from typing import Generator

import httpx

from .logger import setup_logger
from .models import ArtistData, SongData

logger = setup_logger(__name__)


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


class Genius:
    def __init__(self, _base_url: str, access_token: str) -> None:
        self._base_url = _base_url
        self._base_params = {"access_token": access_token}

    def make_request(self, endpoint: str, params: dict | None = None) -> dict | None:
        try:
            if params is None:
                params = self._base_params
            else:
                params = {**self._base_params, **params}
            response = httpx.get(url=f"{self._base_url}/{endpoint}", params=params)
            if response.status_code == 200 and response.json()["meta"]["status"] == 200:
                return response.json()["response"]
            raise httpx.HTTPError("Unable to connect")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            return None

    def _search_artist(self, artist_name: str) -> dict | None:
        return self.make_request("search", {"q": artist_name})

    def _get_artist_song_page(self, artist_id: str, page_no: int) -> dict | None:
        return self.make_request(f"artists/{artist_id}/songs", {"page": page_no, "per_page": 50})

    def _get_artist_name(self, artist_id: str) -> dict | None:
        return self.make_request(f"artists/{artist_id}")

    def _get_song(self, song_id: str) -> dict | None:
        return self.make_request(f"songs/{song_id}")

    @staticmethod
    def _parse_artist_search_result(hit_result: dict, artist_name: str) -> ArtistData | None:
        if artist_name.lower() in hit_result["result"]["primary_artist"]["name"].lower():
            artist_data = hit_result["result"]["primary_artist"]
            return ArtistData(genius_artist_id=artist_data["id"], name=artist_data["name"])

    @staticmethod
    def _parse_date(date_data: dict | str) -> str | date:
        if not isinstance(date_data, dict):
            date_data = {}
        year = date_data.get("year", 1)
        month = date_data.get("month", 1)
        day = date_data.get("day", 1)
        return date(year, month, day)

    @staticmethod
    def _parse_album(album_data: dict) -> str | None:
        name = album_data.get("name")
        if name is None:
            return None
        for to_filter in _TITLE_FILTERS:
            if to_filter.lower() in name.lower():
                return None
        return name

    def _parse_song(self, song_data: dict, artist_name: str) -> SongData | None:
        title_filtered = self._title_filter(song_data["title"].lower().strip())
        is_primary_artist = artist_name == song_data["primary_artist"]["name"].lower()

        if any(song_data["lyrics_state"] != "complete", not title_filtered, not is_primary_artist):
            return None

        return self._get_song_data(song_data)

    def search_artists(self, artist_name: str) -> list[ArtistData]:
        response = self._search_artist(artist_name)
        if response is None:
            logger.info(f"Not found: {artist_name}")
            return []

        artists_found = []
        artists_ids = set()
        for result in response["hits"]:
            artist_result = result["result"]["primary_artist"]
            if artist_name.lower() not in artist_result["name"].lower():
                continue
            if artist_result["id"] in artists_ids:
                continue
            artists_found.append(ArtistData(genius_artist_id=artist_result["id"], name=artist_result["name"]))
            artists_ids.add(artist_result["id"])

        return artists_found

    def artist_song_retriever(self, artist_id: str) -> Generator[SongData]:
        artist_name = self._get_artist_name(artist_id)["artist"]["name"].lower()
        logger.info(f"Retrieving songs for artist: {artist_name} (ID: {artist_id})")
        page_no = 1

        while True:
            response = self._get_artist_song_page(artist_id, page_no)
            if response is None:
                logger.error(f"Failed to retrieve songs for artist ID: {artist_id}")
                break
            for song_data in response["songs"]:
                yield self._parse_song(song_data, artist_name)

            if response["next_page"] is None:
                break

            page_no += 1
            time.sleep(_SLEEP_LENGTH)

    def _get_song_data(self, song_response: dict) -> SongData:
        song = self._get_song(song_response["id"])
        if song is None:
            album = None
        else:
            song_album = song["song"].get("album", {})
            album = self._parse_album(song_album)

        return SongData(
            name=song_response["primary_artist"]["name"],
            genius_artist_id=str(song_response["primary_artist"]["id"]),
            genius_song_id=str(song_response["id"]),
            title=song_response["title"],
            album=album,
            release_date=self._parse_date(song_response.get("release_date_components")),
            url=song_response["url"],
        )

    def _title_filter(self, title: str) -> bool:
        for pattern in _REPLACE_PATTERNS:
            title = title.replace(pattern, " ")

        for pattern in _TITLE_FILTERS:
            if pattern in title:
                return False

        return True
