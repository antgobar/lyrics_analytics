from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

from lyrics_analytics.config import Config
from lyrics_analytics.database.db import mongo_collection, parse_mongo


class ReportsQueries:
    def __init__(self):
        self.artists_collection = mongo_collection("artists")
        self.song_stats_collection = mongo_collection("song_stats")

    def count_ready_artists(self):
        return self.artists_collection.count_documents({"ready": True})

    def artist_summary(self) -> list[dict]:
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
        artists = list(self.song_stats_collection.aggregate(pipeline))
        return parse_mongo(artists)

    def songs_data(self, artist_ids: list[str]) -> list[dict]:
        songs = self.song_stats_collection.find({"genius_artist_id": {"$in": artist_ids}})
        return parse_mongo(list(songs))


class AuthQueries:
    def __init__(self):
        self.user_collection = mongo_collection("users")

    def user_by_id(self, user_id: str) -> dict | None:
        user = self.user_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return parse_mongo(user)
        return None

    def register_user_if_not_exists(self, username: str, password: str) -> bool:
        if self.user_collection.find_one({"username": username}):
            return False

        self.user_collection.insert_one(
            {
                "username": username,
                "password": generate_password_hash(password + Config.PEPPER),
            }
        )

        return True

    def user_is_authorised(self, username: str, password: str) -> dict | None:
        user = self.user_collection.find_one({"username": username})

        if not user or not check_password_hash(user["password"], password + Config.PEPPER):
            return None

        return parse_mongo(user)


class SearchQueries:
    def __init__(self):
        self.artists_collection = mongo_collection("artists")

    def artist_is_ready(self, artist_id: str, artist_name: str) -> bool:
        artist = self.artists_collection.find_one({"genius_artist_id": artist_id})
        if artist is None:
            self.artists_collection.insert_one(
                {"genius_artist_id": artist_id, "name": artist_name, "ready": False}
            )
            return False

        if artist["ready"]:
            return True

        return False


class TaskQueries:
    def __init__(self):
        self.search_log_collection = mongo_collection("search_log_collection")
        self.song_stats_collection = mongo_collection("song_stats")
        self.artists_collection = mongo_collection("artists")

    def artist_previously_searched(self, artist_name: str) -> dict | None:
        return self.search_log_collection.find_one({"search_name": artist_name})

    def update_search_log(self, searched_artist: str, found_artists: list[dict]) -> None:
        self.search_log_collection.insert_one(
            {"search_name": searched_artist, "found_artists": found_artists}
        )

    def insert_many_songs_update_status(self, songs: list[dict], artist_id: str) -> dict:
        self.song_stats_collection.insert_many(songs)
        self.artists_collection.update_one(
            {"genius_artist_id": artist_id}, {"$set": {"ready": True}}
        )
        return {"genius_artist_id": artist_id, "total": len(songs), "ready": True}
