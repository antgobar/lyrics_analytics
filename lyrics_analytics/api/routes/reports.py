import os

import pandas as pd
import plotly.express as px
from flask import Blueprint, flash, redirect, render_template, request, url_for

from lyrics_analytics.api.routes.auth import login_required
from lyrics_analytics.database.queries import (
    artist_summary,
    count_ready_artists,
    songs_data,
)

BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/", methods=("GET", "POST"))
@login_required
def summary():
    if request.method == "POST":
        artist_ids = request.form.getlist("row_checkbox")
        return redirect(url_for(f"{BASE}.combined_reports", artist_ids=artist_ids))
    return render_template(f"{BASE}/summary.html", summary_reports=artist_summary())


@bp.route("/plots")
@login_required
def combined_reports():
    artist_ids = request.args.getlist("artist_ids")
    no_selected_artists = len(artist_ids)
    if not (1 <= no_selected_artists <= 3):
        flash(f"Select between 1 and 3 artists, you've selected {no_selected_artists}")
        return redirect(url_for(f"{BASE}.summary"))

    songs = songs_data(artist_ids)

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
def count_reports():
    return f"Reports: {count_ready_artists()}"


def create_histogram(
    data: list[dict],
    metric_field: str,
    category_field: str,
    title: str,
    category_label: str = "",
) -> str:
    df = pd.DataFrame(data)

    labels = {
        category_field: f"{category_label} {category_field}",
        metric_field: metric_field.replace("_", " ").title(),
    }

    fig = px.histogram(
        df,
        x=metric_field,
        color=category_field,
        marginal="violin",
        hover_data=df.columns,
        nbins=20,
        barmode="overlay",
        labels=labels,
        title=title,
    )

    return fig.to_html(include_plotlyjs=True, full_html=False)
