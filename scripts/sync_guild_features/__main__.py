import json
import os
import re
import sys
from pathlib import Path

from github import Auth, Github

from ..utils import create_update_pr, format_path, lint_path
from .utils import GUILD_FEATURES_GIST_URL, get_features_blob

CI = os.environ.get("CI", "false").lower() in ("true", "1", "yes")

GUILD_FEATURES_PATH = Path.cwd() / "discord" / "types" / "guild.py"
GUILD_FEATURES_VARIABLE_NAME = "GuildFeature"
GUILD_FEATURES_PATTERN = re.compile(rf"{GUILD_FEATURES_VARIABLE_NAME}\s*=\s*Literal\[(.*?)\]", re.DOTALL)


def main():
    with GUILD_FEATURES_PATH.open(encoding="utf-8") as file:
        content = file.read()

    features_blob = get_features_blob()
    features_blob.sort()
    features_blob_str = ", ".join(f'"{feature}"' for feature in features_blob)
    new_content = GUILD_FEATURES_PATTERN.sub(f"{GUILD_FEATURES_VARIABLE_NAME} = Literal[{features_blob_str}]", content)

    with GUILD_FEATURES_PATH.open("w", encoding="utf-8") as file:
        file.write(new_content)

    format_path(GUILD_FEATURES_PATH)
    lint_path(GUILD_FEATURES_PATH)
    with GUILD_FEATURES_PATH.open(encoding="utf-8") as file:
        updated_content = file.read()
    if updated_content == content:
        print("No changes made to guild features.")
        return
    if CI:
        create_update_pr(
            commit_message="chore: Update guild features",
            branch_prefix="sync-guild-features",
            title="Update guild features",
            body=f"This pull request automatically updates the guild features type, based on {GUILD_FEATURES_GIST_URL.split('/raw')[0]}. Please review the changes. and merge if everything looks good.",
            path=GUILD_FEATURES_PATH,
        )
    else:
        print("Not running in CI, skipping PR creation.")


if __name__ == "__main__":
    main()
