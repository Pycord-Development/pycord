import subprocess
from pathlib import Path

from ruff.__main__ import (  # type: ignore[import-untyped]
    find_ruff_bin,
)


def format_path(path: Path) -> str:
    """
    Formats the given path with ruff.

    Parameters
    ----------
        path (Path): The path to format.
    """
    result = subprocess.run(
        [find_ruff_bin(), "format", str(path.absolute())],
        text=True,
        capture_output=True,
        check=True,
        cwd=Path.cwd(),
    )
    result.check_returncode()
    return result.stdout


def lint_path(path: Path) -> str:
    """
    Lints the given path with ruff.

    Parameters
    ----------
        path (Path): The path to format.
    """
    result = subprocess.run(
        [find_ruff_bin(), "check", "--fix", str(path.absolute())],
        text=True,
        capture_output=True,
        check=True,
        cwd=Path.cwd(),
    )
    result.check_returncode()
    return result.stdout


__all__ = ("format_path", "lint_path")
