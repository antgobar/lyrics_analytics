import os

from flask import Blueprint, render_template
import pandas as pd

from lyrics_analytics.api.models import User, LyricsStats


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/")
def summary():
    report_data = [
        {
            "Name": stat.name,
            "Count": stat.count,
            "Unique count": stat.unique_count,
            "Score": stat.uniqueness_score
        } for stat in LyricsStats.query.all()
    ]
    df = pd.DataFrame(report_data)
    grouped = df.groupby(["Name"], as_index=False).mean()
    song_counts = df.groupby(["Name"], as_index=False).size()
    song_counts = song_counts.rename(columns={"size": "Total songs"})
    summary_df = pd.merge(grouped, song_counts, on="Name")
    summary_df = summary_df.round({
        "Count": 0,
        "Unique count": 0,
        "Score": 3
    })
    return render_template(f"{BASE}/index.html", summary_reports=summary_df.to_dict("records"))
