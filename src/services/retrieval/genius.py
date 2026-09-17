import os
from collections import OrderedDict
from collections.abc import Generator
from datetime import date, datetime

import httpx

from services.logger import setup_logger
from services.models import ArtistData, SongData

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


class GeniusRetrieval:
    def __init__(self, base_url: str | None = None, access_token: str | None = None) -> None:
        self.base_url = base_url if base_url else os.getenv("GENIUS_API_BASE_URL")
        self.base_params = {"access_token": access_token if access_token else os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")}

    def _make_request(self, endpoint: str, params: dict | None = None) -> dict:
        response = httpx.get(
            url=f"{self.base_url}/{endpoint}",
            params=self.base_params if params is None else {**self.base_params, **params},
        )
        if response.status_code == 200 and response.json()["meta"]["status"] == 200:
            return response.json()["response"]
        raise httpx.HTTPError("Unable to connect")

    def _search_artist(self, artist_name: str) -> dict:
        return self._make_request("search", {"q": artist_name})

    def _get_artist_song_page(self, artist_id: str, page_no: int) -> dict:
        return self._make_request(f"artists/{artist_id}/songs", {"page": page_no, "per_page": 50})

    def _get_song(self, song_id: str) -> dict:
        return self._make_request(f"songs/{song_id}")

    def search_artists(self, artist_name: str) -> list[ArtistData]:
        response = self._search_artist(artist_name)
        artists_found = [
            ArtistData(
                external_artist_id=result["result"]["primary_artist"]["id"],
                name=result["result"]["primary_artist"]["name"],
            )
            for result in response.get("hits", [])
            if artist_name.lower() in result["result"]["primary_artist"]["name"].lower()
        ]

        return list(OrderedDict.fromkeys(artists_found))

    def artist_song_retriever(self, artist_id: str) -> Generator[SongData]:
        logger.info("Retrieving songs for artist ID: %s", artist_id)
        page_no = 1
        song_ids = set()

        while True:
            response = self._get_artist_song_page(artist_id, page_no)
            for song_data in response["songs"]:
                song_id = song_data["id"]
                if song_id not in song_ids:
                    song_ids.add(song_id)
                    yield self._get_song_data(song_id)

            if response["next_page"] is None:
                break

            page_no += 1

    def _get_song_data(self, song_id: str) -> SongData | None:
        song = self._get_song(song_id)["song"]

        release_date_str = song.get("release_date", "0001-01-01")
        if release_date_str is None:
            release_date_str = "0001-01-01"
        try:
            release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
        except ValueError:
            release_date = date(1, 1, 1)

        logger.info("Processing song ID: %s, artist name: %s", song_id, song["primary_artist"]["name"])
        return SongData(
            name=song["primary_artist"]["name"],
            title=song["title"],
            external_artist_id=song["primary_artist"]["id"],
            external_song_id=song["id"],
            album=song.get("song", {}).get("album", {}).get("name"),
            release_date=release_date,
            lyrics_url=song["url"],
        )


if __name__ == "__main__":
    genius_retrieval = GeniusRetrieval()
    artists = genius_retrieval.search_artists("Adele")
    for artist in artists:
        print(artist)
    artist = artists[0]
    retrieve_artist_songs = genius_retrieval.artist_song_retriever(artist.external_artist_id)
    for _ in retrieve_artist_songs:
        ...
