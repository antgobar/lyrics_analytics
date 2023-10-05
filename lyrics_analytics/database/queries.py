from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd

from lyrics_analytics.config import Config
from lyrics_analytics.database.db import DbClient, parse_mongo


client = DbClient()


class ReportsQueries:
    def __init__(self):
        self.artists_collection = client.collection("artists")
        self.songs_collection = client.collection("songs")

    def count_ready_artists(self):
        return self.artists_collection.count_documents({"status": "success"})

    def artist_lyrics_distribution(self) -> tuple[list[dict], list[dict]] | None:
        songs = pd.DataFrame(self.songs_collection.find({}))
        if songs.empty:
            return None

        songs_grouped_by_artist = (
            songs.groupby("genius_artist_id")
            .agg(
                {
                    "title": "count",
                    "lyrics_count": "mean",
                    "album": "nunique",

                }
            )
            .reset_index()
        )
        artists = pd.DataFrame(self.artists_collection.find({}))
        artists_no_data = artists[artists.status == "failure"]
        artist_data = artists[artists.status.isin(["success", "pending"])]
        df = artist_data.merge(songs_grouped_by_artist, on="genius_artist_id", how="left")
        df = df.rename(
            columns={
                "genius_artist_id": "_id",
                "title": "song_count",
                "lyrics_count": "avg_lyrics",
                "album": "album_count"
            }
        )

        return df.to_dict(orient="records"), artists_no_data.to_dict(orient="records")

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
            "distinct_count": "mean",
        }
        album_info = album_grouped.agg(agg_functions)
        album_info.reset_index(inplace=True)
        return album_info.to_dict(orient="records")


class AuthQueries:
    def __init__(self) -> None:
        self.users_collection = client.collection("users")

    def user_by_id(self, user_id: str) -> dict | None:
        user = self.users_collection.find_one(
            {"_id": ObjectId(user_id), "is_active": True}
        )
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
                "is_active": True,
                "fetches": 5
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
        self.artists_collection = client.collection("artists")
        self.searches_collection = client.collection("searches")
        self.users_collection = client.collection("users")

    def artist_status(self, artist_id: str, artist_name: str) -> None | str:
        artist = self.artists_collection.find_one({"genius_artist_id": artist_id})
        if artist is None:
            self.artists_collection.insert_one(
                {"genius_artist_id": artist_id, "name": artist_name, "status": "pending"}
            )
            return None
        return artist["status"]

    def artist_previously_searched(self, artist_name: str) -> dict | None:
        return self.searches_collection.find_one({"search_name": artist_name})

    def update_search_log(
        self, searched_artist: str, found_artists: list[dict]
    ) -> None:
        self.searches_collection.insert_one(
            {"search_name": searched_artist, "found_artists": found_artists}
        )

    def decrease_fetch_count(self, user_id: str):
        self.users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$inc": {"fetches": -1}}
        )

    def get_fetch_count(self, user_id: str):
        user = self.users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        return user["fetches"]


class TaskQueries:
    def __init__(self):
        self.songs_collection = client.collection("songs")
        self.artists_collection = client.collection("artists")

    def insert_many_songs_update_status(
        self, songs: list[dict], artist_id: str
    ) -> dict:
        if not songs:
            self.artists_collection.update_one(
                {"genius_artist_id": artist_id}, {"$set": {"status": "failure"}}
            )
            return {"genius_artist_id": artist_id, "total": 0, "status": "failure"}

        self.songs_collection.insert_many(songs)
        self.artists_collection.update_one(
            {"genius_artist_id": artist_id}, {"$set": {"status": "success"}}
        )
        return {"genius_artist_id": artist_id, "total": len(songs), "status": "success"}

    def apply_song_filters(self, field, values_to_remove):
        result = self.songs_collection.delete_many({field: {"$in": values_to_remove}})
        return parse_mongo(result)


class AdminQueries:
    def __init__(self):
        self.users_collection = client.collection("users")

    def get_users(self):
        users = self.users_collection.find(
            {},
            {"password": 0},
        )
        return parse_mongo(list(users))

    def get_user(self, user_id: str):
        user = self.users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"password": 0},
        )
        return parse_mongo(user)

    def update_user(self, user_id: str, role: str, status: bool):
        response = self.users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"role": role, "is_active": status}}
        )
        return parse_mongo(response)

    def create_admin(self):
        self.users_collection.delete_many({"username": "admin"})

        self.users_collection.insert_one(
            {
                "username": "admin",
                "password": generate_password_hash(
                    Config.ADMIN_PASSWORD + Config.PEPPER
                ),
                "role": "admin",
                "is_active": True,
                "fetches": 10
            }
        )
