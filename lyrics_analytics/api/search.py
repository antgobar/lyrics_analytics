import os
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lyrics_analytics.backend.task import Task
from lyrics_analytics.services.genius_api import GeniusService

bp = Blueprint("search", __name__)

genius = GeniusService("http://api.genius.com", os.getenv("GENIUS_CLIENT_ACCESS_TOKEN"))

task = Task(
    message_broker_url=os.getenv("BROKER_URL", "amqp://guest:guest@localhost:5672/"),
    cache_host=os.getenv("CACHE_HOST", "localhost"),
    services=(genius, )
)
task.start_worker()


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

    task_id = task.send_task(
        "GeniusService", "find_artists", name
    )
    response = task.get_task_result(task_id, get_now=True)
    return render_template("search/artists-found.html", artists=response["data"])


@bp.route("/artist")
def artist():
    artist_id = request.args.get("id")
    name = request.args.get("name")
    task_id = task.send_task(
        "GeniusService", "get_artist_songs", artist_id
    )
    return redirect(url_for("search.artist_name", task_id=task_id, name=name))


@bp.route("/artist/<name>")
def artist_name(name):
    task_id = request.args.get("task_id")
    response = task.get_task_result(task_id, get_now=True)
    if response["status"] == "PENDING":
        return "Try again later"
    if response["data"] is None:
        flash("No artist data found")
        return redirect(url_for("index"))
    return render_template("search/artist-data.html", artist_name=name, artist_data=response["data"])
