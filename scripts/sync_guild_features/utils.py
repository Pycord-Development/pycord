import requests

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


__all__ = ("get_features_blob", "GUILD_FEATURES_GIST_URL")
