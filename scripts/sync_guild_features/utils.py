import requests
import subprocess
from pathlib import Path
from ruff.__main__ import (  # type: ignore[import-untyped]
    find_ruff_bin,
)

# https://gist.github.com/advaith1/a82065c4049345b38f526146d6ecab96
GUILD_FEATURES_GIST_URL = (
    "https://gist.githubusercontent.com/advaith1/a82065c4049345b38f526146d6ecab96/raw/guildfeatures.json"
)


def get_features_blob() -> list[str]:
    """
    Fetches the latest guild features from the Gist URL.

    Returns
    -------
        list[str]: A list of guild feature strings.
    """
    response = requests.get(GUILD_FEATURES_GIST_URL, timeout=10)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch guild features: {response.status_code}")

    return response.json()


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


__all__ = ("get_features_blob", "format_path", "lint_path", "GUILD_FEATURES_GIST_URL")
