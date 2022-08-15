from typing import List
from collections import Counter

import requests
import musicbrainzngs

from src.lyric_store import RAW_LYRICS

musicbrainzngs.set_useragent("lyrics_analytics", "0.1", "antongb09@gmail.com")

def get_id_by_artist(artist: str) -> list:
    search_artist = artist.lower()
    results = musicbrainzngs.search_artists(query=search_artist)
    artist_list = results["artist-list"]

    artist_ids =  match_artist_id(search_artist, artist_list)

    return artist_ids  


def match_artist_id(search_artist: str, artist_list: dict) -> list:
    artist_ids = []
    for artist in artist_list:
        if artist["name"].lower() == search_artist:
            artist_ids.append(artist["id"])

    return artist_ids  


def get_lyrics(artist: str, title: str) -> str:
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    response = requests.get(url)
    return response.json()["lyrics"]


def get_works(id: str): ...


def check_artist_id(artist_name: str, artist_id: str) -> bool:
    artist_definition = musicbrainzngs.get_artist_by_id(artist_id)
    artist_name_musicbrainz = artist_def["artist"]["name"].lower()
    return artist_name.lower() == artist_name_musicbrainz


def lytic_occurrence(lyrics: list) -> dict: # could use pandas
    occurrences = Counter(tuple(lyrics))
    return dict(occurrences)

def clean_lyrics(lyrics: str, replacing_chars: List[str]) -> str:
    lyrics = lyrics.lower()
    for char in chars_to_remove:
        lyrics = lyrics.replace(char, " ")
    
    return " ".join(lyrics.split())


artist = "justin bieber"
work = "baby"
artist_id = get_id_by_artist(artist)
lyrics = get_lyrics(artist, work)



chars_to_remove = ["\n", "\r", "\t" ,"(", ")", "[", "]", ":", ",", "."]
clean_lyrics = clean_lyrics(RAW_LYRICS, chars_to_remove)
list_lyrics = clean_lyrics.split(" ")



