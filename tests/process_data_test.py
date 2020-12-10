import numpy as np
import pandas as pd

def lyrics_metrics(df, column):
    '''
    Function to count lyrics word length, unique length 
    and unique index (number of unique lyrics divided by total lyrics)
    '''
    # Split lyrics string in to list of strings
    split = df[column].str.split()
    # Add new column counting number of strings (words) in list
    df[column + '_count'] = split.str.len()

    # Find number of unique lyrics
    unique_lyrics_len = []
    
    for i in split:
        unique = np.unique(i)
        unique_length = len(unique)
        unique_lyrics_len.append(unique_length)

    df[column+'_unique_count'] = unique_lyrics_len

    # Unique ratio for each song
    unique_ratio = df[column+'_unique_count'] / df[column + '_count']
    df['unique_ratio'] = unique_ratio.round(3)
    
    return df


def stats_report(df, column):
    '''
    Simple stats on artists lyrics
    '''

    stats_obj = df.groupby('artist')[column]

    lyrics_count = stats_obj.count()
    means =  stats_obj.mean().round(2)
    stdevs = stats_obj.std().round(2)
    min_len = stats_obj.min()
    max_len = stats_obj.max()
    uniqueness = df.groupby('artist')['unique_ratio'].mean().round(2)

    stats_df = pd.concat([lyrics_count,
                          min_len,
                          max_len,
                          means,
                          stdevs,
                          uniqueness], axis=1)

    stats_df.columns = ['song count',
                        'min',
                        'max',
                        'mean',
                        'stdev',
                        'uniqueness']
    
    print(stats_df)


def most_common(df, column, n = 1):
    '''
    Find most common string and its count in user set column
    parameters:
    column = usually the lyrics column
    n = the top number of most common words in the lyrics
    '''
    temp = []
    for i in df[column]:
        top_words = pd.Series(i.split()).value_counts()[:n].to_dict()
        temp.append(top_words)
      
    top_word = []
    top_count = []
    
    for i in temp:
        top_word.append(list(i.keys()))
        top_count.append(list(i.values()))
    
    col_name = 'most_common_' + column
    col_count = 'most_common_count_' + column
    
    df[col_name] = top_word
    df[col_count] = top_count
    
    return df

def get_year(df):
    '''
    Creates year column from data column
    '''
    df['year'] = df['date'].str.split("/").str[2].astype(int)

    return df
