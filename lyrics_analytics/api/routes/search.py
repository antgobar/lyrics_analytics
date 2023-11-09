import os

from flask import Blueprint, session, render_template, request, redirect, url_for, flash

from lyrics_analytics.api.routes.auth import login_required
from lyrics_analytics.api.forms import SearchForm
from lyrics_analytics.common.database.queries import SearchQueries
from lyrics_analytics.common.services.queue import producer
from lyrics_analytics.common.services.search_artist import search_artist_by_name


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__)
search_queries = SearchQueries()


@bp.route("/", methods=("GET",))
@login_required
def index():
    return render_template(f"{BASE}/index.html")


@bp.route("/search", methods=("GET", "POST"))
@login_required
def search_artist():
    if request.method == "GET":
        return redirect(url_for("index"))

    name = request.form["artist-name"]

    been_searched = search_queries.artist_previously_searched(name)
    if been_searched:
        artists = been_searched["found_artists"]
    else:
        artists = search_artist_by_name(name)
        search_queries.update_search_log(name, artists)

    return render_template(f"{BASE}/results.html", artists=artists, searched=name)


@bp.route("/artist", methods=("GET",))
@login_required
def artist():
    artist_id = request.args.get("id")
    name = request.args.get("name")
    status = search_queries.artist_status(artist_id, name)

    if status is None:
        user_id = session["user_id"]
        fetches = search_queries.get_fetch_count(user_id)
        if fetches <= 0:
            return "No fetches left"

        search_queries.set_artist_pending(artist_id, name)
        producer(artist_id)
        search_queries.decrease_fetch_count(user_id)
        return "Fetching..."

    if status == "pending":
        return "Already fetching..."

    if status == "success":
        return "Ready"

    return "Error"
