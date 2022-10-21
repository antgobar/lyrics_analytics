import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
API_KEY = config["MUSICMAX_API_KEY"]

BASE_URL = "https://api.musixmatch.com/ws/1.1"


def search_artist(artist_name: str, page_size: int) -> dict:
    url = f"{BASE_URL}/artist.search?q_artist={artist_name}&page_size={page_size}&apikey={API_KEY}"
    
    response = requests.get(url)
    if response.ok:
        return response.json()

def get_artist_ids(artist_response: dict, artist_name: str):
    artist_list = []
    for artist in artist_response["message"]["body"]["artist_list"]:
        artist_list.append(artist["artist"])

    artist_id_name = []
    for artist in artist_list:
        found_artist_name = artist["artist_name"].lower()
        if artist_name in found_artist_name:
            artist_id_name.append((artist["artist_id"], found_artist_name))
    
    return artist_id_name


artist_name = "prodigy"
page_size = 5
artist_search = search_artist(artist_name, page_size)
artist_ids = get_artist_ids(artist_search, artist_name)
