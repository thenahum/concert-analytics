import logging
import sys

import pandas as pd
import pytest

from setkit import notebook


def test_find_project_root_walks_up_to_marker(tmp_path):
    root = tmp_path / "repo"
    nested = root / "projects" / "0001"
    nested.mkdir(parents=True)
    (root / "AGENTS.md").write_text("# agents\n")

    assert notebook.find_project_root(start=nested) == root


def test_find_project_root_raises_when_no_marker(tmp_path):
    with pytest.raises(FileNotFoundError):
        notebook.find_project_root(start=tmp_path)


def test_add_project_root_adds_root_once(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    original_path = list(sys.path)

    try:
        notebook.add_project_root(project_root=root)
        notebook.add_project_root(project_root=root)

        assert sys.path.count(str(root.resolve())) == 1
    finally:
        sys.path[:] = original_path


def test_configure_pandas_sets_display_options():
    original_max_columns = pd.get_option("display.max_columns")
    original_max_rows = pd.get_option("display.max_rows")

    try:
        notebook.configure_pandas(max_columns=12, max_rows=34)

        assert pd.get_option("display.max_columns") == 12
        assert pd.get_option("display.max_rows") == 34
    finally:
        pd.set_option("display.max_columns", original_max_columns)
        pd.set_option("display.max_rows", original_max_rows)


def test_setup_returns_context_and_does_not_import_database_helpers(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    original_path = list(sys.path)
    original_max_columns = pd.get_option("display.max_columns")
    original_loadin_postgres = sys.modules.pop("loadin.postgres", None)

    try:
        context = notebook.setup(
            project_name="Project",
            project_root=root,
            log_level=logging.WARNING,
            max_columns=99,
        )

        assert context.project_root == root.resolve()
        assert context.project_name == "Project"
        assert sys.path[0] == str(root.resolve())
        assert pd.get_option("display.max_columns") == 99
        assert "loadin.postgres" not in sys.modules
    finally:
        if original_loadin_postgres is not None:
            sys.modules["loadin.postgres"] = original_loadin_postgres
        sys.path[:] = original_path
        pd.set_option("display.max_columns", original_max_columns)
