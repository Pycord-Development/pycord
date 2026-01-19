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


def build_message(
    version: str, previous_tag: str, previous_final_tag: str, repo: str
) -> str:
    major_minor = version.split(".")[:2]
    major_minor_str = ".".join(major_minor)
    docs_url = f"https://docs.pycord.dev/en/v{version}/changelog.html"
    base_compare = previous_tag
    if "rc" not in version:
        base_compare = previous_final_tag or previous_tag
    compare_url = f"https://github.com/{repo}/compare/{base_compare}...v{version}"
    release_url = f"https://github.com/{repo}/releases/tag/v{version}"
    pypi_url = f"https://pypi.org/project/py-cord/{version}/"

    if "rc" in version:
        heading = f"## <:pycord:1063211537008955495> Pycord v{version} Release Candidate ({major_minor_str}) is available!\n\n"
        audience = "@here\n\n"
        preface = (
            "This is a pre-release (release candidate) for testing and feedback.\n\n"
        )
        docs_line = f"You can view the changelog here: <{docs_url}>\n\n"
        links = f"Check out the [GitHub changelog](<{compare_url}>), [GitHub release page](<{release_url}>), and [PyPI release page](<{pypi_url}>).\n\n"
        install = f"You can install this version by running the following command:\n```sh\npip install -U py-cord=={version}\n```\n\n"
        close = "Please try it out and let us know your feedback or any issues!"
    else:
        heading = f"## <:pycord:1063211537008955495> Pycord v{version} is out!\n\n"
        audience = "@everyone\n\n"
        preface = ""
        docs_line = f"You can view the changelog here: <{docs_url}>\n\n"
        links = f"Feel free to take a look at the [GitHub changelog](<{compare_url}>), [GitHub release page](<{release_url}>) and the [PyPI release page](<{pypi_url}>).\n\n"
        install = f"You can install this version by running the following command:\n```sh\npip install -U py-cord=={version}\n```"
        close = ""

    return heading + audience + preface + docs_line + links + install + close


def send_webhook(webhook_url: str, content: str) -> None:
    payload = {"content": content, "allowed_mentions": {"parse": ["everyone", "roles"]}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "pycord-release-bot/1.0 (+https://github.com/Pycord-Development/pycord)",
            "Accept": "*/*",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:  # nosec - not applicable
        if resp.status >= 300:
            raise RuntimeError(f"Webhook post failed with status {resp.status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Notify Discord about a release.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print payload instead of sending"
    )
    parser.add_argument(
        "--webhook-url", help="Webhook URL (overrides DISCORD_WEBHOOK_URL)"
    )
    args = parser.parse_args()

    version = os.environ.get("VERSION")
    previous_tag = os.environ.get("PREVIOUS_TAG")
    previous_final_tag = os.environ.get("PREVIOUS_FINAL_TAG")
    webhook_url = args.webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
    repo = os.environ.get("REPOSITORY")

    if not all([version, previous_tag, repo]) or (not args.dry_run and not webhook_url):
        sys.exit("Missing required environment variables.")

    message = build_message(
        version, previous_tag, previous_final_tag or previous_tag, repo
    )

    if args.dry_run:
        payload = {
            "content": message,
            "allowed_mentions": {"parse": ["everyone", "roles"]},
        }
        print(json.dumps(payload, indent=2))
        return

    send_webhook(webhook_url, message)


if __name__ == "__main__":
    main()
