from lyrics_analytics.services.genius_api import genius_service


genius = genius_service(test_connection=False)


REGISTERED_TASKS = (
    genius.find_artists,
    genius.get_artist_songs
)
