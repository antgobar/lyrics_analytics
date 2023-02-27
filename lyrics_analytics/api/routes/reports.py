import base64
import os
from io import BytesIO

from flask import Blueprint, render_template
import pandas as pd
from matplotlib.figure import Figure

from lyrics_analytics.api.models import User, LyricsStats


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/")
def summary():
    artist_name = "Artist"
    lyrics_count = "Avg lyrics/song"
    distinct_count = "Avg distinct lyrics/song"
    distinct_score = "Distinctness"
    total_songs = "Total songs"
    report_data = [
        {
            artist_name: stat.name,
            lyrics_count: stat.count,
            distinct_count: stat.distinct_count,
            distinct_score: stat.distinct_score
        } for stat in LyricsStats.query.all()
    ]
    df = pd.DataFrame(report_data)
    grouped = df.groupby([artist_name], as_index=False).mean()
    song_counts = df.groupby([artist_name], as_index=False).size()
    song_counts = song_counts.rename(columns={"size": total_songs})
    summary_df = pd.merge(grouped, song_counts, on=artist_name)
    summary_df = summary_df.round({
        lyrics_count: 0,
        distinct_count: 0,
        distinct_score: 3
    })
    return render_template(f"{BASE}/index.html", summary_reports=summary_df.to_dict("records"))


@bp.route("/artist/<artist_id>")
def artist(artist_id):
    return artist_id


@bp.route("/plot")
def plot():
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"