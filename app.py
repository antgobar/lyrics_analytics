import sys

from src.genius_api import (
    search_artist, 
    get_artist_id, 
    get_song_data, 
    get_song_data_single_page
)


artist = "metallica"
if len(sys.argv) > 1:
    artist = sys.argv[1]

print("Searching for", artist)
artist_response = search_artist(artist)
artist_id = get_artist_id(artist, artist_response)
song_data = get_song_data_single_page(artist_id)