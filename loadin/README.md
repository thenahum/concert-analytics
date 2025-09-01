# loadin

**Concert Analytics Ingestion SDK**

`loadin` is the ingestion layer for the Concert Analytics stack. It wraps our main data sources — **Postgres**, **Spotify**, and **setlist.fm** — into a single package so projects can fetch raw data, cache API responses, and load tables with minimal boilerplate.

## ✨ Features

- **Postgres helpers** (`loadin.postgres`)
  - `get_engine()` — one-liner SQLAlchemy engine from env vars
  - `run_query()` / `fetch_table()` — DataFrame helpers
  - `load_dataframe()` — create/append/upsert into `raw.<table>`
- **Spotify client** (`loadin.spotify`)
  - Artist/album/track metadata via Spotipy (Client Credentials)
  - Built-in JSON caching on disk
  - (e.g.) `albums_dataframe()`, `tracks_metadata_dataframe()`
- **setlist.fm client** (`loadin.setlistfm`)
  - Fetch artist setlists from the setlist.fm API
  - `setlist_dataframe(artist_name_or_mbid)` and `search_artist()`
- **Shared cache directory**
  - Defaults to `<repo_root>/data` (if inside a Git repo)
  - Else uses a platform-correct user cache (via `platformdirs`)
  - Override with `CA_DATA_DIR=/path/to/cache`

---

## 📦 Installation

From the **repo root**:

```bash
pip install -e ./loadin