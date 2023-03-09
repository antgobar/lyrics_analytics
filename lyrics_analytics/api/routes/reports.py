from base64 import b64encode
import os
from io import BytesIO

from flask import Blueprint, render_template
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns

from lyrics_analytics.api.models import User, LyricsStats


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
sns.set_style("dark")
sns.light_palette("seagreen", as_cmap=True)
sns.color_palette("Set2")


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


@bp.route("/<name>")
def artist(name):
    df = pd.DataFrame([
        {
            "name": stat.name,
            "title": stat.title,
            "album": stat.album,
            "date": stat.date,
            "lyrics_count": stat.count,
            "distinct_count": stat.distinct_count,
            "score": stat.distinct_score
        } for stat in LyricsStats.query.filter_by(name=name).all()
    ])

    basic_reports = pd.concat([
        basic_metric_min_max(df, "Longest song", "Shortest song", "lyrics_count"),
        basic_metric_min_max(df, "Most unique", "Least unique", "distinct_count"),
        basic_metric_min_max(df, "High score", "Low score", "score"),
    ])

    count_fig = sns.histplot(data=df, x="lyrics_count", kde=True)
    count_plot = create_plot_data(count_fig, name, "Lyrics count")
    distinct_fig = sns.histplot(data=df, x="distinct_count", kde=True)
    distinct_plot = create_plot_data(distinct_fig, name, "Unique count")

    return render_template(
        f"{BASE}/plots.html",
        artist=name,
        basic_reports=basic_reports.to_dict("records"),
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
    return pd.concat([max_df.rename(columns={metric_col: "value"}), min_df.rename(columns={metric_col: "value"})])


def create_plot_data(figure, title, xlabel):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    buffer = BytesIO()
    figure.figure.savefig(buffer, format='png')
    plt.clf()
    return b64encode(buffer.getbuffer()).decode("ascii")