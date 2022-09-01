import sys

from src.genius_api import search_artist, get_artist_id

artist = sys.argv[1]
print("Searching for", artist)
artist_response = search_artist(artist)
artist_id = get_artist_id(artist, artist_response)
print(artist_id)