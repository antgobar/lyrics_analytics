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
        assert test_instance.titles == []
        assert test_instance.ping() is True
        
    @pytest.mark.parametrize(("ok_status", "g_status"), [
        (True, 404), (False, 200), (False, 404)
    ])
    def test_ping_raises(self, mock_requests, ok_status, g_status):
        mock_response = MagicMock()
        mock_response.ok = ok_status
        mock_response.json.return_value = {"meta": {"status": g_status}}
        mock_requests.get.return_value = mock_response
        
        with pytest.raises(ConnectionError):
            test_instance = GeniusService("url", "apikey")
            
    def test_handle_response(self, mock_requests, ping_is_true):
        class MockResponse:
            def __init__(self):
                self.ok = 200
                
            def json(self):
                return {"response": "data", "meta": {"status": 200}}
            
        mock_response = MockResponse()
        mock_requests.get.return_value = ping_is_true
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance.handle_response(mock_response) == "data"
        
    def test_handle_response_raises_error(self, mock_requests, ping_is_true):
        class MockResponse:
            def __init__(self):
                self.ok = 404
                
            def json(self):
                return {"response": "data", "meta": {"status": 404}}
            
        mock_response = MockResponse()
        mock_requests.get.return_value = ping_is_true
        test_instance = GeniusService("url", "apikey")
        
        with pytest.raises(RequestException):
            test_instance.handle_response(mock_response)

    @patch("lyrics_analytics.services.genius_api.GeniusService.handle_response")
    @pytest.mark.parametrize(("handle_return", "expected"), [
        (
            {
                
                "hits": [
                    {"result": {"primary_artist": {"name": "artist_A", "id": 1}}},
                    {"result": {"primary_artist": {"name": "artist_A", "id": 1}}},
                    {"result": {"primary_artist": {"name": "artist_A", "id": 2}}},
                    {"result": {"primary_artist": {"name": "artist_B", "id": 1}}},
                ]
            },
            1
        ),
        (None, None)
    ])
    def test_get_artist_id(
        self, 
        mock_handle_response, 
        mock_requests, 
        ping_is_true, 
        handle_return, 
        expected
    ):
        mock_requests.get.return_value = ping_is_true
        mock_handle_response.return_value = handle_return
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance.get_artist_id("Artist_a") == expected

    @patch("lyrics_analytics.services.genius_api.GeniusService.handle_response")
    @patch("lyrics_analytics.services.genius_api.GeniusService.title_filter")
    @patch("lyrics_analytics.services.genius_api.GeniusService.get_song_data")
    @patch("lyrics_analytics.services.genius_api.GeniusService.get_artist_song_page")
    def test_get_artist_songs(
        self, 
        mock_get_artist_song_page, 
        mock_get_song_data,
        mock_title_filter,
        mock_handle_response,
        mock_requests,
        ping_is_true,
        
    ):
        mock_requests.get.return_value = ping_is_true
        mock_handle_response.return_value = {"songs": [
                {"title": "some_title", "lyrics_state": "complete"}
            ], "next_page": 1
        }
        mock_get_song_data.return_value = {"song": "data"}
        mock_title_filter.return_value = True
        
        test_instance = GeniusService("url", "apikey")
        
        actual = test_instance.get_artist_songs(1, 2)
        
        assert actual == [{"song": "data"}, {"song": "data"}]
        
    def test_get_song_data(self, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        song_response = {
            "primary_artist": {"name": "some artist"},
            "title": "some title",
            "url": "some url",
            "release_date_components": "some date",
            "pyongs_count": "some count"
        }
        expected = {
            "artist_name": "some artist",
            "title": "some title", 
            "lyrics_url": "some url", 
            "date": "some date",
            "pyongs_count": "some count"
        }
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance.get_song_data(song_response) == expected
        
    def test_title_filter(self, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance.title_filter("title") == True