import os
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lyrics_analytics.backend.cache import CacheService
from lyrics_analytics.backend.tasks import find_artists, artist_song_data
from lyrics_analytics.backend import db


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__)

cache = CacheService(host=os.getenv("CACHE_HOST", "localhost"))


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("search/index.html")
    name = request.form["artist-name"]
    return redirect(url_for("search.search", name=name))


@bp.route("/search", methods=("GET", "POST"))
def search():
    if request.method == "POST":
        return redirect(url_for("search.search", name=request.form["artist-name"]))

    name = request.args.get("name")
    artists_found = find_artists.delay(name).get()

    if not artists_found:
        flash(f"No results found for {name}")

    return render_template("search/index.html", artists=artists_found)


@bp.route("/artist", methods=("GET", "POST"))
def artist():
    if request.method == "POST":
        return redirect(url_for("search.search", name=request.form["artist-name"], use_cache=True))

    artist_id = request.args.get("id")
    name = request.args.get("name")

    artists_collection = db.get_collection("lyrics_analytics", "artists")
    artist_query = artists_collection.find_one({"genius_artist_id": artist_id})

    if artist_query is None:
        artist_song_data.delay(artist_id)

        flash(f"Fetching lyric data for {name}, check reports later :)")
        return render_template("search/index.html")

    flash(f"Already fetched or fetching {name} lyrics data - check reports")
    return render_template("search/index.html")
