from unittest.mock import MagicMock, patch

import pytest

from lyrics_analytics.services.genius import GeniusService, SongData


@pytest.fixture
def ping_is_true():
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"meta": {"status": 200}}
    return mock_response 


@patch("lyrics_analytics.services.genius.requests")
class TestGeniusService:
    
    def test_contstructor(self, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance._base_url == "url"
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

        with pytest.raises(ConnectionError) as err:
            func()
        assert "Unable to connect" in str(err.value)

    @patch("lyrics_analytics.services.genius.GeniusService._search_artist")
    @pytest.mark.parametrize(("search_artist_return", "expected"), [
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
            ]
        ),
        (None, [])
    ])
    def test_find_artists(
        self, 
        mock_search_artist,
        mock_requests, 
        ping_is_true, 
        search_artist_return,
        expected
    ):
        mock_requests.get.return_value = ping_is_true
        mock_search_artist.return_value = search_artist_return
        
        test_instance = GeniusService("url", "apikey")

        assert test_instance.titles == []
        assert test_instance.find_artists("Artist_a") == expected
        mock_search_artist.assert_called_with("Artist_a")

    @patch("lyrics_analytics.services.genius.GeniusService._title_filter")
    @patch("lyrics_analytics.services.genius.GeniusService._get_artist")
    @patch("lyrics_analytics.services.genius.GeniusService._get_song_data")
    @patch("lyrics_analytics.services.genius.GeniusService._get_artist_song_page")
    def test_get_artist_songs(
        self, 
        mock_get_artist_song_page, 
        mock_get_song_data,
        mock_get_artist,
        mock_title_filter,
        mock_requests,
        ping_is_true,
        
    ):
        mock_requests.get.return_value = ping_is_true
        mock_get_artist_song_page.side_effect = [
            {
                "songs": [{"title": "some_title", "lyrics_state": "complete", "primary_artist": {"name": "artist A"}}],
                "next_page": 1
            },
            {
                "songs": [{"title": "some_title", "lyrics_state": "complete", "primary_artist": {"name": "artist A"}}],
                "next_page": None
            }
        ]
        mock_get_song_data.return_value = {"song": "data"}
        mock_get_artist.return_value = {"artist": {"name": "artist A"}}
        mock_title_filter.return_value = True
        
        test_instance = GeniusService("url", "apikey")
        
        actual_song_data_gen = test_instance.get_artist_songs(1)

        for song_data, expected in zip(actual_song_data_gen, [{"song": "data"}, {"song": "data"}]):
            assert song_data == expected
        mock_get_artist.assert_called_with(1)
        mock_title_filter.assert_called_with("some_title")
        mock_get_artist_song_page.assert_called_with(1, 2)
        mock_get_song_data.assert_called_with({"title": "some_title", "lyrics_state": "complete", "primary_artist": {"name": "artist A"}})

    @patch("lyrics_analytics.services.genius.GeniusService._parse_date")
    @patch("lyrics_analytics.services.scraper.ScraperService.get_lyrics")
    @patch("lyrics_analytics.services.genius.GeniusService._get_song")
    def test_get_song_data(self, mock_get_song, mock_scraper, mock_date, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        mock_get_song.return_value = {"song": {"album": {"name": "some album"}}}
        mock_scraper.return_value = ["some", "some", "lyrics"]
        mock_date.return_value = "some date"
        song_response = {
            "primary_artist": {"name": "some artist", "id": 2},
            "title": "some title",
            "url": "some url",
            "release_date_components": "some date",
            "id": 1
        }
        expected = SongData(**{
            "name": "some artist",
            "title": "some title",
            "album": "some album",
            "release_date": "some date",
            "genius_artist_id": 2,
            "genius_song_id": 1,
            "lyrics_count": 3,
            "distinct_count": 2,
        })
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance._get_song_data(song_response) == expected
        
    def test_title_filter(self, mock_requests, ping_is_true):
        mock_requests.get.return_value = ping_is_true
        
        test_instance = GeniusService("url", "apikey")
        
        assert test_instance._title_filter("title") is True

    @pytest.mark.parametrize(("album_data", "expected"), [
        (None, None),
        ({"name": "album_name"}, "album_name"),
        ({"other": "not album"}, None)
    ])
    def test_parse_album(self, mock_requests, ping_is_true, album_data, expected):
        mock_requests.get.return_value = ping_is_true
        test_instance = GeniusService("url", "apikey")

        assert test_instance._parse_album(album_data) == expected

    @pytest.mark.parametrize(("date_components", "expected"), [
        ("not_dict", "1-01-01"),
        ({}, "1-01-01"),
        ({"day": 2}, "1-01-02"),
        ({"month": 2, "day": 2}, "1-02-02"),
        ({"year": 2, "month": 2, "day": 2}, "2-02-02")
    ])
    def test_parse_date(self, mock_requests, ping_is_true, date_components, expected):
        mock_requests.get.return_value = ping_is_true
        test_instance = GeniusService("url", "apikey")

        assert test_instance._parse_date(date_components) == expected
