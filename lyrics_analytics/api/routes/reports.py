import os

from flask import Blueprint, render_template
import pandas as pd

from lyrics_analytics.api.models import User, LyricsStats


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/")
def summary():
    artist_name = "Artist"
    lyrics_count = "Average lyrics per song"
    unique_count = "Average distinct lyrics per song"
    score = "Distinctness score"
    total_songs = "total songs"
    report_data = [
        {
            artist_name: stat.name,
            lyrics_count: stat.count,
            unique_count: stat.unique_count,
            score: stat.uniqueness_score
        } for stat in LyricsStats.query.all()
    ]
    df = pd.DataFrame(report_data)
    grouped = df.groupby([artist_name], as_index=False).mean()
    song_counts = df.groupby([artist_name], as_index=False).size()
    song_counts = song_counts.rename(columns={"size": total_songs})
    summary_df = pd.merge(grouped, song_counts, on=artist_name)
    summary_df = summary_df.round({
        lyrics_count: 0,
        unique_count: 0,
        score: 3
    })
    return render_template(f"{BASE}/index.html", summary_reports=summary_df.to_dict("records"))
