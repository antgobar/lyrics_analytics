from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lyrics_analytics.services.genius_api import find_artists, get_artist_data

bp = Blueprint("search", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("search/index.html")

    artist_name = request.form["name"]
    error = None
    if not artist_name:
        error = "Artist name required."

    if error is not None:
        flash(error)
        return render_template("search/index.html")

    found_artists = find_artists(artist_name)
    if len(found_artists) == 0:
        flash(f"No artists found under name: {artist_name}")
        return render_template("search/index.html")

    return render_template("search/index.html", artists=found_artists)


@bp.route("/<id>")
def artist(id):
    data = get_artist_data(id, 1)
    if len(data) == 0:
        flash("No artist data")
        return render_template("search/index.html")
    return render_template("search/found.html", artist_data=data)
