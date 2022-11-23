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
        
    def ping(self):
        response = requests.get(f"{self.base_url}/songs/1", params=self.base_params)
        if response.ok and response.json()["meta"]["status"] == 200:
            return True
        else:
            raise ConnectionError("Unable to connect")
        
    def handle_response(self, response) -> dict:
        if response.ok and response.json()["meta"]["status"] == 200:
            return response.json()["response"]
        raise RequestException()
    
    def search_artist(self, artist_name: str) -> Response:
        url = f"{self.base_url}/search"
        params = self.base_params
        params["q"] = artist_name
        return requests.get(url=url, params=params)
    
    def get_artist_id(self, artist_name):
        artist_response = self.handle_response(self.search_artist(artist_name))
        if artist_response is None:
            print("Not found:", artist_name)
            return
            
        artist_ids = []
        for result in artist_response["hits"]:
            if artist_name.lower() in result["result"]["primary_artist"]["name"].lower():
                artist_ids.append(result["result"]["primary_artist"]["id"])

        if artist_ids:
            return mode(artist_ids)
        
        return

    def get_artist_song_page(self, artist_id: int, page_no: int) -> Response:
        url = f"{self.base_url}/artists/{artist_id}/songs"
        params = self.base_params
        params["page"] = page_no
        return requests.get(url=url, params=params)

    def get_artist_songs(self, artist_id: int, page_limit: int=1) -> list:
        page_no = 1
        songs = []
        while page_no <= page_limit:
            
            response = self.handle_response(self.get_artist_song_page(artist_id, page_no))
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
    def get_song_data(song_response):
        return {
            "artist_name": song_response["primary_artist"]["name"],
            "title": song_response["title"], 
            "lyrics_url": song_response["url"], 
            "date": song_response["release_date_components"],
            "pyongs_count": song_response["pyongs_count"]
        }
    
    def title_filter(self, title):
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


def connect_genius():
    config = dotenv_values(".env")
    base_url = "http://api.genius.com"
    access_token = config["GENIUS_CLIENT_ACCESS_TOKEN"]
    return base_url, access_token


def get_artist_data(artist_name, page_limit):
    base_url, access_token = connect_genius()
    genius_service = GeniusService(base_url, access_token)
    artist_id = genius_service.get_artist_id(artist_name)
    return genius_service.get_artist_songs(artist_id, page_limit)


if __name__ == "__main__":
    result = get_artist_data("metallica", 2)