import pytest

from loadin.postgres.loader import _raw_table_name
from loadin.postgres.utils import sanitize_table_name
from loadin.setlistfm.client import SetlistFmConfig, _headers
from loadin.spotify.client import search_artist_uri


def test_sanitize_table_name_preserves_safe_schema_table_shape():
    assert sanitize_table_name("analytics_mart.mart all tracks!") == "analytics_mart.martalltracks"


def test_raw_table_name_rejects_schema_prefix():
    with pytest.raises(ValueError):
        _raw_table_name("raw.setlist_history")


def test_setlistfm_headers_accept_explicit_config():
    headers = _headers(SetlistFmConfig(api_key="test-key"))

    assert headers == {
        "x-api-key": "test-key",
        "Accept": "application/json",
    }


def test_spotify_search_accepts_fake_client():
    class FakeSpotifyClient:
        def search(self, q, type, limit):
            assert q == "artist:test artist"
            assert type == "artist"
            assert limit == 1
            return {"artists": {"items": [{"name": "Test Artist"}]}}

    assert search_artist_uri("test artist", client=FakeSpotifyClient()) == [{"name": "Test Artist"}]
