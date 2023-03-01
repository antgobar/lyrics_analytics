import base64
import os
from io import BytesIO

from flask import Blueprint, render_template
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns

from lyrics_analytics.api.models import User, LyricsStats

buffer = BytesIO()

BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/")
def summary():
    artist_name = "name"
    lyrics_count = "average_count"
    distinct_count = "distinct_count"
    distinct_score = "score"
    report_data = [
        {
            artist_name: stat.name,
            lyrics_count: stat.count,
            distinct_count: stat.distinct_count,
            distinct_score: stat.distinct_score
        } for stat in LyricsStats.query.all()
    ]
    total_songs = "total"

    df = pd.DataFrame(report_data)
    grouped = df.groupby([artist_name], as_index=False).mean()
    song_counts = df.groupby([artist_name], as_index=False).size()
    song_counts = song_counts.rename(columns={"size": total_songs})
    summary_df = pd.merge(grouped, song_counts, on=artist_name)
    return render_template(f"{BASE}/index.html", summary_reports=summary_df.to_dict("records"))


@bp.route("/artist/<name>")
def artist(name):
    report_data = [
        {
            "name": stat.name,
            "lyrics_count": stat.count,
            "distinct_count": stat.distinct_count,
            "score": stat.distinct_score
        } for stat in LyricsStats.query.filter_by(name=name).all()
    ]
    df = pd.DataFrame(report_data)
    fig = sns.histplot(data=df, x="lyrics_count", kde=True)
    plt.title(f"{name}")

    buffer.truncate(0)
    buffer.seek(0)
    fig.figure.savefig(buffer, format='png')
    data = base64.b64encode(buffer.getbuffer()).decode("ascii")
    return render_template(f"{BASE}/report.html", plot_data=data)
