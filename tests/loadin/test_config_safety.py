from loadin.postgres import PostgresConfig, get_postgres_config
from loadin.setlistfm import SetlistFmConfig, get_setlistfm_config
from loadin.spotify import SpotifyConfig, get_spotify_config


def test_postgres_config_can_be_loaded_without_dotenv(monkeypatch):
    monkeypatch.setenv("PGUSER", "concert_user")
    monkeypatch.setenv("PGPASSWORD", "super-secret-password")
    monkeypatch.setenv("PGHOST", "localhost")
    monkeypatch.setenv("PGPORT", "5432")
    monkeypatch.setenv("PGDATABASE", "concerts")

    config = get_postgres_config(load_env=False)

    assert config.user == "concert_user"
    assert config.password == "super-secret-password"
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.database == "concerts"


def test_spotify_config_can_be_loaded_without_dotenv(monkeypatch):
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "spotify-client-id")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "spotify-secret")

    config = get_spotify_config(load_env=False)

    assert config.client_id == "spotify-client-id"
    assert config.client_secret == "spotify-secret"


def test_setlistfm_config_can_be_loaded_without_dotenv(monkeypatch):
    monkeypatch.setenv("SETLIST_FM_API_KEY", "setlist-secret")

    config = get_setlistfm_config(load_env=False)

    assert config.api_key == "setlist-secret"


def test_config_repr_does_not_expose_secrets():
    configs = [
        PostgresConfig(
            user="user",
            password="super-secret-password",
            host="localhost",
            port=5432,
            database="concerts",
        ),
        SpotifyConfig(client_id="client-id", client_secret="spotify-secret"),
        SetlistFmConfig(api_key="setlist-secret"),
    ]

    rendered = "\n".join(repr(config) for config in configs)

    assert "super-secret-password" not in rendered
    assert "spotify-secret" not in rendered
    assert "setlist-secret" not in rendered
