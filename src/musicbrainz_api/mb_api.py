from typing import List

import musicbrainzngs


musicbrainzngs.set_useragent("lyrics_analytics", "0.1", "antongb09@gmail.com")


def get_id_by_artist(artist: str) -> List[str]:
    search_artist = artist.lower()
    results = musicbrainzngs.search_artists(query=search_artist)
    artist_list = results["artist-list"]

    artist_ids =  match_artist_id(search_artist, artist_list)

    return artist_ids


def match_artist_id(search_artist: str, artist_list: dict) -> List[str]:
    artist_ids = []
    for artist in artist_list:
        if artist["name"].lower() == search_artist:
            artist_ids.append(artist["id"])

    return artist_ids  


def check_artist_id(artist_name: str, artist_id: str) -> bool:
    artist_definition = musicbrainzngs.get_artist_by_id(artist_id)
    artist_name_musicbrainz = artist_definition["artist"]["name"]
    return artist_name.lower() == artist_name_musicbrainz.lower()


def get_works(artist_id: str) -> List[dict]:
    response = musicbrainzngs.browse_releases(artist=artist_id)
    releases = response["release-list"]

    return [
        {"title": release["title"], "date": release["date"]} for release in releases
    ]