from base64 import b64encode
import os
from io import BytesIO

from flask import Blueprint, render_template
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from lyrics_analytics.backend.db import mongo_collection, parse_mongo


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
sns.set_style("dark")
sns.light_palette("seagreen", as_cmap=True)
sns.color_palette("Set2")


@bp.route("/")
def summary():
    artists_collection = mongo_collection("song_stats")
    pipeline = [
        {
            "$group": {
                "_id": "$genius_artist_id",
                "name": {"$first": "$name"},
                "avg_lyrics": {"$avg": "$lyrics_count"},
                "song_count": {"$sum": 1},
                "max_count": {"$max": "$lyrics_count"},
                "min_count": {"$min": "$lyrics_count"}
            }
        },
    ]

    artists = list(artists_collection.aggregate(pipeline))
    return render_template(f"{BASE}/index.html", summary_reports=parse_mongo(artists))


@bp.route("/<artist_id>")
def artist(artist_id):
    song_stats_collection = mongo_collection("song_stats")
    artists_collection = mongo_collection("artists")

    songs = song_stats_collection.find({"genius_artist_id": artist_id})
    df = pd.DataFrame(parse_mongo(list(songs)))

    name = artists_collection.find_one({"genius_artist_id": artist_id})["name"]

    count_fig = sns.histplot(data=df, x="lyrics_count", kde=True)
    count_plot = create_plot_data(count_fig, "Number of lyrics")
    distinct_fig = sns.histplot(data=df, x="distinct_count", kde=True)
    distinct_plot = create_plot_data(distinct_fig, "Number of distinct lyrics")

    return render_template(
        f"{BASE}/plots.html",
        artist=name,
        plots=[count_plot, distinct_plot],
    )


def basic_metric_min_max(df, max_name, min_name, metric_col, base_cols=("title", "album", "date")):
    df = df.dropna()
    max_df = pd.DataFrame(df.loc[df["lyrics_count"].idxmax()].loc[[*base_cols, metric_col]]).transpose()
    min_df = pd.DataFrame(df.loc[df["lyrics_count"].idxmin()].loc[[*base_cols, metric_col]]).transpose()
    max_df["metric"] = max_name
    min_df["metric"] = min_name
    max_df = max_df.rename(columns={metric_col: "value"})
    min_df = min_df.rename(columns={metric_col: "value"})
    return pd.concat([max_df, min_df])


def create_plot_data(figure, xlabel):
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    buffer = BytesIO()
    figure.figure.savefig(buffer, format='png')
    plt.clf()
    return b64encode(buffer.getbuffer()).decode("ascii")


@bp.route("/query")
def query():
    # song_stats_collection = mongo_collection("song_stats")
    # song_stats_collection.update_many({"name": "Kate Bush"}, {"$set": {"genius_artist_id": "39200"}})
    # song_stats_collection.delete_many({"album": {"$type": 10}})
    return {"query": None}
