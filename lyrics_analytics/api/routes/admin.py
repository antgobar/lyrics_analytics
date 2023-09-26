import os

from flask import Blueprint, redirect, render_template, request, url_for

from lyrics_analytics.api.routes.auth import admin_only
from lyrics_analytics.database.queries import AdminQueries

BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
admin_queries = AdminQueries()
ROLES = ["admin", "user", "other"]


@bp.route("/users")
@admin_only
def user_control():
    users = admin_queries.get_users()
    return render_template(f"{BASE}/users.html", users=users)


@bp.route("user/<user_id>", methods=("GET", "POST"))
@admin_only
def edit_user(user_id: str):
    if request.method == "GET":
        user = admin_queries.get_user(user_id)
        return render_template(f"{BASE}/user.html", user=user, roles=ROLES)

    user_role = request.form["user-role"]
    is_active = request.form.get("user-active")

    admin_queries.update_user(user_id, user_role, bool(is_active))

    return redirect(url_for(f"{BASE}.user_control"))
