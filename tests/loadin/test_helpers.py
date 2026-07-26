import pytest

from loadin.postgres.loader import _raw_table_name
from loadin.postgres.utils import sanitize_table_name
from loadin.setlistfm.client import SetlistFmConfig, _headers, search_artist
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


def test_setlistfm_search_accepts_page_and_sort(monkeypatch):
    class FakeResponse:
        status_code = 200
        url = "https://example.test/search/artists"

        def raise_for_status(self):
            return None

        def json(self):
            return {"artist": [{"name": "Test Artist"}], "page": 2}

    def fake_get(url, headers, params):
        assert url.endswith("/search/artists")
        assert headers["x-api-key"] == "test-key"
        assert params == {
            "artistName": "test artist",
            "p": 2,
            "sort": "relevance",
        }
        return FakeResponse()

    monkeypatch.setattr("loadin.setlistfm.client.requests.get", fake_get)

    result = search_artist(
        "test artist",
        config=SetlistFmConfig(api_key="test-key"),
        page=2,
        sort="relevance",
    )

    assert result == {"artist": [{"name": "Test Artist"}], "page": 2}


def test_spotify_search_accepts_fake_client():
    class FakeSpotifyClient:
        def search(self, q, type, limit):
            assert q == "artist:test artist"
            assert type == "artist"
            assert limit == 1
            return {"artists": {"items": [{"name": "Test Artist"}]}}

    assert search_artist_uri("test artist", client=FakeSpotifyClient()) == [{"name": "Test Artist"}]
