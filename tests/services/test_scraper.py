from unittest.mock import patch

import pytest

from lyrics_analytics.services.scraper import Scraper


@patch("lyrics_analytics.services.scraper.ScraperService.clean")
@patch("lyrics_analytics.services.scraper.ScraperService.scrape")
def test_scraper_get_lyrics(mock_scrape, mock_clean):
    mock_scrape.return_value = "raw lyrics"
    mock_clean.return_value = "clean lyrics"

    assert Scraper.get_lyrics("some_url") == "clean lyrics"
    mock_scrape.assert_called_with("some_url")
    mock_clean.assert_called_with("raw lyrics")


@patch("lyrics_analytics.services.scraper.BeautifulSoup")
@patch("lyrics_analytics.services.scraper.requests")
def test_scraper_scrape(mock_requests, mock_bs):
    mock_requests.get.return_value.content = b"content"

    Scraper.scrape("some_url")

    mock_bs.assert_called_with(b"content", "html.parser")


@pytest.mark.parametrize(
    ("lyric", "expected"),
    [
        ("has [square] brackets", "has brackets"),
        ("new\n\nlines", "new lines"),
        ("UPPER", "upper"),
        ("some.other,characters  here", "some other characters here"),
        ("foobar lyrics some lyric here", "some lyric here"),
        ("basic", "basic"),
    ],
)
def test_scraper_clean(lyric, expected):
    assert Scraper.clean(lyric) == expected
