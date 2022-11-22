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
