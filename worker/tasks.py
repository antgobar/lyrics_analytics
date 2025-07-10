from worker.genius import ArtistData, GeniusService
from worker.models import SongData


def search_artists(service: GeniusService, artist_name: str) -> list[ArtistData]:
    return service.search_artists(artist_name)


def get_artist_songs(service: GeniusService, artist_id: str) -> list[SongData]:
    get_songs = service.artist_song_retriever(artist_id)
    return [song for song in get_songs]
