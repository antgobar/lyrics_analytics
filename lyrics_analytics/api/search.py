import os
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lyrics_analytics.backend.cache import CacheService
from lyrics_analytics.backend.tasks import find_artists, get_artist_songs

bp = Blueprint("search", __name__)
cache = CacheService(host="redis")


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("search/index.html")

    name = request.form["artist-name"]

    if cache.is_stored("searched_artists", name):
        artists = cache.get_value("searched_artists", name)

    else:
        artists = find_artists.delay(name).get()
        cache.update_store("searched_artists", name, artists)

    return render_template("search/artists-found.html", artists=artists)


@bp.route("/artist")
def artist():
    artist_id = request.args.get("id")
    name = request.args.get("name")
    task = get_artist_songs.delay(artist_id)
    flash(f"Fetching lyrics for {name} - check notifications later")
    return redirect(url_for("search.artist_name", task_id=task.id, name=name))


@bp.route("/artist/<name>")
def artist_name(name):
    task_id = request.args.get("task_id")
    task = get_artist_songs.AsyncResult(task_id)
    if task.ready():
        return render_template("search/artist-data.html", artist_name=name, artist_data=task.result)
    return {"status": "Not Ready"}
