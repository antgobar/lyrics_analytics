from worker.genius import GeniusService


def search_artists(service: GeniusService, artist_name: str):
    return service.search_artists(artist_name)


def get_artist_songs(service: GeniusService, artist_id: str):
    get_songs = service.artist_song_retriever(artist_id)
    for song in get_songs:
        print(song)
