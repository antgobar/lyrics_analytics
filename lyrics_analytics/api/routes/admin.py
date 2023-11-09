import os
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from lyrics_analytics.api.routes.auth import admin_only
from lyrics_analytics.common.database.queries import AdminQueries


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
admin_queries = AdminQueries()
ROLES = ["admin", "user", "other"]


@bp.route("/")
@admin_only
def admin_dashboard():
    return {
        "message": "lyrics with 0 count deleted",
        "response": admin_queries.remove_songs_with_no_lyrics()
    }


@bp.route("/users")
@admin_only
def user_control():
    users = admin_queries.get_users()
    return render_template(f"{BASE}/users.html", users=users, roles=ROLES)


@bp.route("user/<user_id>", methods=("POST",))
@admin_only
def edit_user(user_id: str):
    user_role = request.form["user-role"]
    is_active = request.form[f"user-active-{user_id}"]
    fetches = request.form["fetches"]
    active_status = True if is_active == "is-active" else False
    admin_queries.update_user(user_id, user_role, active_status, int(fetches))
    return f"Updated at { datetime.today().strftime('%H:%M:%S')}"


@bp.route("artists/pending", methods=("GET",))
@admin_only
def get_pending_artists():
    pending_artists = admin_queries.get_pending_artists()
    return render_template(f"{BASE}/pending_artists.html", pending_artists=pending_artists)
