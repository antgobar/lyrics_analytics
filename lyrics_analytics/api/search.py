from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint("search", __name__)


@bp.route("/search", methods=("GET", "POST"))
def search():
    if request.method == "GET":
        return render_template("search/index.html")

