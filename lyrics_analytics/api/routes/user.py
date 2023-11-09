import os

from flask import Blueprint, session, render_template, url_for, flash

from lyrics_analytics.api.routes.auth import login_required
from lyrics_analytics.common.database.queries import UserQueries


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
user_queries = UserQueries()


@bp.get("/<username>")
@login_required
def dashboard(username: str):
    user = user_queries.get_user(session["user_id"])
    if user["username"] != username:
        flash(f"You're not {username}", "warning")
        return render_template(url_for("search.index"))

    return render_template(f"{BASE}/dashboard.html", user=parse_user(user))


def parse_user(user: dict) -> dict:
    return {
        "User ID": user["_id"],
        "Username": user["username"],
        "Fetches left": user["fetches"]
    }
