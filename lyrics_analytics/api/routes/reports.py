from base64 import b64encode
import os
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from lyrics_analytics.api.routes.auth import login_required
from lyrics_analytics.backend.db import mongo_collection, parse_mongo


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
sns.set_style("dark")
sns.light_palette("seagreen", as_cmap=True)
sns.color_palette("Set2")


@bp.route("/", methods=("GET", "POST"))
@login_required
def summary():
    if request.method == "POST":
        artist_ids = request.form.getlist("row_checkbox")
        return redirect(url_for(f"{BASE}.combined_reports", artist_ids=artist_ids))

    song_stats_collection = mongo_collection("song_stats")
    pipeline = [
        {
            "$group": {
                "_id": "$genius_artist_id",
                "name": {"$first": "$name"},
                "avg_lyrics": {"$avg": "$lyrics_count"},
                "song_count": {"$sum": 1},
            }

        },
        {"$sort": {"name": 1}}
    ]

    artists = list(song_stats_collection.aggregate(pipeline))
    return render_template(f"{BASE}/index.html", summary_reports=parse_mongo(artists))


@bp.route("/<artist_id>")
@login_required
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
        artists=name,
        plots=[count_plot, distinct_plot],
    )


@bp.route("/combined")
@login_required
def combined_reports():
    artist_ids = request.args.getlist("artist_ids")
    if len(artist_ids) > 3:
        flash("Select no more than 3 artists")
        return redirect(url_for(f"{BASE}.summary"))

    if len(artist_ids) < 1:
        flash("Select at least 1 artist...")
        return redirect(url_for(f"{BASE}.summary"))

    song_stats_collection = mongo_collection("song_stats")
    songs = song_stats_collection.find({"genius_artist_id": {'$in': artist_ids}})
    parsed_songs = list(songs)

    if len(parsed_songs) <= 1:
        flash("There must be more that one song to generate a report")
        return redirect(url_for(f"{BASE}.summary"))

    df = pd.DataFrame(parse_mongo(parsed_songs))

    count_fig = sns.histplot(data=df, x="lyrics_count", hue="name", kde=True)
    count_plot = create_plot_data(count_fig, "Number of lyrics")
    distinct_fig = sns.histplot(data=df, x="distinct_count", hue="name", kde=True)
    distinct_plot = create_plot_data(distinct_fig, "Number of distinct lyrics")

    return render_template(
        f"{BASE}/plots.html",
        artist=None,
        plots=[count_plot, distinct_plot],
    )


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
    # song_stats_collection.update_many({"name": "Steel Panther"}, {"$set": {"genius_artist_id": "247279"}})
    # song_stats_collection.update_many({"name": "Metallica"}, {"$set": {"genius_artist_id": "10662"}})
    # song_stats_collection.update_many({"name": "Pantera"}, {"$set": {"genius_artist_id": "63725"}})
    # song_stats_collection.delete_many({"album": {"$type": 10}})
    return {"query": None}
