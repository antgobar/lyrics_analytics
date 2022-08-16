from typing import List

from collections import Counter


REPLACE_CHARSET = ["\n", "\r", "\t" ,"(", ")", "[", "]", ":", ",", "."]

def lyric_occurrence(lyrics: list) -> dict: # could use pandas
    occurrences = Counter(tuple(lyrics))
    return dict(occurrences)

def clean_lyrics(lyrics: str, replacing_chars: List[str]=REPLACE_CHARSET) -> str:
    lyrics = lyrics.lower()
    for char in replacing_chars:
        lyrics = lyrics.replace(char, " ")
    return " ".join(lyrics.split())