# Lyrics Analytics
### Python CLI program that fetches data for user defined musical artists
Fetch artist data from the genius API and lyrics (only) from lyricsovh APIs (see resources)
### __Before you begin create a genius account and get an access token (see resources below)__
### How to use:
* This was written in `Python 3.8.1`
* Download this repo, open up terminal and navigate to `lyrics_analytics`
##### * _IMPORTANT_ open up `access_token.py` and paste in your genius API **access token**
Like this: `ACCESS_TOKEN = '<your access token from your genius API account>'`
* Create a python virtual environment
* Install required libraries:\
`python3 pip install -r requirements.txt`
* Check out how to use the command line interface:\
`python3 lyrics_analytics_main.py -h`
* Think of musical artists you're interested in\
e.g. Coldplay, Taylor Swift and Queen
* Search for artists with the `-W` flag:\
`python3 lyrics_analytics_main.py -W -A Coldplay 'Taylor Swift' Queen -N 30`\
`-A` = artists\
`-N` = number of songs to search for, both required\
##### _IMPORTANT_ artists with more than one word e.g. Taylor Swift _must_ be written with quotes to be read as one entry
##### for example `-A Coldplay 'Taylor Swift'`
* The data has been searched, processed and written to a csv file. path:\
`'data/artist_data.csv'`
* Now you are ready to get useful information using the read `-R` flag:\
`python3 lyrics_analytics_main.py -R -A Coldplay -H lyrics_count album` to plot a histogram of word counts for different albums\
`python3 lyrics_analytics_main.py -R -A Coldplay 'Taylor Swift' -H lyrics_unique_count artist` to compare unique lyric counts for chosen artists (not necessarily all of the artists you originally searched for)\
`python3 lyrics_analytics_main.py -R -S` for a stats report on lyrics count of your df\
`python3 lyrics_analytics_main.py -R -C rand` to plot a word cloud of a randomly chosen artist and song title
* If you want to get straight to looking at the analysis you can use the demo csv by including the `-D` flag
### Resources:
* genius api: https://docs.genius.com/
* some ideas from this article [How to Analyze Emotions and Words of the Lyrics From your Favorite Music Artist](https://towardsdatascience.com/how-to-analyze-emotions-and-words-of-the-lyrics-from-your-favorite-music-artist-bbca10411283)
* lyrics api: https://lyricsovh.docs.apiary.io/
### Ideas for the future;
* Analysis of lyrics changing over time
* Lematization of lyrics and sentiment analysis with natural language processing (NLP)
