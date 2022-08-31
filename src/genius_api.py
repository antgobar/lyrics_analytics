import requests

from dotenv import dotenv_values

config = dotenv_values(".env")
ACCESS_TOKEN = config["CLIENT_ACCESS_TOKEN"]
BASE_URL = "http://api.genius.com/"


def search_artist(artist_name: str):
    url = f"{BASE_URL}search?q={artist_name}&access_token={ACCESS_TOKEN}"
    result = requests.get(url)
    if result.status_code != 200:
        print(f"Artist: {artist_name} - NOT FOUND")
        return
    else:
        print(f"Artist: {artist_name} - FOUND")
        return result.json()
