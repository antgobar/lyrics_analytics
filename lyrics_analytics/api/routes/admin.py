import os

from flask import Blueprint
import pandas as pd

# from lyrics_analytics.api import db

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
