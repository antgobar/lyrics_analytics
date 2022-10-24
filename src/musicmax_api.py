import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
API_KEY = config["MUSICMAX_API_KEY"]

BASE_URL = "https://api.musixmatch.com/ws/1.1"


def search_artist(artist_name: str, page_size: int) -> dict:
    url = f"{BASE_URL}/artist.search?q_artist={artist_name}&page_size={page_size}&apikey={API_KEY}"
    response = requests.get(url)
    
    if response.ok:
        response_json = response.json()
        ok_status = response_json["message"]["header"]["status_code"]
        if ok_status == 200:
            return {
                "status_code": 200,
                "searched_artist": artist_name,
                "matches": response_json["message"]["body"]["artist_list"]
            }
        return {"status_code": ok_status, "matches": None}
    return {"status_code": response.status_code, "matches": None}


def get_artist_id(artist_response: dict, artist_name: str):
    if artist_response["matches"] is None:
        return None
    
    for artist in artist_response["matches"]:
        if artist_name == artist["artist"]["artist_name"].lower():
            return {
                "artist_id": artist["artist"]["artist_id"],
                "artist_name": artist_name
            }
    

def search_albums(artist_id):
    url = f"{BASE_URL}/artist.albums.get?artist_id={artist_id}"
    response = requests.get(url)
    
    if response.ok:
        response_json = response.json()
        ok_status = response_json["message"]["header"]["status_code"]
        if ok_status == 200:
            return {
                "status_code": 200,
                "searched_artist_id": artist_id,
                "matches": response_json["message"]["body"]["album_list"]
            }
        return {"status_code": ok_status}
    return {"status_code": response.status_code}


def get_album_ids(album_response):
    if album_response["matches"] is None:
        return None
    albums = []
    for album in album_response["matches"]:
        album_data = {
            "album_id": album["album"]["album_id"],
            "album_name": album["album"]["album_name"]
        }
        albums.append(album_data)




artist_name = "metallica"
page_size = 5
artist_search = search_artist(artist_name, page_size)
artist_id = get_artist_id(artist_search, artist_name)
album_search = search_albums(artist_id)
album_ids = get_album_ids(album_search)
print(len(album_ids))