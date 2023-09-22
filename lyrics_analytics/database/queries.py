from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd

from lyrics_analytics.config import Config
from lyrics_analytics.database.db import DbClient, parse_mongo


client = DbClient()
artists_collection = client.collection("artists")
songs_collection = client.collection("songs")
searches_collection = client.collection("searches")
users_collection = client.collection("users")


class ReportsQueries:
    def __init__(self):
        self.artists_collection = artists_collection
        self.songs_collection = songs_collection

    def count_ready_artists(self):
        return self.artists_collection.count_documents({"ready": True})

    def artist_lyrics_distribution(self) -> list[dict] | None:
        songs = pd.DataFrame(self.songs_collection.find({}))
        if songs.empty:
            return None
        songs_grouped_by_artist = (
            songs.groupby("genius_artist_id")
            .agg({"title": "count", "lyrics_count": "mean"})
            .reset_index()
        )
        artists = pd.DataFrame(self.artists_collection.find({}))

        df = artists.merge(songs_grouped_by_artist, on="genius_artist_id", how="left")
        df = df.rename(
            columns={
                "genius_artist_id": "_id",
                "title": "song_count",
                "lyrics_count": "avg_lyrics",
            }
        )

        return df.to_dict(orient="records")

    def songs_data(self, artist_ids: list[str]) -> list[dict]:
        songs = self.songs_collection.find({"genius_artist_id": {"$in": artist_ids}})
        return parse_mongo(list(songs))

    def album_lyrics_distribution(self, artist_ids: list[str]) -> list[dict]:
        result = self.songs_collection.find({"genius_artist_id": {"$in": artist_ids}})
        songs = pd.DataFrame(result)
        songs["release_date"] = pd.to_datetime(songs["release_date"])
        album_grouped = songs.groupby("album")
        agg_functions = {
            "name": "first",
            "release_date": "max",
            "lyrics_count": "mean",
            "distinct_count": "mean"
        }
        album_info = album_grouped.agg(agg_functions)
        album_info.reset_index(inplace=True)
        return album_info.to_dict(orient="records")


class AuthQueries:
    def __init__(self):
        self.users_collection = users_collection

    def user_by_id(self, user_id: str) -> dict | None:
        user = self.users_collection.find_one({"_id": ObjectId(user_id), "active": True})
        if user:
            return parse_mongo(user)
        return None

    def register_user_if_not_exists(self, username: str, password: str) -> bool:
        if self.users_collection.find_one({"username": username}):
            return False

        self.users_collection.insert_one(
            {
                "username": username,
                "password": generate_password_hash(password + Config.PEPPER),
                "role": "user",
                "active": True
            }
        )

        return True

    def user_is_authorised(self, username: str, password: str) -> dict | None:
        user = self.users_collection.find_one({"username": username})

        if not user or not check_password_hash(
            user["password"], password + Config.PEPPER
        ):
            return None

        return parse_mongo(user)

    def user_is_admin(self, username: str):
        user = self.users_collection.find_one({"username": username, "role": "admin"})
        return parse_mongo(user)


class SearchQueries:
    def __init__(self):
        self.artists_collection = artists_collection

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
        self.searches_collection = searches_collection
        self.songs_collection = songs_collection
        self.artists_collection = artists_collection

    def artist_previously_searched(self, artist_name: str) -> dict | None:
        return self.searches_collection.find_one({"search_name": artist_name})

    def update_search_log(
        self, searched_artist: str, found_artists: list[dict]
    ) -> None:
        self.searches_collection.insert_one(
            {"search_name": searched_artist, "found_artists": found_artists}
        )

    def insert_many_songs_update_status(
        self, songs: list[dict], artist_id: str
    ) -> dict:
        self.songs_collection.insert_many(songs)
        self.artists_collection.update_one(
            {"genius_artist_id": artist_id}, {"$set": {"ready": True}}
        )
        return {"genius_artist_id": artist_id, "total": len(songs), "ready": True}

    def apply_song_filters(self, field, values_to_remove):
        result = self.songs_collection.delete_many({field: {"$in": values_to_remove}})
        return parse_mongo(result)


class AdminQueries:
    def __init__(self):
        self.users_collection = users_collection

    def get_users(self):
        users = self.users_collection.find(
            {"username": {"$ne": "admin"}},
            {"_id": 1, "username": 1, "role": 1, "active": 1}
        )
        return parse_mongo(list(users))

    def get_user(self, user_id: str):
        user = self.users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"_id": 1, "username": 1, "role": 1, "active": 1}
        )
        return parse_mongo(user)

    def create_admin(self):
        admin = self.users_collection.find_one(
            {"username": "admin", "role": "admin"},
            {"username": 1, "role": 1, "active": 1}
        )

        if not list(admin):
            self.users_collection.insert_one(
                {
                    "username": "admin",
                    "password": generate_password_hash("admin" + Config.PEPPER),
                    "role": "admin",
                    "active": True
                }
            )
