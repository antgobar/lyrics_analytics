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
        self.base_params = {"access_token": access_token}
        self.ping()
        
    def ping(self) -> None:
        response = requests.get(f"{self.base_url}/account", params=self.base_params)
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
        artist_response = self.handle_response(search_artist(artist_name))
        
        artist_ids = []
        for result in artist_response["hits"]:
            if artist_name.lower() in result["result"]["primary_artist"]["name"].lower():
                artist_ids.append(result["result"]["primary_artist"]["id"])

        if artist_ids:
            return {"artist_name": artist_name, "artist_id": mode(artist_ids)}
        
        return {"artist_name": artist_name, "artist_id": None}

    def get_artist_song_page(self, artist_id: int, page_no: int=None) -> Response:
        url = f"{self.base_url}/artists/{artist_id}/songs"
        params = self.base_params
        params["page"] = page_no
        return requests.get(url=url, params=params)

    def get_artist_songs(self, artist_id: int, page_limit: int, page_no: int=None) -> list:
        page_no = 1
        songs = []
        while page_no <= page_limit:
            response = self.get_artist_song_page(artist_id, page_no)
            songs.append(response["songs"])
            
            if response["next_page"] is None:
                break
            
            page_no += 1
        
        return songs   
    
    @staticmethod
    def get_song_data(song_response):
        if song_response["lyrics_state"] == "complete":
            return {
                "title": song_response["full_title"], 
                "lyrics_endpoint": song_response["path"], 
                "date": song_response["release_date_components"]
            }
        return None
    

def handle_request(request_result: dict) -> None:
    if request_result.status_code != 200:
        print("Request", request_result.status_code)
        return
    
    response = request_result.json()
    if response["meta"]["status"] != 200:
        print("Request", request_result.status_code)
        return
    return response


def search_artist(artist_name: str) -> dict:
    url = f"{BASE_URL}/search"
    params = {
        "q": artist_name,
        "access_token": ACCESS_TOKEN
    }
    result = requests.get(url=url, params=params)
    artist_response = handle_request(result)
    if artist_response:
        print("Artist:", artist_name, True)
        return artist_response
    else:
        print("Artist:", artist_name, False)
        return


def get_artist_id(artist_name: str, artist_response: dict) -> int:
    if artist_response is None:
        return
    artist_ids = []
    for result in artist_response["response"]["hits"]:
        if artist_name.lower() in result["result"]["primary_artist"]["name"].lower():
            artist_ids.append(result["result"]["primary_artist"]["id"])

    if artist_ids:
        return mode(artist_ids)
    
    print(f"Artist: {artist_name} - NOT FOUND")
    return


def get_artist_song(artist_id: int, page_no: int=1) -> tuple:
    url = f"{BASE_URL}/artists/{artist_id}/songs"
    params = {
        "access_token": ACCESS_TOKEN
    }
    result = requests.get(url=url, params=params)
    aritst_id_response = handle_request(result)
    if aritst_id_response:
        return aritst_id_response, aritst_id_response["response"]["next_page"]
    return None, None



def get_artist_songs(artist_id, page_limit=1) -> None:
    page_no = 1
    songs = []
    while True:
        aritst_id_response, next_page = get_artist_song(artist_id, page_no)
        if next_page is None or page_no >= page_limit:
            break
        songs.append(aritst_id_response)
        page_no += 1
    
    print(f"Searched {page_no} pages.")
    return songs


def get_lyrics_endpoint(songs_response):
    song_data = []
    for song in songs_response:
        if song["lyrics_state"] == "complete":
            song_data.append(
                {
                    "title": song["full_title"], 
                    "lyrics_endpoint": song["path"], 
                    "date": song["release_date_components"]
                })
    return song_data
          

if __name__ == "__main__":
    artist = "metallica"
    print("Searching for", artist)
    artist_response = search_artist(artist)
    artist_id = get_artist_id(artist, artist_response)
    print(artist_id)
    song_data = get_artist_song(artist_id)