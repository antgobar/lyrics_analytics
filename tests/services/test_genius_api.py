from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException

from lyrics_analytics.services.genius_api import GeniusService


@pytest.fixture
def ping_is_true():
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"meta": {"status": 200}}
    return mock_response 


@patch("lyrics_analytics.services.genius_api.requests")
class TestGeniusService:
    
    def test_contstructor(self, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance.base_url == "url"
        assert test_instance.cache == {"titles": [], "artists_found": []}
        assert test_instance.ping() is True
        
    @pytest.mark.parametrize(("ok_status", "g_status"), [
        (True, 404), (False, 200), (False, 404)
    ])
    def test_ping_raises(self, mock_requests, ok_status, g_status):
        mock_response = MagicMock()
        mock_response.ok = ok_status
        mock_response.json.return_value = {"meta": {"status": g_status}}
        mock_requests.get.return_value = mock_response
        
        with pytest.raises(ConnectionError) as err:
            GeniusService("url", "apikey")
        assert "Unable to connect" in str(err)

    def test_handle_response_decorator(self, mock_requests, ping_is_true):
        class MockResponse:
            def __init__(self):
                self.ok = 200

            def json(self):
                return {"response": "data", "meta": {"status": 200}}

        mock_response = MockResponse()
        mock_requests.get.return_value = ping_is_true
        test_instance = GeniusService("url", "apikey")

        @test_instance.handle_response
        def func():
            return mock_response

        assert func() == "data"

    def test_handle_response_decorator_raises_error(self, mock_requests, ping_is_true):
        class MockResponse:
            def __init__(self):
                self.ok = 404

            def json(self):
                return {"response": "data", "meta": {"status": 404}}

        mock_response = MockResponse()
        mock_requests.get.return_value = ping_is_true
        test_instance = GeniusService("url", "apikey")

        @test_instance.handle_response
        def func():
            return mock_response

        with pytest.raises(RequestException):
            func()

    @patch("lyrics_analytics.services.genius_api.GeniusService.search_artist")
    @pytest.mark.parametrize(("search_artist_return", "expected_cache", "expected"), [
        (
            {
                "hits": [
                    {"result": {"primary_artist": {"name": "artist_A", "id": 1}}},
                    {"result": {"primary_artist": {"name": "artist_A", "id": 1}}},
                    {"result": {"primary_artist": {"name": "artist_B", "id": 2}}},
                    {"result": {"primary_artist": {"name": "artist_A_and_B", "id": 3}}}
                ]
            },
            [
                {"id": 1, "name": 'artist_A'},
                {"id": 3, "name": 'artist_A_and_B'}
            ],
            [
                {"id": 1, "name": 'artist_A'},
                {"id": 3, "name": 'artist_A_and_B'}
            ]
        ),
        (None, [], None)
    ])
    def test_find_artists(
        self, 
        mock_search_artist,
        mock_requests, 
        ping_is_true, 
        search_artist_return,
        expected_cache,
        expected
    ):
        mock_requests.get.return_value = ping_is_true
        mock_search_artist.return_value = search_artist_return
        
        test_instance = GeniusService("url", "apikey")

        assert test_instance.cache["artists_found"] == []
        assert test_instance.find_artists("Artist_a") == expected
        assert test_instance.cache["artists_found"] == expected_cache

    @patch("lyrics_analytics.services.genius_api.GeniusService.title_filter")
    @patch("lyrics_analytics.services.genius_api.GeniusService.get_song_data")
    @patch("lyrics_analytics.services.genius_api.GeniusService.get_artist_song_page")
    def test_get_artist_songs(
        self, 
        mock_get_artist_song_page, 
        mock_get_song_data,
        mock_title_filter,
        mock_requests,
        ping_is_true,
        
    ):
        mock_requests.get.return_value = ping_is_true
        mock_get_artist_song_page.side_effect = [
            {"songs": [{"title": "some_title", "lyrics_state": "complete"}], "next_page": 1},
            {"songs": [{"title": "some_title", "lyrics_state": "complete"}], "next_page": None}
        ]
        mock_get_song_data.return_value = {"song": "data"}
        mock_title_filter.return_value = True
        
        test_instance = GeniusService("url", "apikey")
        
        actual = test_instance.get_artist_songs(1)
        
        assert actual == [{"song": "data"}, {"song": "data"}]
        
    def test_get_song_data(self, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        song_response = {
            "primary_artist": {"name": "some artist"},
            "title": "some title",
            "url": "some url",
            "release_date_components": "some date"
        }
        expected = {
            "name": "some artist",
            "title": "some title", 
            "lyrics_url": "some url", 
            "date": "some date"
        }
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance.get_song_data(song_response) == expected
        
    def test_title_filter(self, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance.title_filter("title") == True