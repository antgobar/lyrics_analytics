from base64 import b64encode
import os
from io import BytesIO

from flask import Blueprint, render_template
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from lyrics_analytics.backend import db


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
sns.set_style("dark")
sns.light_palette("seagreen", as_cmap=True)
sns.color_palette("Set2")


@bp.route("/")
def summary():
    artists_collection = db.get_collection("lyrics_analytics", "song_stats")
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
    return render_template(f"{BASE}/index.html", summary_reports=db.parse_mongo(artists))


@bp.route("/<artist_id>")
def artist(artist_id):
    song_stats_collection = db.get_collection("lyrics_analytics", "song_stats")
    artists_collection = db.get_collection("lyrics_analytics", "artists")

    songs = song_stats_collection.find({"genius_artist_id": int(artist_id)})
    df = pd.DataFrame(db.parse_mongo(list(songs)))

    # basic_reports = pd.concat([
    #     basic_metric_min_max(df, "Longest song", "Shortest song", "lyrics_count"),
    #     basic_metric_min_max(df, "Most unique", "Least unique", "distinct_count"),
    #     basic_metric_min_max(df, "High score", "Low score", "score"),
    # ])

    name = artists_collection.find_one({"genius_artist_id": int(artist_id)})["name"]

    count_fig = sns.histplot(data=df, x="lyrics_count", kde=True)
    count_plot = create_plot_data(count_fig, "Lyrics count")
    distinct_fig = sns.histplot(data=df, x="distinct_count", kde=True)
    distinct_plot = create_plot_data(distinct_fig, "Unique count")

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
