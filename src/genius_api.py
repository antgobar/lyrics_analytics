from statistics import mode
from xmlrpc.client import ResponseError

import requests
from requests.models import Response
from dotenv import dotenv_values

config = dotenv_values(".env")
ACCESS_TOKEN = config["GENIUS_CLIENT_ACCESS_TOKEN"]
BASE_URL = "http://api.genius.com"


class GeniusService:
    def __init__(self, base_url: str, access_token: str) -> None:
        self.base_url = base_url
        self.base_params = {"access_token": access_token}
        self.ping()
        
    def ping(self) -> None:
        response = requests.get(f"{self.base_url}/songs/1", params=self.base_params)
        if response.ok and response.json()["meta"]["status"] == 200:
            return True
        else:
            raise ConnectionError("Unable to connect")
        
    def handle_response(self, response) -> dict:
        if response.ok and response.json()["meta"]["status"] == 200:
            return response.json()["response"]
        raise ResponseError()
    
    def search_artist(self, artist_name: str) -> Response:
        url = f"{self.base_url}/search"
        params = self.base_params
        params["q"] = artist_name
        return requests.get(url=url, params=params)
    
    def get_artist_id(self, artist_name):
        artist_response = self.handle_response(self.search_artist(artist_name))
        
        artist_ids = []
        for result in artist_response["hits"]:
            if artist_name.lower() in result["result"]["primary_artist"]["name"].lower():
                artist_ids.append(result["result"]["primary_artist"]["id"])

        if artist_ids:
            return mode(artist_ids)
        
        return None

    def get_artist_song_page(self, artist_id: int, page_no: int) -> Response:
        url = f"{self.base_url}/artists/{artist_id}/songs"
        params = self.base_params
        params["page"] = page_no
        return requests.get(url=url, params=params)

    def get_artist_songs(self, artist_id: int, page_limit: int=1) -> list:
        page_no = 1
        songs = []
        while page_no <= page_limit:
            response = self.get_artist_song_page(artist_id, page_no).json()["response"]
            for song in response["songs"]:
                if song["lyrics_state"] == "complete":
                    songs.append(self.get_song_data(song))            
            if response["next_page"] is None:
                break
            
            page_no += 1
        
        return songs   
    
    @staticmethod
    def get_song_data(song_response):
        return {
            "artist_name": song_response["primary_artist"]["name"],
            "title": song_response["full_title"], 
            "lyrics_endpoint": song_response["path"], 
            "date": song_response["release_date_components"],
            "pyongs_count": song_response["pyongs_count"]
        }
    

def get_artist_data(artist_name, page_limit):
    genius_service = GeniusService(BASE_URL, ACCESS_TOKEN)
    artist_id = genius_service.get_artist_id(artist_name)
    return genius_service.get_artist_songs(artist_id, page_limit)


if __name__ == "__main__":
    result = get_artist_data("metallica", 1)