from typing import Callable
import logging
from datetime import date

import requests
from requests.models import Response
from dotenv import dotenv_values

from lyrics_analytics.services.scraper import ScraperService


class GeniusService:
    def __init__(self, _base_url: str, access_token: str, healthcheck=True) -> None:
        self._base_url = _base_url
        if access_token is None:
            access_token = dotenv_values(".env.secrets").get("GENIUS_CLIENT_ACCESS_TOKEN")
        self._base_params = {"access_token": access_token}
        self.titles = []
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

    def find_artists(self, artist_name: str) -> list[dict] or None:
        response = self._search_artist(artist_name)
        if response is None:
            logging.info(f"Not found: {artist_name}")
            return []

        artists_found = []
        for result in response["hits"]:
            if artist_name.lower() in result["result"]["primary_artist"]["name"].lower():
                artist_data = result["result"]["primary_artist"]
                artists_found.append(
                    {"id": artist_data["id"], "name": artist_data["name"]}
                )

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

    def get_artist_songs(self, artist_id: int) -> list:
        artist_name = self._get_artist(artist_id)["artist"]["name"].lower()
        page_no = 1
        songs = []
        while True:
            response = self._get_artist_song_page(artist_id, page_no)
            for song in response["songs"]:
                passed_filter = self._title_filter(song["title"])
                is_primary_artist = artist_name == song["primary_artist"]["name"].lower()
                if song["lyrics_state"] != "complete" or not passed_filter or not is_primary_artist:
                    continue

                song_data = self._get_song_data(song)
                songs.append(song_data)
                    
            if response["next_page"] is None:
                break
            
            page_no += 1

        self.titles = []
        return songs   
    
    @staticmethod
    def _lyrics_stat_summary(lyrics):
        lyrics = lyrics.split(" ")
        count = len(lyrics)
        unique_count = len(set(lyrics))
        return {
            "count": count,
            "unique_count": unique_count,
            "unique_score": unique_count / count
        }

    @staticmethod
    def _parse_date_components(date_components: dict) -> date:
        year = date_components.get("year") or 1
        month = date_components.get("month") or 1
        day = date_components.get("day") or 1
        return date(year, month, day)

    def _get_song_data(self, song_response: dict) -> dict:
        song = self._get_song(song_response["id"])["song"]
        lyrics = ScraperService.get_lyrics(song_response["url"])
        stat_summary = self._lyrics_stat_summary(lyrics)
        album_data = song.get("album")
        if album_data is None:
            album = None
        else:
            album = album_data.get("name")

        date_components = song_response.get("release_date_components")
        if type(date_components) is not dict:
            date_components = {}

        metadata = {
            "name": song_response["primary_artist"]["name"],
            "title": song_response["title"],
            "album": album,
            "date": self._parse_date_components(date_components)
        }
        return {**metadata, **stat_summary}
    
    def _title_filter(self, title: str) -> bool:
        title = title.lower()
        
        replace_patterns = ("\u2014", )
        for pattern in replace_patterns:    
            title = title.replace(pattern, " ")
    
        patterns = ("(", "[", "demo", "tour", "award", "speech", "annotated")
        for pattern in patterns:
            if pattern in title:
                return False
        
        if title in self.titles:
            return False
        
        self.titles.append(title)
        return True
