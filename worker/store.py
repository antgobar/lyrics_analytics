from models import ArtistData, SongData


class Store:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def save_artists(self, artists: list[ArtistData]):
        # Implement saving logic here
        pass

    def save_songs(self, songs: list[SongData]):
        # Implement saving logic here
        pass

    def save_lyrics(self, song_id: str, lyrics: str):
        # Implement saving logic here
        pass
