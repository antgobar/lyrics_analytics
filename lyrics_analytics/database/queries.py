import pandas as pd
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

from lyrics_analytics.config import Config
from lyrics_analytics.database.db import DbClient, parse_mongo

client = DbClient()


ARTIST_NAME_FIELD = "name"
DOCUMENT_ID_FIELD = "_id"
ARTIST_ID_FIELD = "genius_artist_id"
ARTIST_STATUS_FIELD = "status"
SONG_TITLE_FIELD = "title"
LYRICS_COUNT_FIELD = "lyrics_count"
ALBUM_FIELD = "album"
SONG_RELEASE_DATE_FIELD = "release_date"
DISTINCT_COUNT_FIELD = "distinct_count"
USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"
USER_ROLE_FIELD = "role"
USER_IS_ACTIVE_FIELD = "is_active"
USER_FETCHES_LEFT_FIELD = "fetches"


class ReportsQueries:
    def __init__(self):
        self.artists_collection = client.collection("artists")
        self.songs_collection = client.collection("songs")

    def count_ready_artists(self):
        return self.artists_collection.count_documents({ARTIST_STATUS_FIELD: "success"})

    def artist_lyrics_distribution(self) -> tuple[list[dict], list[dict]] | None:
        songs = pd.DataFrame(self.songs_collection.find({}))
        songs = songs.drop([DOCUMENT_ID_FIELD, ARTIST_NAME_FIELD], axis=1)
        if songs.empty:
            return None

        songs_grouped_by_artist = (
            songs.groupby(ARTIST_ID_FIELD)
            .agg(
                {
                    SONG_TITLE_FIELD: "count",
                    LYRICS_COUNT_FIELD: "mean",
                    ALBUM_FIELD: "nunique",
                }
            )
            .reset_index()
        )

        artists = pd.DataFrame(self.artists_collection.find({}))
        artists_no_data = artists[artists.status == "failure"]
        artist_data = artists[artists.status.isin(["success", "pending"])]
        df = artist_data.merge(songs_grouped_by_artist, on=ARTIST_ID_FIELD, how="left")
        df = df.rename(
            columns={
                ARTIST_ID_FIELD: DOCUMENT_ID_FIELD,
                SONG_TITLE_FIELD: "song_count",
                LYRICS_COUNT_FIELD: "avg_lyrics",
                ALBUM_FIELD: "album_count",
            }
        )

        return df.to_dict(orient="records"), artists_no_data.to_dict(orient="records")

    def songs_data(self, artist_ids: list[str]) -> list[dict]:
        songs = self.songs_collection.find({ARTIST_ID_FIELD: {"$in": artist_ids}})
        return parse_mongo(list(songs))

    def album_lyrics_distribution(self, artist_ids: list[str]) -> list[dict]:
        result = self.songs_collection.find({ARTIST_ID_FIELD: {"$in": artist_ids}})
        songs = pd.DataFrame(result)
        songs[SONG_RELEASE_DATE_FIELD] = pd.to_datetime(songs[SONG_RELEASE_DATE_FIELD])
        album_grouped = songs.groupby(ALBUM_FIELD)
        agg_functions = {
            ARTIST_NAME_FIELD: "first",
            SONG_RELEASE_DATE_FIELD: "max",
            LYRICS_COUNT_FIELD: "mean",
            DISTINCT_COUNT_FIELD: "mean",
        }
        album_info = album_grouped.agg(agg_functions)
        album_info.reset_index(inplace=True)
        return album_info.to_dict(orient="records")


class AuthQueries:
    def __init__(self) -> None:
        self.users_collection = client.collection("users")

    def user_by_id(self, user_id: str) -> dict | None:
        user = self.users_collection.find_one({DOCUMENT_ID_FIELD: ObjectId(user_id), USER_IS_ACTIVE_FIELD: True})
        if user:
            return parse_mongo(user)
        return None

    def register_user_if_not_exists(self, username: str, password: str) -> bool:
        if self.users_collection.find_one({USERNAME_FIELD: username}):
            return False

        self.users_collection.insert_one(
            {
                USERNAME_FIELD: username,
                PASSWORD_FIELD: generate_password_hash(password + Config.PEPPER),
                USER_ROLE_FIELD: "user",
                USER_IS_ACTIVE_FIELD: True,
                USER_FETCHES_LEFT_FIELD: 5,
            }
        )

        return True

    def user_is_authorised(self, username: str, password: str) -> dict | None:
        user = self.users_collection.find_one({USERNAME_FIELD: username})

        if not user or not check_password_hash(user[PASSWORD_FIELD], password + Config.PEPPER):
            return None

        return parse_mongo(user)

    def user_is_admin(self, username: str):
        user = self.users_collection.find_one({USERNAME_FIELD: username, USER_ROLE_FIELD: "admin"})
        return parse_mongo(user)


