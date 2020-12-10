import pytest

import pandas as pd
import numpy as np
from process_data_test import lyrics_metrics, most_common

d = {'artist': ['Greg',
                'Greg',
                'Tom'],
     'lyrics': ['one one two three four five six six six seven',
                'seven eight nine nine ten eleven twelve 3teen 4teen 5teen',
                '6teen 7teen 8teen 8teen']}

df = pd.DataFrame(d)
df = lyrics_metrics(df, 'lyrics')

def test_most_common():
    df_test = most_common(df, 'lyrics', n = 1)
    assert df_test['most_common_lyrics'][0] == ['six']
    assert df_test['most_common_lyrics'][1] == ['nine']
    assert df_test['most_common_lyrics'][2] == ['8teen']

def test_most_common_count():
    df_test = most_common(df, 'lyrics', n = 1)
    assert df_test['most_common_count_lyrics'][0] == [3]
    assert df_test['most_common_count_lyrics'][1] == [2]
    assert df_test['most_common_count_lyrics'][2] == [2]
    
