from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint("demo", __name__, url_prefix="/demo")


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("demo/index.html")

    name = request.form["artist-name"]

    flash(f"Searching {name}")

    found = [
        {"name": name, "id": 1},
        {"name": "Metallica", "id": 2},
        {"name": "Taylor Swift", "id": 3}
    ]

    return render_template("demo/artists-found.html", artists=found)

