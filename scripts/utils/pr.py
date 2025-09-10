from __future__ import annotations

import datetime
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from github import Auth, Github

if TYPE_CHECKING:
    from github.PullRequest import PullRequest


def ident() -> None:
    subprocess.run(["/usr/bin/git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(
        ["/usr/bin/git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True
    )


def create_update_pr(commit_message: str, branch_prefix: str, title: str, body: str, path: str | Path) -> None:
    """
    Creates or updates a pull request with the given title and body.

    Parameters
    ----------
    commit_message (str): The commit message to use.
    branch_prefix (str): The prefix for the branch name.
    title (str): The title of the pull request.
    body (str): The body of the pull request.
    path (str | Path): The path or glob to the file to commit.
    """
    github = Github(os.environ["GITHUB_TOKEN"])
    repo = github.get_repo(os.environ["GITHUB_REPOSITORY"])
    base_branch = subprocess.run(
        ["/usr/bin/git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    ident()
    print(f"Creating/updating PR in {repo.full_name} on branch {base_branch} with prefix {branch_prefix}")

    prs = repo.get_pulls(state="open", sort="created", base=base_branch)
    pull_request: None | PullRequest = None
    for pr in prs:
        if pr.head.ref.startswith(branch_prefix):
            branch_name: str = pr.head.ref
            subprocess.run(
                ["/usr/bin/git", "fetch", "origin", branch_name],
                check=False,
            )
            subprocess.run(
                ["/usr/bin/git", "checkout", branch_name],
                check=False,
            )
            pull_request = pr
            break
    else:
        branch_name = f"{branch_prefix}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        subprocess.run(
            ["/usr/bin/git", "checkout", "-b", branch_name],
            check=False,
        )

    if not subprocess.run(["/usr/bin/git", "status", "--porcelain"], check=False, capture_output=True).stdout:
        print("No changes to commit.")
        return

    subprocess.run(
        ["/usr/bin/git", "add", str(path)],
        check=False,
    )
    subprocess.run(
        ["/usr/bin/git", "commit", "-m", title],
        check=False,
    )
    subprocess.run(
        ["/usr/bin/git", "push", "-u", "origin", branch_name],
        check=False,
    )

    if not pull_request:
        pull_request = repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base=base_branch,
        )
        print(f"Created new PR #{pull_request.number}: {pull_request.title}")


__all__ = ("create_update_pr",)
