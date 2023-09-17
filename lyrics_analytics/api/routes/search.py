import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from lyrics_analytics.api.routes.auth import login_required
from lyrics_analytics.database.queries import artist_is_ready
from lyrics_analytics.tasks.tasks import artist_song_data, find_artists

BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__)


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    if request.method == "GET":
        return render_template(f"{BASE}/index.html")
    name = request.form["artist-name"]
    return redirect(url_for(f"{BASE}.search", name=name))


@bp.route("/search", methods=("GET", "POST"))
def search():
    if request.method == "POST":
        return redirect(url_for(f"{BASE}.search", name=request.form["artist-name"]))

    name = request.args.get("name")
    artists_found = find_artists.delay(name).get()

    if not artists_found:
        flash(f"No results found for {name}")

    return render_template(f"{BASE}/index.html", artists=artists_found)


@bp.route("/artist", methods=("GET", "POST"))
def artist():
    if request.method == "POST":
        return redirect(url_for(f"{BASE}.search", name=request.form["artist-name"]))

    artist_id = request.args.get("id")
    name = request.args.get("name")

    if artist_is_ready(artist_id, name):
        return redirect(url_for(f"reports.combined_reports", artist_ids=artist_id))

    artist_song_data.delay(artist_id)
    flash(f"Fetching lyric data for {name}, check reports later")
    return render_template(f"{BASE}/index.html")
