import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

from access_token import ACCESS_TOKEN

from lyrics_analytics.get_data import search_artist, add_lyrics
from lyrics_analytics.process_data import lyrics_metrics, stats_report, most_common, get_year
from lyrics_analytics.visualisations import lyrics_hist, make_wordcloud
from lyrics_analytics.api_fetch_timer import write_time, read_time, check_api_calls

parser=argparse.ArgumentParser(description="Get lyrics analytics and comparisons between artists")

parser.add_argument('-A',
                    '--artist',
                    nargs = '*',
                    help="""One or more artist names.
Use quotes for artist with more than one word e.g. 'Taylor Swift'
df written to csv file in data directory""",
                    type=str,
                    metavar='')

parser.add_argument('-N',
                    '--number',
                    help='max number of titles by each artist to search for',
                    type=int,
                    default = 20)

parser.add_argument('-W',
                    '--write',
                    help='Wrote df to csv file',
                    action='store_true')

parser.add_argument('-R',
                    '--read',
                    help='Read df from csv file',
                    action='store_true')

parser.add_argument('-D',
                    '--demo',
                    help='Use the demo df csv file',
                    action='store_true')

parser.add_argument('-H',
                    '--histogram',
                    nargs = 2,
                    help='''Plot histogram of lyric analytics.
1st argument (column of choice): lyrics_count, lyrics_unique_count or unique_ratio
2nd argument (category): artist or album.
Only use album category when choosing one artist''',
                    type=str,
                    metavar='')

parser.add_argument('-C',
                    '--cloud',
                    help="Create word cloud from a random song in your df",
                    type=str,
                    metavar='')

parser.add_argument('-S',
                    '--stats',
                    help='Simple stats report for artists found',
                    action='store_true')

parser.add_argument('-L',
                    '--list',
                    help="List all songs found (in case you don't know what song to pick for word cloud!)",
                    action='store_true')


args=parser.parse_args()

if __name__=="__main__":
    artists = args.artist

    if args.write:
        # Check if artists were called recently
        if check_api_calls(artists):
            df = search_artist(artists, args.number, ACCESS_TOKEN)
            df = add_lyrics(df)

            # Save record of search
            write_time(artists)
            
            # Final clean of missing values and reset index
            df = df.dropna().reset_index(drop=True)

            # Process df
            df = lyrics_metrics(df, 'lyrics')
            df = most_common(df, 'lyrics', n=1)

            # Drop rows where there are less than 10 words in total
            df = df[df['lyrics_count'] >= 10]

            df.to_csv('data/artist_data.csv', index=False)
            print(f'{artists} have been written to csv file')

    if args.read:
        df = pd.read_csv('data/artist_data.csv')

        if args.demo:
            df = pd.read_csv('data/artist_data_demo_lyrics_demo.csv')

            df = df.dropna().reset_index(drop=True)

            # Process df
            df = lyrics_metrics(df, 'lyrics')
            df = most_common(df, 'lyrics', n=1)

            # Drop rows where there are less than 10 words in total
            df = df[df['lyrics_count'] >= 10]

            df.to_csv('data/artist_data.csv', index=False)
            print(f'Demo fle read')           
        
        #df = get_year(df)

        # Stats report
        if args.stats:
            stats_report(df, 'lyrics_count')

        # Histogram plot
        # Choose between comparing all lyrics for diffeerent artsts
        # or comparing lyrics for one artist
        if args.histogram:
            if args.histogram[1] == 'album':
                if len(args.artist) > 1:
                    print('Lyric count histogram for albums only valid for one artist!')
                else:
                    lyrics_hist(df, args.histogram[0], df.loc[df.artist.isin(artists)].album)
            elif args.histogram[1] == 'artist':
                lyrics_hist(df, args.histogram[0], df.loc[df.artist.isin(artists)].artist)

        # Word cloud
        if args.cloud == 'rand':
            rand_choice = df.sample()
            c_artist = rand_choice.artist.item()
            c_title = rand_choice.title.item()
            c_words = rand_choice.lyrics.item()
            
            make_wordcloud(c_words, c_title, c_artist)

        # List songs
        if args.list:
            print(df.title)



