from statistics import mode

import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
ACCESS_TOKEN = config["GENIUS_CLIENT_ACCESS_TOKEN"]
BASE_URL = "http://api.genius.com"


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


def get_song_data_single_page(artist_id: int, page_no: int=1) -> tuple:
    url = f"{BASE_URL}/artists/{artist_id}/songs"
    params = {
        "access_token": ACCESS_TOKEN
    }
    result = requests.get(url=url, params=params)
    aritst_id_response = handle_request(result)
    if aritst_id_response:
        return aritst_id_response, aritst_id_response["response"]["next_page"]
    else:
        return None, None



def get_song_data(artist_id) -> None:
    page_no = 1
    song_data = []
    while True:
        aritst_id_response, next_page = get_song_data_single_page(artist_id, page_no)
        if not aritst_id_response or not next_page:
            break
        song_data.append(aritst_id_response)
        page_no += 1
    
    print(f"Searched {page_no} pages.")
    return song_data



if __name__ == "__main__":
    artist = "metallica"
    print("Searching for", artist)
    artist_response = search_artist(artist)
    artist_id = get_artist_id(artist, artist_response)
    print(artist_id)
    song_data = get_song_data_single_page(artist_id)