import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from lyrics_analytics.api.routes.auth import login_required
from lyrics_analytics.database.queries import ReportsQueries
from lyrics_analytics.services.reporting import create_histogram


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
report_queries = ReportsQueries()


@bp.route("/", methods=("GET", "POST"))
@login_required
def summary():
    if request.method == "POST":
        artist_ids = request.form.getlist("row_checkbox")
        return redirect(url_for(f"{BASE}.combined_reports", artist_ids=artist_ids))
    return render_template(
        f"{BASE}/summary.html", summary_reports=report_queries.artist_lyrics_distribution()
    )


@bp.route("/plots")
@login_required
def combined_reports():
    artist_ids = request.args.getlist("artist_ids")
    no_selected_artists = len(artist_ids)
    if not (1 <= no_selected_artists <= 3):
        flash(f"Select between 1 and 3 artists, you've selected {no_selected_artists}")
        return redirect(url_for(f"{BASE}.summary"))

    songs = report_queries.songs_data(artist_ids)

    if len(songs) <= 1:
        flash("There must be more that one song to generate a report")
        return redirect(url_for(f"{BASE}.summary"))

    count_plot = create_histogram(
        songs, "lyrics_count", "name", "Number of lyrics", "Artist"
    )
    distinct_plot = create_histogram(
        songs,
        "distinct_count",
        "name",
        "Number of distinct lyrics",
        "Artist",
    )

    return render_template(f"{BASE}/plots.html", plots=[count_plot, distinct_plot])


@bp.route("/ready-count")
@login_required
def count_ready_artists():
    return f"Reports: {report_queries.count_ready_artists()}"
