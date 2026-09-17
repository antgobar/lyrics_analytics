from unittest.mock import Mock, patch

import pytest

from services.scraper.genius import GeniusScraper


@patch("services.scraper.genius.BeautifulSoup")
@patch("services.scraper.genius.httpx.get")
def test__scraper__scrape(mock_get: Mock, mock_bs: Mock):
    mock_get.return_value.content = b"content"

    GeniusScraper.get_lyrics("some_url")

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
    assert GeniusScraper.clean(lyric) == expected
