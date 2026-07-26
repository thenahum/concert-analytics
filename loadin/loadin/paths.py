from __future__ import annotations
import os
from pathlib import Path

try:
    # lightweight, cross-platform user cache dir
    from platformdirs import user_cache_dir  # pip dep below
except Exception:
    user_cache_dir = None  # we’ll handle missing gracefully

def get_data_dir() -> Path:
    # 1) explicit env var wins
    env = os.getenv("CA_DATA_DIR") or os.getenv("LOADIN_DATA_DIR")
    if env:
        p = Path(env).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p

    # 2) repo /workspace fallback: walk up until we see a .git and use <repo>/data
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            p = parent / "data"
            p.mkdir(parents=True, exist_ok=True)
            return p

    # 3) user cache dir fallback (platform-correct)
    if user_cache_dir:
        p = Path(user_cache_dir(appname="concert-analytics", appauthor="RRG"))
    else:
        # no platformdirs? default to ~/.cache
        p = Path.home() / ".cache" / "concert-analytics"
    p.mkdir(parents=True, exist_ok=True)
    return p