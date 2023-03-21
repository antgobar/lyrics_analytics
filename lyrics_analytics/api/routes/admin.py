import os

from flask import Blueprint

from lyrics_analytics.backend import db

BASE = os.path.basename(__file__).split(".")[0]

bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/")
def index():
    return {"status": "admin base"}


@bp.route("/get/<artist_id>")
def get(artist_id):
    artists_collection = db.get_collection("lyrics_analytics", "artists")
    query_result = artists_collection.find_one(
        {"genius_artist_id": int(artist_id)}
    )
    return str(query_result)


@bp.route("/update/<artist_id>")
def create(artist_id):
    artists_collection = db.get_collection("lyrics_analytics", "artists")
    result = artists_collection.update_one(
        {"genius_artist_id": int(artist_id)},
        {"$set": {"ready": True}}
    )
    return {"status": result.modified_count}
