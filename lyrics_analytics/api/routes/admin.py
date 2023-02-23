import os

from flask import Blueprint

from lyrics_analytics.api import db
from lyrics_analytics.api.models import User, LyricsStats

BASE = os.path.basename(__file__).split(".")[0]

bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/")
def index():
    return {"status": "admin base"}


@bp.route("/create")
def create():
    db.create_all()
    return {"status": "db created"}


@bp.route("/delete")
def delete():
    db.drop_all()
    return {"status": "db deleted"}


@bp.route("/add_user/<username>")
def add_user(username):
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return [{"name": user.username} for user in User.query.all()]


@bp.route("/users")
def users():
    return [{"name": user.username} for user in User.query.all()]


@bp.route("/stats")
def stats():
    return [{"name": stat.name, "count": stat.count} for stat in LyricsStats.query.all()]
