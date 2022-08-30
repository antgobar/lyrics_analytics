from typing import List

def get_artist_data_dummy(artist: str) -> List[dict]:
    artist_data = {
        "justin bieber": [
            {
                "title": "song A",
                "date": "2001_1_1",
                "lyrics": "la la fa fa",
                "lyrics_count": 4,
                "lyrics_count_unique": 2,
                "uniqueness": 0.5
            },
            {
                "title": "song B",
                "date": "2002_2_2",
                "lyrics": "a b c d e f",
                "lyrics_count": 6,
                "lyrics_count_unique": 6,
                "uniqueness": 1
            }
        ]
    }

    return artist_data.get(artist, [])
