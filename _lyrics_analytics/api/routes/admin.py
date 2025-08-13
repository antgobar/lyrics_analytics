import os

from flask import Blueprint, redirect, render_template, request, url_for

from _lyrics_analytics.api.routes.auth import admin_only
from _lyrics_analytics.database.queries import AdminQueries

BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
admin_queries = AdminQueries()
ROLES = ["admin", "user", "other"]


@bp.route("/users")
@admin_only
def user_control():
    users = admin_queries.get_users()
    return render_template(f"{BASE}/users.html", users=users, roles=ROLES)


@bp.route("user/<user_id>", methods=("GET", "POST"))
@admin_only
def edit_user(user_id: str):
    if request.method == "GET":
        user = admin_queries.get_user(user_id)
        return render_template(f"{BASE}/user.html", user=user, roles=ROLES)

    user_role = request.form["user-role"]
    is_active = request.form["user-active"]
    fetches = request.form["fetches"]

    admin_queries.update_user(user_id, user_role, bool(is_active), int(fetches))

    return redirect(url_for(f"{BASE}.user_control"))


def transfer_between_deployments():
    import time

    from pymongo import MongoClient

    from _lyrics_analytics.config import Config

    db_name = "LyricStats"

    local_client = MongoClient(Config.MONGO_URI)
    local_db = local_client[db_name]

    local_data = {}

    for collection_name in local_db.list_collection_names():
        source_collection = local_db[collection_name]
        docs = source_collection.find({})
        local_data[collection_name] = list(docs)

    remote_client = MongoClient(Config.MONGO_URI_PROD)
    remote_db = remote_client[db_name]

    for collection, docs in local_data.items():
        print(collection)
        time.sleep(5)
        remote_collection = remote_db[collection]
        remote_collection.insert_many(docs)
