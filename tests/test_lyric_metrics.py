import pytest

import pandas as pd
import numpy as np
from process_data_test import lyrics_metrics

d = {'artist': ['Greg',
                'Greg',
                'Tom'],
     'lyrics': ['one one two three four five six six six seven',
                'seven eight nine nine ten eleven twelve 3teen 4teen 5teen',
                '6teen 7teen 8teen']}

df = pd.DataFrame(d)
df_test = lyrics_metrics(df, 'lyrics')

def test_lyric_count():
    assert df_test['lyrics_count'][0] == 10
    assert df_test['lyrics_count'][1] == 10
    assert df_test['lyrics_count'][2] == 3

def test_lyric_unique_count():
    assert df_test['lyrics_unique_count'][0] == 7
    assert df_test['lyrics_unique_count'][1] == 9
    assert df_test['lyrics_unique_count'][2] == 3

def test_unique_ratio():
    assert df_test['unique_ratio'][0] == 0.7
    assert df_test['unique_ratio'][1] == 0.9
    assert df_test['unique_ratio'][2] == 1
    
    
