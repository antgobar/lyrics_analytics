import pandas as pd

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
