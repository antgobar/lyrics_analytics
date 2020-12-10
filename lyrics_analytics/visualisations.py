import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS

def lyrics_hist(df, column, category):
    '''
    function takes df column to plot histogram
    for a given category e.g. artist or albums
    '''
    
    sns.histplot(data=df,
                 x=column,
                 hue=category,
                 kde=True,
                 common_norm=False)

    plt.title(f'Histogram of {column}')
    plt.show()



def make_wordcloud(lyrics, title, artist):
    '''
    Given title lyrics, produce a wordcloud 
    '''
    lyrics = lyrics.split()
    word_str = ' '.join(lyrics)

    wordcloud = WordCloud(width = 600,
                          height = 600,
                          background_color ='white',
                          stopwords = STOPWORDS,
                          min_font_size = 10,
                          collocations = False
                          ).generate(word_str)

    plt.figure(figsize = (6, 6), facecolor = None)
    plt.title(f'Wordcloud of {title} by {artist}')
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    
    
    plt.show()
