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

from lyrics_analytics.database.queries import (
    register_user_if_not_exists,
    user_by_id,
    user_is_authorised,
)

BASE = os.path.basename(__file__).split(".")[0]

bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "GET":
        return render_template(f"{BASE}/register.html")

    username = request.form["username"]
    password = request.form["password"]

    if register_user_if_not_exists(username, password):
        return redirect(url_for("auth.login"))

    flash(f"User {username} already exists")
    return redirect(url_for(f"{BASE}.register"))


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return render_template(f"{BASE}/login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = user_is_authorised(username, password)

    if user:
        session.clear()
        session["user_id"] = user["_id"]
        return redirect(url_for("index"))

    flash(f"Incorrect username or password for {username}")
    return render_template(f"{BASE}/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        return None

    user = user_by_id(user_id)
    if user:
        g.user = user_by_id(user_id)


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
