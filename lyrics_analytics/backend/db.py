import pandas as pd
from sqlalchemy import create_engine

from lyrics_analytics.config import Config


def get_engine():
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)


def df_writer(data, table_name):
    df = pd.DataFrame(data)
    engine = get_engine()
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
