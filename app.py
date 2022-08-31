import sys

from src.genius_api import search_artist

artist = sys.argv[1]
print("Searching for", artist)
works = search_artist(artist)


