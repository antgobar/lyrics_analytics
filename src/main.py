import requests
import musicbrainzngs

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


print(get_id_by_artist("Justin Bieber"))


def get_lyrics(artist: str, title: str):
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    