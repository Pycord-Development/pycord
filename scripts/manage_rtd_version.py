import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request


API_BASE = "https://readthedocs.org/api/v3"


def sync_versions(project: str, token: str) -> None:
    url = f"{API_BASE}/projects/{project}/sync-versions/"
    req = urllib.request.Request(
        url,
        data=json.dumps({}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        if resp.status >= 300:
            raise RuntimeError(f"Sync versions failed for {project} with status {resp.status}")


def activate_version(project: str, docs_version: str, hidden: bool, token: str) -> None:
    url = f"{API_BASE}/projects/{project}/versions/{docs_version}/"
    payload = {"active": True, "hidden": hidden}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        if resp.status >= 300:
            raise RuntimeError(
                f"Activating version {docs_version} for {project} failed with status {resp.status}"
            )


def determine_docs_version(version: str) -> tuple[str, bool]:
    match = re.match(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>rc\d+)?$", version)
    if not match:
        raise ValueError(f"Version '{version}' is not in the expected format")
    major = match.group("major")
    minor = match.group("minor")
    suffix = match.group("suffix") or ""
    hidden = bool(suffix)
    if hidden:
        docs_version = f"v{major}.{minor}.x"
    else:
        docs_version = f"v{version}"
    return docs_version, hidden


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Read the Docs version activation.")
    parser.add_argument("--project", default="pycord", help="RTD project slug (default: pycord)")
    parser.add_argument("--version", required=True, help="Release version (e.g., 2.6.0 or 2.6.0rc1)")
    parser.add_argument("--token", help="RTD token (overrides READTHEDOCS_TOKEN env)")
    parser.add_argument("--sync", action="store_true", help="Sync versions before activating")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without calling RTD")
    args = parser.parse_args()

    token = (args.token or os.environ.get("READTHEDOCS_TOKEN"))
    if not token:
        sys.exit("Missing Read the Docs token.")

    try:
        docs_version, hidden = determine_docs_version(args.version)
    except ValueError as exc:
        sys.exit(str(exc))

    if args.dry_run:
        plan = {
            "project": args.project,
            "version": args.version,
            "docs_version": docs_version,
            "hidden": hidden,
            "sync": args.sync,
        }
        print(json.dumps(plan, indent=2))
        return

    try:
        if args.sync:
            sync_versions(args.project, token)
        activate_version(args.project, docs_version, hidden, token)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()
