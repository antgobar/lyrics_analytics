import os
import functools

from bson.objectid import ObjectId
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from lyrics_analytics.config import Config
from lyrics_analytics.database.db import mongo_collection, parse_mongo


BASE = os.path.basename(__file__).split(".")[0]

bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "GET":
        return render_template(f"{BASE}/register.html")

    username = request.form["username"]
    password = request.form["password"]
    user_collection = mongo_collection("users")

    if user_collection.find_one({"username": username}):
        flash(f"User {username} already exists")
        return redirect(url_for(f"{BASE}.register"))

    user_collection.insert_one(
        {
            "username": username,
            "password": generate_password_hash(password + Config.PEPPER),
        }
    )

    return redirect(url_for("auth.login"))


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return render_template(f"{BASE}/login.html")

    username = request.form["username"]
    password = request.form["password"]
    user_collection = mongo_collection("users")

    user = user_collection.find_one({"username": username})

    if not user or not check_password_hash(user["password"], password + Config.PEPPER):
        flash(f"Incorrect username or password for {username}")
        return render_template(f"{BASE}/login.html")

    parsed_user = parse_mongo(user)

    session.clear()
    session["user_id"] = parsed_user["_id"]
    return redirect(url_for("index"))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    user_collection = mongo_collection("users")
    if user_id is None:
        g.user = None
    else:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        g.user = parse_mongo(user)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for(f"{BASE}.login"))

        return view(**kwargs)

    return wrapped_view
