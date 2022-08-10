import numpy as np
import pandas as pd
import json
import requests
import lyricsgenius as genius

def search_artist(artists, max_songs, ACCESS_TOKEN):
    '''
    This function uses the lyricsgenius libary (genius API) to extract 
    the fields: song title, artist, album, date and lyrics
    Stored in a pandas dataframe.
    parameters:
    artists = artist(s) or band(s) to search, passed as a list
    e.g. artists = ['Coldplay', 'Taylor Swift']
    max_songs = maximum number of songs to search for 
    Songs by artist are sorted by 'popularity'
    access_token = your access token of the genius API
    '''

    total_searches = len(artists) * max_songs
        
    api = genius.Genius(ACCESS_TOKEN)
    
    # Initialise fields lists 
    list_title = [] 
    list_artist = []
    list_lyrics = []
    list_album = []
    list_date = []
    
    
    # Iterate over artists list
    for i_artist in artists:
        artist = api.search_artist(i_artist,
                                   max_songs=max_songs,
                                   sort='popularity')
        try:
            songs = artist.songs
        except:
            # api.search_artist() will return a print statement
            # indiating no artist found if none is found
            pass
        else:
            for song in songs:
                list_artist.append(song.artist)
                list_title.append(song.title)
                list_album.append(song.album)
                list_date.append(song.year)

    df = pd.DataFrame({'artist':list_artist,
                       'title':list_title,
                       #'lyrics_genius_api':list_lyrics,
                       'album':list_album,
                        'date':list_date})

    df['lyrics'] = np.nan # lyrics to be added by add_lyrics and get_lyrics functions

    return df


def get_lyrics(artist, title):
    '''
    Function that uses "https://lyrics.ovh/" API to fetch lyrics
    from a given artist and song title.
    This function cleans lyrics to remove unwanted characters.
    Returns one string containing the lyrics (not split)
    '''
    
    base_url = 'https://api.lyrics.ovh/v1/' + artist + '/' + title

    response = requests.get(base_url)
    status_code = response.status_code
    
    if status_code == 200:
        
        json_data = json.loads(response.content)
        lyrics = json_data['lyrics']
        # make all lyrics lower case
        lyrics = lyrics.lower()
        # Remove characters to isolate words
        unwanted_chars = ['\n', '\r', '(', ')', '[', ']', '.', '!', ",",
                          '"\"', '/',
                          'chorus', 'verse', 'intro', 'outro',
                          'instrumental', 'guitar', 'solo', 'drums']

        cleaned_lyrics = []
        
        for line in lyrics:
            if line in unwanted_chars:
                # Put a space instead of unwanted characters
                cleaned_lyrics.append(' ')

            else:
                cleaned_lyrics.append(line)

        lyrics = ''.join(cleaned_lyrics)

        # Final filter of unwanted whitespace
        lyrics = ' '.join(lyrics.split())

        return lyrics

    elif status_code != 200:
        print(f'''Status code {status_code}
{title} by {artist} not found''')

        return 'NA'


def add_lyrics(df):
    '''
    Function that swaps out lyrics field in df 
    for lyrics found via get_lyrics function.
    Lyrics found via genius API are harder to clean
    e.g. they contain strings such as [verse1], or name
    the artist at the begining of a verse.
    '''

    new_lyrics = []
    for index, track in df.iterrows():
        better_lyrics = get_lyrics(str(track.artist), str(track.title))
        new_lyrics.append(better_lyrics)

    # df['lyrics_ovh_api'] = new_lyrics
    df['lyrics'] = new_lyrics
    
    return df