class SearchQueries:
    def __init__(self):
        self.artists_collection = client.collection("artists")
        self.searches_collection = client.collection("searches")
        self.users_collection = client.collection("users")

    def artist_status(self, artist_id: str, artist_name: str) -> None | str:
        artist = self.artists_collection.find_one({ARTIST_ID_FIELD: artist_id})
        if artist is None:
            self.artists_collection.insert_one(
                {
                    ARTIST_ID_FIELD: artist_id,
                    ARTIST_NAME_FIELD: artist_name,
                    ARTIST_STATUS_FIELD: "pending",
                }
            )
            return None
        return artist[ARTIST_STATUS_FIELD]

    def artist_previously_searched(self, artist_name: str) -> dict | None:
        return self.searches_collection.find_one({"search_name": artist_name})

    def update_search_log(self, searched_artist: str, found_artists: list[dict]) -> None:
        self.searches_collection.insert_one({"search_name": searched_artist, "found_artists": found_artists})

    def decrease_fetch_count(self, user_id: str):
        self.users_collection.update_one(
            {DOCUMENT_ID_FIELD: ObjectId(user_id)},
            {"$inc": {USER_FETCHES_LEFT_FIELD: -1}},
        )

    def get_fetch_count(self, user_id: str):
        user = self.users_collection.find_one({DOCUMENT_ID_FIELD: ObjectId(user_id)}, {PASSWORD_FIELD: 0})
        return user[USER_FETCHES_LEFT_FIELD]


class TaskQueries:
    def __init__(self):
        self.songs_collection = client.collection("songs")
        self.artists_collection = client.collection("artists")

    def insert_many_songs_update_status(self, songs: list[dict], artist_id: str) -> dict:
        if not songs:
            self.artists_collection.update_one({ARTIST_ID_FIELD: artist_id}, {"$set": {ARTIST_STATUS_FIELD: "failure"}})
            return {
                ARTIST_ID_FIELD: artist_id,
                "total": 0,
                ARTIST_STATUS_FIELD: "failure",
            }

        self.songs_collection.insert_many(songs)
        self.artists_collection.update_one({ARTIST_ID_FIELD: artist_id}, {"$set": {ARTIST_STATUS_FIELD: "success"}})
        return {
            ARTIST_ID_FIELD: artist_id,
            "total": len(songs),
            ARTIST_STATUS_FIELD: "success",
        }

    def apply_song_filters(self, field, values_to_remove):
        result = self.songs_collection.delete_many({field: {"$in": values_to_remove}})
        return parse_mongo(result)


class AdminQueries:
    def __init__(self):
        self.users_collection = client.collection("users")

    def get_users(self):
        users = self.users_collection.find(
            {},
            {PASSWORD_FIELD: 0},
        )
        return parse_mongo(list(users))

    def get_user(self, user_id: str):
        user = self.users_collection.find_one(
            {DOCUMENT_ID_FIELD: ObjectId(user_id)},
            {PASSWORD_FIELD: 0},
        )
        return parse_mongo(user)

    def update_user(self, user_id: str, role: str, status: bool, fetches: int):
        response = self.users_collection.update_one(
            {DOCUMENT_ID_FIELD: ObjectId(user_id)},
            {
                "$set": {
                    USER_ROLE_FIELD: role,
                    USER_IS_ACTIVE_FIELD: status,
                    USER_FETCHES_LEFT_FIELD: fetches,
                }
            },
        )
        return parse_mongo(response)

    def create_admin(self):
        self.users_collection.delete_many({USERNAME_FIELD: "admin"})

        self.users_collection.insert_one(
            {
                USERNAME_FIELD: "admin",
                PASSWORD_FIELD: generate_password_hash(Config.ADMIN_PASSWORD + Config.PEPPER),
                USER_ROLE_FIELD: "admin",
                USER_IS_ACTIVE_FIELD: True,
                USER_FETCHES_LEFT_FIELD: 10,
            }
        )


class UserQueries:
    def __init__(self):
        self.users_collection = client.collection("users")

    def get_user(self, user_id: str):
        user = self.users_collection.find_one(
            {DOCUMENT_ID_FIELD: ObjectId(user_id)},
            {PASSWORD_FIELD: 0},
        )
        return parse_mongo(user)
