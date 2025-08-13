from unittest.mock import Mock, patch

from httpx import Response

from src.common.models import ArtistData
from src.worker.genius import Genius


def test__genius_service__init():
    base_url = "https://api.genius.com"
    access_token = "test_access_token"
    genius_service = Genius(base_url, access_token)

    assert genius_service.base_url == base_url
    assert genius_service.base_params == {"access_token": access_token}


@patch("worker.genius.httpx.get")
def test__genius_service__make_request__successful_request__returns_response(mock_get: Mock):
    base_url = "https://api.genius.com"
    access_token = "test_access_token"
    genius_service = Genius(base_url, access_token)
    mock_get.return_value = Response(
        status_code=200,
        json={"response": {"artist": "Justin Bieber"}, "meta": {"status": 200}},
    )

    response = genius_service.make_request("test_endpoint")

    assert response == {"artist": "Justin Bieber"}
    assert mock_get.was_called_once_with(url=f"{base_url}/test_endpoint", params={"access_token": access_token})


@patch("worker.genius.Genius.make_request")
def test__genius_service__search_artist__makes_correct_query(mock_make_request: Mock):
    base_url = "https://api.genius.com"
    access_token = "test_access_token"
    genius_service = Genius(base_url, access_token)
    mock_make_request.return_value = {
        "hits": [
            {"result": {"primary_artist": {"id": "123", "name": "Justin Bieber"}}},
            {"result": {"primary_artist": {"id": "456", "name": "Other Bieber"}}},
            {"result": {"primary_artist": {"id": "789", "name": "justin bieber strikes again"}}},
            {"result": {"other_artist": "james", "primary_artist": {"id": "101", "name": "Not Bieber"}}},
        ],
    }

    artists_found = genius_service.search_artists("Justin Bieber")

    assert mock_make_request.was_called_once_with("search", {"q": "Justin Bieber"})
    assert artists_found == [
        ArtistData(genius_artist_id="123", name="Justin Bieber"),
        ArtistData(genius_artist_id="789", name="justin bieber strikes again"),
    ]
