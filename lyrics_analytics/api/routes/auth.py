import functools
import os

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

from lyrics_analytics.common.database.queries import AuthQueries

BASE = os.path.basename(__file__).split(".")[0]

bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")
auth_queries = AuthQueries()


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "GET":
        return render_template(f"{BASE}/register.html")

    username = request.form["username"]
    password = request.form["password"]

    if auth_queries.register_user_if_not_exists(username, password):
        return redirect(url_for(f"{BASE}.login"))

    flash(f"User {username} already exists", category="warning")
    return redirect(url_for(f"{BASE}.register"))


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return render_template(f"{BASE}/login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = auth_queries.user_is_authorised(username, password)

    if not user:
        flash(f"Incorrect username or password for {username}", category="danger")
        return render_template(f"{BASE}/login.html")

    session.clear()
    session["user_id"] = user["_id"]

    if user["role"] == "admin":
        return redirect(url_for("admin.user_control"))

    return redirect(url_for("search.index"))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        return None

    user = auth_queries.user_by_id(user_id)
    if user:
        g.user = user


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


def in_session(state) -> bool:
    user_in_obj = hasattr(state, "user")
    if not user_in_obj:
        return False
    if state.user is None:
        return False
    return True


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not in_session(g):
            return redirect(url_for(f"{BASE}.login"))

        return view(**kwargs)

    return wrapped_view


def admin_only(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not in_session(g):
            return redirect(url_for(f"{BASE}.logout"))

        if not auth_queries.user_is_admin(g.user["username"]):
            return redirect(url_for("search.index"))

        return view(**kwargs)

    return wrapped_view
