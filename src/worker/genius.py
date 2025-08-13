from collections.abc import Generator
from datetime import date

import httpx

from common.logger import setup_logger
from common.models import ArtistData, SongData

logger = setup_logger(__name__)


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
    def __init__(self, base_url: str, access_token: str) -> None:
        self.base_url = base_url
        self.base_params = {"access_token": access_token}

    def make_request(self, endpoint: str, params: dict | None = None) -> dict | None:
        def raise_connection_error():
            raise httpx.HTTPError("Unable to connect")

        try:
            params = self.base_params if params is None else {**self.base_params, **params}
            response = httpx.get(url=f"{self.base_url}/{endpoint}", params=params)
            if response.status_code == 200 and response.json()["meta"]["status"] == 200:
                return response.json()["response"]
            raise_connection_error()
        except httpx.HTTPError as e:
            logger.info("HTTP error occurred: %s", e)
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
            return ArtistData(external_artist_id=artist_data["id"], name=artist_data["name"])
        return None

    @staticmethod
    def _parse_date(date_data: dict | str) -> date:
        if not isinstance(date_data, dict):
            return date(1, 1, 1)  # Default date if no data is provided
        year = date_data.get("year") or 1
        month = date_data.get("month") or 1
        day = date_data.get("day") or 1
        return date(year, month, day)

    @staticmethod
    def _parse_album(song_data: dict) -> str | None:
        album_data = song_data.get("song", {}).get("album", {})
        if not album_data:
            return None
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

        if any([song_data["lyrics_state"] != "complete", not title_filtered, not is_primary_artist]):
            return None

        return self._get_song_data(song_data)

    def search_artists(self, artist_name: str) -> list[ArtistData]:
        response = self._search_artist(artist_name)
        if response is None:
            logger.info("Not found: %s", artist_name)
            return []

        artists_found = []
        artists_ids = set()
        for result in response["hits"]:
            artist_result = result["result"]["primary_artist"]
            if artist_name.lower() not in artist_result["name"].lower():
                continue
            if artist_result["id"] in artists_ids:
                continue
            logger.info("Found artist: %s (ID: %s)", artist_result["name"], artist_result["id"])
            artists_found.append(ArtistData(external_artist_id=artist_result["id"], name=artist_result["name"]))
            artists_ids.add(artist_result["id"])

        return artists_found

    def artist_song_retriever(self, artist_id: str) -> Generator[SongData]:
        artist_name = self._get_artist_name(artist_id)["artist"]["name"].lower()
        logger.info("Retrieving songs for artist: %s (ID: %s)", artist_name, artist_id)
        page_no = 1

        while True:
            response = self._get_artist_song_page(artist_id, page_no)
            if response is None:
                logger.error("Failed to retrieve songs for artist ID: %s", artist_id)
                break
            for song_data in response["songs"]:
                song = self._parse_song(song_data, artist_name)
                if song is None:
                    logger.info("Skipping song: %s (ID: %s)", song_data["title"], song_data["id"])
                if song:
                    logger.info("Found song: %s (ID: %s)", song.title, song.song_id)
                    yield song

            if response["next_page"] is None:
                break

            page_no += 1

    def _get_song_data(self, song_response: dict) -> SongData | None:
        logger.info("Processing song: %s (ID: %s)", song_response["title"], song_response["id"])
        song = self._get_song(song_response["id"])
        if song is None:
            logger.error("Failed to retrieve song data for ID: %s", song_response["id"])
            return None
        return SongData(
            name=song_response["primary_artist"]["name"],
            external_song_id=song_response["primary_artist"]["id"],
            song_id=song_response["id"],
            title=song_response["title"],
            album=self._parse_album(song),
            release_date=self._parse_date(song_response.get("release_date_components")),
            lyrics_url=song_response["url"],
        )

    def _title_filter(self, title: str) -> bool:
        for pattern in _REPLACE_PATTERNS:
            title = title.replace(pattern, " ")

        return all(pattern not in title for pattern in _TITLE_FILTERS)
