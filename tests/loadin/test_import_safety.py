import importlib
import sys
from pathlib import Path

import dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]


def _clear_loadin_modules():
    for module_name in list(sys.modules):
        if module_name == "loadin" or module_name.startswith("loadin."):
            del sys.modules[module_name]


def test_loadin_imports_do_not_load_dotenv(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("load_dotenv() should not be called during import")

    _clear_loadin_modules()
    monkeypatch.syspath_prepend(str(REPO_ROOT / "loadin"))
    monkeypatch.setattr(dotenv, "load_dotenv", fail_if_called)

    importlib.import_module("loadin")
    importlib.import_module("loadin.postgres")
    importlib.import_module("loadin.spotify")
    importlib.import_module("loadin.setlistfm")
