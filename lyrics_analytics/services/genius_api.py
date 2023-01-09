from statistics import mode

import requests
from requests.exceptions import RequestException
from requests.models import Response
from dotenv import dotenv_values


class GeniusService:
    def __init__(self, base_url: str, access_token: str) -> None:
        self.base_url = base_url
        self.base_params = {"access_token": access_token}
        self.ping()
        self.titles = []
        self.artists_found = None
        
    def ping(self):
        response = requests.get(f"{self.base_url}/songs/1", params=self.base_params)
        if response.ok and response.json()["meta"]["status"] == 200:
            return True
        else:
            raise ConnectionError("Unable to connect")
        
    @staticmethod
    def handle_response(response: Response) -> dict:
        if response.ok and response.json()["meta"]["status"] == 200:
            return response.json()["response"]
        raise RequestException()
    
    def search_artist(self, artist_name: str) -> Response:
        url = f"{self.base_url}/search"
        params = self.base_params
        params["q"] = artist_name
        return requests.get(url=url, params=params)
    
    def find_artists(self, artist_name: str) -> list[dict]:
        unhandled = self.search_artist(artist_name)
        response = self.handle_response(unhandled)
        if response is None:
            print("Not found:", artist_name)
            return
            
        artists_found = []
        for result in response["hits"]:
            print(result["type"])
            if artist_name.lower() in result["result"]["primary_artist"]["name"].lower():
                artist_data = result["result"]["primary_artist"]
                artists_found.append(
                    {"id": artist_data["id"], "name": artist_data["name"]}
                )

        self.artists_found = list({artist["id"]: artist for artist in artists_found}.values())
        return self.artists_found

    def get_artist_song_page(self, artist_id: int, page_no: int) -> Response:
        url = f"{self.base_url}/artists/{artist_id}/songs"
        params = self.base_params
        params["page"] = page_no
        params["per_page"] = 50  # max per page
        return requests.get(url=url, params=params)

    def get_artist_songs(self, artist_id: int, page_limit: int) -> list:
        page_no = 1
        songs = []
        while page_no <= page_limit:
            pre_response = self.get_artist_song_page(artist_id, page_no)
            response = self.handle_response(pre_response)
            for song in response["songs"]:
                passed_filter = self.title_filter(song["title"])
                if song["lyrics_state"] != "complete":
                    continue
                elif not passed_filter:
                    continue
                
                song_data = self.get_song_data(song)
                songs.append(song_data)
                    
            if response["next_page"] is None:
                break
            
            page_no += 1
        
        return songs   
    
    @staticmethod
    def get_song_data(song_response: dict) -> dict:
        return {
            "name": song_response["primary_artist"]["name"],
            "title": song_response["title"], 
            "lyrics_url": song_response["url"], 
            "date": song_response["release_date_components"]
        }
    
    def title_filter(self, title: str) -> bool:
        title = title.lower()
        
        replace_patterns = ("\u2014", )
        for pattern in replace_patterns:    
            title = title.replace(pattern, " ")
    
        patterns = ("(live", "[live", "(demo", "[", "demo")
        for pattern in patterns:
            if pattern in title:
                return False
        
        if title in self.titles:
            return False
        
        self.titles.append(title)
        return True


def connect_genius() -> tuple:
    config = dotenv_values(".env")
    base_url = "http://api.genius.com"
    access_token = config["GENIUS_CLIENT_ACCESS_TOKEN"]
    return base_url, access_token


def find_artists(artist_name):
    base_url, access_token = connect_genius()
    genius_service = GeniusService(base_url, access_token)
    return genius_service.find_artists(artist_name)


def get_artist_data(artist_id, page_limit):
    base_url, access_token = connect_genius()
    genius_service = GeniusService(base_url, access_token)
    return genius_service.get_artist_songs(artist_id, page_limit)
