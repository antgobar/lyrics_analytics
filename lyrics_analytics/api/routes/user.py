import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from lyrics_analytics.api.routes.auth import login_required


BASE = os.path.basename(__file__).split(".")[0]
bp = Blueprint(BASE, __name__, url_prefix=f"/{BASE}")


@bp.get("/")
@login_required
def user_dashboard():
    ...
