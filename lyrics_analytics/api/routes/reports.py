import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
import plotly.express as px

from lyrics_analytics.api.routes.auth import login_required
from lyrics_analytics.database.db import mongo_collection, parse_mongo


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


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
        {"$sort": {"name": 1}},
    ]

    artists = list(song_stats_collection.aggregate(pipeline))
    return render_template(f"{BASE}/reports.html", summary_reports=parse_mongo(artists))


@bp.route("/plots")
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
    songs = song_stats_collection.find({"genius_artist_id": {"$in": artist_ids}})
    songs = list(songs)

    if len(songs) <= 1:
        flash("There must be more that one song to generate a report")
        return redirect(url_for(f"{BASE}.summary"))

    count_plot = create_histogram(
        parse_mongo(songs), "lyrics_count", "name", "Number of lyrics", "Artist"
    )
    distinct_plot = create_histogram(
        parse_mongo(songs),
        "distinct_count",
        "name",
        "Number of distinct lyrics",
        "Artist",
    )

    return render_template(f"{BASE}/plots.html", plots=[count_plot, distinct_plot])


@bp.route("/ready-count")
def count_reports():
    artists_collection = mongo_collection("artists")
    count = artists_collection.count_documents({"ready": True})
    return f"Reports: {count}"


def create_histogram(
    data: list[dict],
    metric_field: str,
    category_field: str,
    title: str,
    category_label: str = "",
) -> str:
    df = pd.DataFrame(data)
    fig = px.histogram(
        df,
        x=metric_field,
        color=category_field,
        marginal="violin",
        hover_data=df.columns,
        nbins=20,
        barmode="overlay",
        labels={
            category_field: f"{category_label} {category_field}",
            metric_field: metric_field.replace("_", " ").title(),
        },
    )

    fig.update_layout(
        title=title,
    )

    return fig.to_html(include_plotlyjs=True, full_html=False)
