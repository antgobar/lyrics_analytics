import pytest

from lyrics_analytics.services.scraper import Scraper


@pytest.mark.parametrize(("lyric", "expected"), [
    ("has [square] brackets", "has brackets")
])
def test_scraper_clean(lyric, expected):
    assert Scraper.clean(lyric) == expected

