from typing import List

import requests
import pandas as pd

from src.process_lyrics.process_lyrics import clean_lyrics
from src.musicbrainz_api.mb_api import get_id_by_artist, get_works

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


def get_artist_data(artist_name: str) -> List[dict]:
    artist_id = get_id_by_artist(artist_name)[0]
    works = get_works(artist_id)
    
    works_with_lyrics = []
    for work in works:
        lyrics = get_lyrics("https://api.lyrics.ovh/v1/", artist_name, work["title"].lower())
        if lyrics is None:
            continue
        
        cleansed_lyrics = clean_lyrics(lyrics["lyrics"])
        work["lyrics"] = cleansed_lyrics
        
        lyrics_split = cleansed_lyrics.split(" ")
        lyrics_count = len(lyrics_split)
        work["lyrics_count"] = lyrics_count

        unique_lyrics = list(set(lyrics_split))
        unique_lyrics_count = len(unique_lyrics)
        work["lyrics_count_unique"] = unique_lyrics_count

        work["uniqueness"] = unique_lyrics_count / lyrics_count

        works_with_lyrics.append(work)

    return cleanse_works(works_with_lyrics)


def cleanse_works(works: dict) -> dict:
    df = pd.DataFrame(works)
    df = df.drop_duplicates(subset=["title"]).dropna()
    return df.to_dict('records')