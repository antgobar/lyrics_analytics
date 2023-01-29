from unittest.mock import patch

import pytest

from lyrics_analytics.api import create_app


@pytest.fixture()
def app():
    with patch("lyrics_analytics.backend.task.Task") as mock_task:
        app = create_app()
        app.config.update({
            "TESTING": True,
        })
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"""<label for="name">Artist Name</label>""" in response.data
    assert b"""<input name="name" id="name"required>""" in response.data


@pytest.mark.parametrize("data", [
    "metallica", ""
])
def test_index_post(client, data):
    response = client.post("/", data={"name": data})
    assert response.status_code == 302


@patch("lyrics_analytics.api.search.genius_service.find_artists")
@pytest.mark.parametrize(("artist", "find_artist_return", "expected"), [
    (
        "metallica",
        [{"id": 1, "name": "metallica"}, {"id": 2, "name": "metallica 2"}],
        [
            b"""<a class="action" href="/artist?id=1"><h1>metallica</h1></a>""",
            b"""<a class="action" href="/artist?id=2"><h1>metallica 2</h1></a>"""
        ]
    ),
    (
        None,
        [],
        [b"""<label for="name">Artist Name</label>"""]
    )
])
def test_artists(mock_find_artists, client, artist, find_artist_return, expected):
    mock_find_artists.return_value = find_artist_return
    response = client.get(f"/artists?name={artist}", follow_redirects=True)
    assert response.status_code == 200
    for html in expected:
        assert html in response.data

    if artist is not None:
        mock_find_artists.assert_called_with(artist)
