from unittest.mock import patch
gitimport json

import pytest

from lyrics_analytics.backend.cache import RedisCache


class MockRedis:
    cache = {}

    def get(self, key):
        return self.cache[key]

    def set(self, key, value):
        self.cache[key] = value


@patch("lyrics_analytics.backend.cache.Redis")
class TestRedisCache:
    def test_constructor(self, mock_redis):
        mock_redis.return_value = MockRedis
        test_instance = RedisCache("hostname")

        mock_redis.assert_called_with("hostname")

    def test_create_store(self, mock_redis):
        pass
