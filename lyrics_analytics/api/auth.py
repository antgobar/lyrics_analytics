import os

from flask import Blueprint

bp = Blueprint(os.path.basename(__file__).split(".")[0], __name__)
