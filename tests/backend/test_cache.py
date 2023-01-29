from unittest.mock import patch

import pytest

from lyrics_analytics.backend.cache import RedisCache


class MockRedis:
    pass


@patch("lyrics_analytics.backend.cache.Redis")
class TestRedisCache:
    def test_constructor(self, mock_redis):
        mock_redis.return_value = MockRedis
        test_instance = RedisCache("hostname")

        assert test_instance._redis == mock_redis
