import sys

from flask import Flask, render_template

from src.lyrics_api.dummy_api import get_artist_data_dummy


artist = sys.argv[1]
print("Searching for lyrics by:", artist)
works = get_artist_data_dummy(artist)
print(len(works))



app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'


