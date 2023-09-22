import os

from flask import Blueprint, redirect, render_template, request, url_for

from lyrics_analytics.api.routes.auth import login_required, admin_only
from lyrics_analytics.database.queries import AdminQueries

BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
admin_queries = AdminQueries()


@bp.route("/users")
@admin_only
def user_control():
    users = admin_queries.get_users()
    return render_template(f"{BASE}/users.html", users=users)


@bp.route("users/<user_id>")
@admin_only
def edit_user(user_id: str):
    user = admin_queries.get_user(user_id)
    return render_template(f"{BASE}/user.html", user=user)
