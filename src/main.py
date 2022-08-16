from types import resolve_bases
from typing import List
from datetime import datetime, date

import requests
import musicbrainzngs
import pandas as pd

from src.data_store import RAW_LYRICS
from src.utils.process_lyrics import clean_lyrics

musicbrainzngs.set_useragent("lyrics_analytics", "0.1", "antongb09@gmail.com")


def get_id_by_artist(artist: str) -> List[str]:
    search_artist = artist.lower()
    results = musicbrainzngs.search_artists(query=search_artist)
    artist_list = results["artist-list"]

    artist_ids =  match_artist_id(search_artist, artist_list)

    return artist_ids  


def check_artist_id(artist_name: str, artist_id: str) -> bool:
    artist_definition = musicbrainzngs.get_artist_by_id(artist_id)
    artist_name_musicbrainz = artist_definition["artist"]["name"]
    return artist_name.lower() == artist_name_musicbrainz.lower()


def match_artist_id(search_artist: str, artist_list: dict) -> List[str]:
    artist_ids = []
    for artist in artist_list:
        if artist["name"].lower() == search_artist:
            artist_ids.append(artist["id"])

    return artist_ids  


def get_lyrics(root_url: str, artist: str, title: str) -> str:
    url = f"{root_url}{artist}/{title}"
    try:
        response = requests.get(url)
        status = response.status_code
        if status == 200:
            print(f"Lyrics found for {artist} - {title}")
            return response.json()
        else:
            print(f"Lyrics NOT found for {artist} - {title} - status: {status}")
            return None
    except Exception as e:
        print(f"Exception thrown for {artist} - {title} - exception: {e}")
        return None


def date_YM(date_str: str, delim="-") -> date:
    return datetime.strptime(date_str[:7], f"%Y{delim}%m")


def get_works(artist_id: str) -> List[dict]:
    response = musicbrainzngs.browse_releases(artist=artist_id)
    releases = response["release-list"]

    return [
        {"title": release["title"], "date": date_YM(release["date"])} for release in releases
    ]


def get_artist_data(artist_name: str) -> List[dict]:
    artist_id = get_id_by_artist(artist)[0]
    works = get_works(artist_id)
    
    for work in works:
        lyrics = get_lyrics("https://api.lyrics.ovh/v1/", artist_name, work["title"].lower())
        if lyrics is None:
            continue
        work["lyrics"] = clean_lyrics(lyrics["lyrics"])

    return works


def cleanse_works(works: dict) -> pd.DataFrame():
    df = pd.DataFrame(works)
    df = df.drop_duplicates(subset=["title"]).dropna()
    return df.to_dict('records')


artist = "justin bieber"
works = get_artist_data(artist)
cleansed = cleanse_works(works)





