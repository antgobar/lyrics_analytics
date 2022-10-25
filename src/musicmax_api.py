import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
API_KEY = config["MUSICMAX_API_KEY"]

BASE_URL = "https://api.musixmatch.com/ws/1.1"


def search_artist(artist_name: str, page_size: int) -> dict:
    url = f"{BASE_URL}/artist.search"
    params = {
        "q_artist": artist_name,
        "page_size": page_size,
        "apikey": API_KEY
    }
    response = requests.get(url=url, params=params)
    
    if response.ok:
        response_json = response.json()
        ok_status = response_json["message"]["header"]["status_code"]
        if ok_status == 200:
            return response_json["message"]["body"]["artist_list"]
        raise Exception(f"Searching {artist_name=} - {ok_status}") 
    raise Exception(f"Searching {artist_name=} - {response.status_code}") 
     

def get_artist_id(artist_response: dict, artist_name: str):
    for artist in artist_response:
        if artist_name == artist["artist"]["artist_name"].lower():
            return artist["artist"]["artist_id"]
    raise Exception(f"{artist_name=} not found")


def search_albums(artist_id, page_size=10):
    url = f"{BASE_URL}/artist.albums.get"
    params = {
        "artist_id": artist_id,
        "page_size": page_size,
        "apikey": API_KEY
    }
    response = requests.get(url=url, params=params)
    
    if response.ok:
        response_json = response.json()
        ok_status = response_json["message"]["header"]["status_code"]
        if ok_status == 200:
            return response_json["message"]["body"]["album_list"]
        raise Exception(f"Searching {artist_id=} - {ok_status}")
    raise Exception(f"Searching {artist_id=} - {response.status_code}") 


def get_album_ids(album_response):
    albums = []
    for album in album_response:
        albums.append({
            "album_id": album["album"]["album_id"],
            "album_name": album["album"]["album_name"],
            "album_release_date": album["album"]["album_release_date"]
        })
    return albums


def search_tracks(album_id):
    url = f"{BASE_URL}/album.tracks.get"
    params = {
        "album_id": album_id,
        "f_has_lyrics": True,
        "apikey": API_KEY
    }
    response = requests.get(url=url, params=params)
    
    if response.ok:
        response_json = response.json()
        ok_status = response_json["message"]["header"]["status_code"]
        if ok_status == 200:
            return response_json["message"]["body"]["track_list"]
        raise Exception(f"Searching {album_id=} - {ok_status}")
    raise Exception(f"Searching {album_id=} - {response.status_code}")


def get_track_ids(track_response):
    tracks = []
    for track in track_response:
        tracks.append({
            "track_id": track["track"]["track_id"],
            "track_name": track["track"]["track_name"]
        })
    return tracks


def search_lyrics(track_id):
    url = f"{BASE_URL}/track.lyrics.get"
    params = {
        "track_id": track_id,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    if response.ok:
        response_json = response.json()
        ok_status = response_json["message"]["header"]["status_code"]
        if ok_status == 200:
            return response_json["message"]["body"]["lyrics"]
        raise Exception(f"Searching {track_id=} - {ok_status}")
    raise Exception(f"Searching {track_id=} - {response.status_code}")


def get_lyrics(lyrics_response): ...



artist_name = "metallica"
page_size = 2
artist_search = search_artist(artist_name, page_size)
artist_id = get_artist_id(artist_search, artist_name)
album_search = search_albums(artist_id)
album_ids = get_album_ids(album_search)
album_id = album_ids[0]["album_id"]
track_search = search_tracks(album_id)
track_data = get_track_ids(track_search)
track_id = track_data[0]["track_id"]
lyrics_search = search_lyrics(track_id)