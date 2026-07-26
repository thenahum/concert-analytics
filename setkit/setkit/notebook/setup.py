"""General notebook setup helpers."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import sys
from typing import Iterable

import pandas as pd


DEFAULT_MARKERS = ("AGENTS.md", "README.md", ".git")


@dataclass(frozen=True)
class NotebookContext:
    """Basic context returned by notebook setup."""

    project_root: Path
    project_name: str | None = None


def find_project_root(
    start: str | Path | None = None,
    markers: Iterable[str] = DEFAULT_MARKERS,
) -> Path:
    """Find the repository root by walking upward from ``start``."""
    current = Path(start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    marker_names = tuple(markers)
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in marker_names):
            return candidate

    raise FileNotFoundError(f"Could not find a project root from {current}")


def add_project_root(
    project_root: str | Path | None = None,
    start: str | Path | None = None,
    prepend: bool = True,
) -> Path:
    """Add the project root to ``sys.path`` and return it."""
    root = Path(project_root).resolve() if project_root is not None else find_project_root(start=start)
    root_string = str(root)

    if root_string not in sys.path:
        if prepend:
            sys.path.insert(0, root_string)
        else:
            sys.path.append(root_string)

    return root


def configure_logging(level: int | str = logging.INFO, force: bool = False) -> None:
    """Configure notebook logging."""
    logging.basicConfig(level=level, force=force)


def configure_pandas(max_columns: int | None = None, max_rows: int | None | object = pd.NA) -> None:
    """Apply common pandas display options for notebooks."""
    pd.set_option("display.max_columns", max_columns)
    if max_rows is not pd.NA:
        pd.set_option("display.max_rows", max_rows)


def setup(
    project_name: str | None = None,
    project_root: str | Path | None = None,
    start: str | Path | None = None,
    log_level: int | str = logging.INFO,
    max_columns: int | None = None,
    max_rows: int | None | object = pd.NA,
) -> NotebookContext:
    """Run standard notebook setup and return context.

    This helper intentionally does not import database helpers. Analysis notebooks
    should import ``loadin.postgres`` explicitly when they need warehouse access.
    """
    root = add_project_root(project_root=project_root, start=start)
    configure_logging(log_level)
    configure_pandas(max_columns=max_columns, max_rows=max_rows)
    return NotebookContext(project_root=root, project_name=project_name)
