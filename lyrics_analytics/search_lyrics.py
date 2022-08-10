import json
import requests
import numpy as np

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

