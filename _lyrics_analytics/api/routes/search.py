import os

from flask import Blueprint, session, render_template, request

from _lyrics_analytics.api.routes.auth import login_required
from _lyrics_analytics.database.queries import SearchQueries
from _lyrics_analytics.worker.tasks import artist_song_data, find_artists


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__)
search_queries = SearchQueries()


@bp.route("/", methods=("GET",))
@login_required
def index():
    return render_template(f"{BASE}/index.html")


@bp.route("/search", methods=("POST",))
@login_required
def search_artist():
    name = request.form["artist-name"]
    been_searched = search_queries.artist_previously_searched(name)
    if been_searched:
        artists = been_searched["found_artists"]
    else:
        artists = find_artists.delay(name).get()
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

        artist_song_data.delay(artist_id)
        search_queries.decrease_fetch_count(user_id)
        return "Fetching..."

    if status == "pending":
        return "Already fetching..."

    if status == "success":
        return "Ready"

    return "Error"
