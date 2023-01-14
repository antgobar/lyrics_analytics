from unittest.mock import patch

import pytest

from lyrics_analytics.api import create_app


class TestIndex:
    def test_index_get(self):
        app = create_app()
        with app.test_client() as c:
            response = c.get("/")
            assert response.status_code == 200
            assert b"""<label for="name">Artist Name</label>""" in response.data
            assert b"""<input name="name" id="name"required>""" in response.data

    @patch("lyrics_analytics.api.search.find_artists")
    def test_index_post(self, mock_find_artists):
        app = create_app()
        mock_find_artists.return_value = [
            {"id": 1, "name": "metallica"},
            {"id": 2, "name": "metallica 2"}
        ]
        with app.test_client() as c:
            response = c.post("/", data={"name": "metallica"})
            assert response.status_code == 200
            assert b"""<a class="action" href="/artist?artist_id=1"><h1>metallica</h1></a>""" in response.data
            assert b"""<a class="action" href="/artist?artist_id=2"><h1>metallica 2</h1></a>""" in response.data
