from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

from lyrics_analytics.config import Config
from lyrics_analytics.database.db import mongo_collection, parse_mongo


# REPORTS
def count_ready_artists():
    artists_collection = mongo_collection("artists")
    return artists_collection.count_documents({"ready": True})


def artist_summary() -> list[dict]:
    song_stats_collection = mongo_collection("song_stats")
    pipeline = [
        {
            "$group": {
                "_id": "$genius_artist_id",
                "name": {"$first": "$name"},
                "avg_lyrics": {"$avg": "$lyrics_count"},
                "song_count": {"$sum": 1},
            }
        },
        {"$sort": {"name": 1}},
    ]
    artists = list(song_stats_collection.aggregate(pipeline))
    return parse_mongo(artists)


def songs_data(artist_ids: list[str]) -> list[dict]:
    song_stats_collection = mongo_collection("song_stats")
    songs = song_stats_collection.find({"genius_artist_id": {"$in": artist_ids}})
    return parse_mongo(list(songs))


#  AUTH
def user_by_id(user_id: str) -> dict | None:
    user_collection = mongo_collection("users")
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return parse_mongo(user)
    return None


def register_user_if_not_exists(username: str, password: str) -> bool:
    user_collection = mongo_collection("users")
    if user_collection.find_one({"username": username}):
        return False

    user_collection.insert_one(
        {
            "username": username,
            "password": generate_password_hash(password + Config.PEPPER),
        }
    )

    return True


def user_is_authorised(username: str, password: str) -> dict | None:
    user_collection = mongo_collection("users")
    user = user_collection.find_one({"username": username})

    if not user or not check_password_hash(user["password"], password + Config.PEPPER):
        return None

    return parse_mongo(user)


# SEARCH
def artist_is_ready(artist_id: str, artist_name: str) -> bool:
    artists_collection = mongo_collection("artists")
    artist_query = artists_collection.find_one({"genius_artist_id": artist_id})
    if artist_query is None:
        artists_collection.insert_one(
            {"genius_artist_id": artist_id, "name": artist_name, "ready": False}
        )
        return False

    if artist_query["ready"]:
        return True

    return False


# TASKS
def artist_previously_searched(artist_name: str) -> dict | None:
    search_log_collection = mongo_collection("search_log_collection")
    return search_log_collection.find_one({"search_name": artist_name})


def update_search_log(searched_artist: str, found_artists: list[dict]) -> None:
    search_log_collection = mongo_collection("search_log_collection")
    search_log_collection.insert_one(
        {"search_name": searched_artist, "found_artists": found_artists}
    )


def insert_many_songs_update_status(songs: list[dict], artist_id: str) -> dict:
    song_stats_collection = mongo_collection("song_stats")
    song_stats_collection.insert_many(songs)
    artists_collection = mongo_collection("artists")
    artists_collection.update_one(
        {"genius_artist_id": artist_id}, {"$set": {"ready": True}}
    )
    return {"genius_artist_id": artist_id, "total": len(songs), "ready": True}
