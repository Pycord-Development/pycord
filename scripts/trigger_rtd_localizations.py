"""
The MIT License (MIT)

Copyright (c) 2025 Lala Sabathil <lala@pycord.dev> & Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def trigger_build(project: str, version: str, token: str) -> None:
    url = (
        f"https://readthedocs.org/api/v3/projects/{project}/versions/{version}/builds/"
    )
    data = json.dumps({}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp: # nosec - not applicable
        if resp.status >= 300:
            raise RuntimeError(
                f"Build trigger failed for {project}:{version} with status {resp.status}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trigger Read the Docs builds for localization projects."
    )
    parser.add_argument(
        "--project",
        action="append",
        required=True,
        help="Localization project slug. Can be repeated.",
    )
    parser.add_argument(
        "--version", default="master", help="Version to build (default: master)."
    )
    parser.add_argument(
        "--token", help="Read the Docs token (overrides READTHEDOCS_TOKEN env)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned builds instead of sending.",
    )
    args = parser.parse_args()

    token = args.token or os.environ.get("READTHEDOCS_TOKEN")
    if not token:
        sys.exit("Missing Read the Docs token.")

    if args.dry_run:
        payload = {"projects": args.project, "version": args.version}
        print(json.dumps(payload, indent=2))
        return

    failures = []
    for project in args.project:
        try:
            trigger_build(project, args.version, token)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
            failures.append((project, str(exc)))

    if failures:
        details = "; ".join([f"{proj}: {err}" for proj, err in failures])
        sys.exit(f"One or more builds failed: {details}")


if __name__ == "__main__":
    main()
