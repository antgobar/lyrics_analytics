import os
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lyrics_analytics.backend.cache import CacheService
from lyrics_analytics.backend.tasks import find_artists, get_artist_songs


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__)

cache = CacheService(host=os.getenv("CACHE_HOST", "localhost"))


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("search/index.html")
    name = request.form["artist-name"]
    return redirect(url_for("search.artists", name=name, use_cache=True))


@bp.route("/artists", methods=("GET", "POST"))
def artists():
    if request.method == "POST":
        return redirect(url_for("search.artists", name=request.form["artist-name"], use_cache=True))

    name = request.args.get("name")
    use_cache = request.args.get("use_cache")

    if not use_cache:
        artists_found = find_artists.delay(name).get()
        return render_template("search/index.html", artists=artists_found)

    if cache.is_stored("searched_artists", name):
        artists_found = cache.get_value("searched_artists", name)
        return render_template("search/index.html", artists=artists_found, name=name)

    artists_found = find_artists.delay(name).get()

    if not artists_found:
        return render_template("search/index.html", not_found=True, name=name)

    cache.update_store("searched_artists", name, artists_found)
    return render_template("search/index.html", artists=artists_found)


@bp.route("/artist", methods=("GET", "POST"))
def artist():
    if request.method == "POST":
        return redirect(url_for("search.artists", name=request.form["artist-name"], use_cache=True))

    artist_id = request.args.get("id")
    name = request.args.get("name")

    process_key = f"{name.lower()}__{artist_id}"
    if cache.is_stored("getting_lyrics", process_key):
        flash(f"Already fetched or fetching {name} lyrics data - check reports")
        return render_template("search/index.html")

    task = get_artist_songs.delay(artist_id)
    cache.update_store("getting_lyrics", process_key, task.id)

    flash(f"Fetching lyric data for {name}, check reports later :)")
    return render_template("search/index.html")


@bp.route("/artist/<name>")
def songs(name):
    task_id = request.args.get("task_id")
    task = get_artist_songs.AsyncResult(task_id)
    if task.ready():
        return render_template("search/songs.html", artist_name=name, artist_data=task.result)
    return {"status": "Not Ready"}
