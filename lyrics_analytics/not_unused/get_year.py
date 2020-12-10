import pandas as pd
import numpy as np

def get_year(df):
    '''
    Creates year column from data column
    '''
    df['year'] = df['date'].str.split("/").str[2].astype(int)

    return df

    
        
