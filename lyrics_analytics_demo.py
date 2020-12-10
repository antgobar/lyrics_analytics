import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from access_token import ACCESS_TOKEN

from lyrics_analytics.search_artist import search_artist
from lyrics_analytics.search_lyrics import add_lyrics
from lyrics_analytics.stats_reporting import lyrics_metrics, stats_report
from lyrics_analytics.visualisations import lyrics_hist, make_wordcloud
from lyrics_analytics.api_fetch_timer import write_time, read_time, check_api_calls
from lyrics_analytics.most_common import most_common

df = pd.read_csv('data/artist_data_demo_lyrics_demo.csv')
# df = add_lyrics(df)
df = lyrics_metrics(df, 'lyrics')

# plot histogram


lyric = df.loc[df['title'] == str('Dance for You')].lyrics.item()
make_wordcloud(lyric, 'Dance for you', 'Beyonce')

df = most_common(df, 'lyrics', n=2)

# Final clean of missing values and reset index
df = df.dropna().reset_index(drop=True)

# Convert date row into year integer values
years = [int(i[-1]) for i in df['date'].str.split("/")]
df['years'] = years
