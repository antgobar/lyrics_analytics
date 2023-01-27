import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lyrics_analytics.background.task import Task


bp = Blueprint("search", __name__)

task = Task(
    broker_url=os.getenv("BROKER_URL", "amqp://guest:guest@localhost:5672/"),
    cache_host=os.getenv("CACHE_HOST", "localhost")
)


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("search/index.html")

    name = request.form["name"]
    error = None
    if not name:
        error = "Artist name required."

    if error is not None:
        flash(error)
        return redirect(url_for("index"))

    return redirect(url_for("search.artists", name=name))


@bp.route("/artists")
def artists():
    artist_name = request.args.get("name")
    task_id = task.send_task(
        "find_artists", artist_name
    )
    return task_id
    # found_artists = genius_service.find_artists(artist_name)
    # if len(found_artists) == 0:
    #     flash(f"No artists found under name: {artist_name}")
    #     return redirect(url_for("index"))
    # return render_template("search/artists-found.html", artists=found_artists)


@bp.route("/artist")
def artist():
    artist_id = request.args.get("id")
    data = genius_service.get_artist_songs(int(artist_id))
    if len(data) == 0:
        flash("No artist data")
        return redirect(url_for("index"))
    return render_template("search/artist-data.html", artist_data=data)
