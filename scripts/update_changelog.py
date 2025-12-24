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
import pathlib
import re
import sys
from datetime import date as date_cls


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update CHANGELOG for a release.")
    parser.add_argument("--path", default="CHANGELOG.md", help="Path to CHANGELOG.md")
    parser.add_argument("--version", required=True, help="Version being released")
    parser.add_argument("--previous-tag", required=True, help="Previous git tag")
    parser.add_argument(
        "--previous-final-tag",
        required=False,
        help="Previous final (non-rc) tag; used for final release compare links",
    )
    parser.add_argument(
        "--branch", required=True, help="Branch name for Unreleased copy"
    )
    parser.add_argument("--repository", required=True, help="owner/repo for links")
    parser.add_argument(
        "--date", default=None, help="Release date (YYYY-MM-DD); defaults to today"
    )
    return parser.parse_args()


def find_unreleased_section(text: str) -> tuple[int, int]:
    match = re.search(r"^## \[Unreleased\]\s*", text, flags=re.M)
    if not match:
        sys.exit("Missing '## [Unreleased]' heading in changelog.")
    start = match.start()
    after = match.end()
    next_header = re.search(r"^## \[", text[after:], flags=re.M)
    end = after + next_header.start() if next_header else len(text)
    return start, end


def build_unreleased_block(branch: str) -> str:
    lines = [
        "## [Unreleased]",
        "",
        f"These changes are available on the `{branch}` branch, but have not yet been released.",
        "",
        "### Added",
        "",
        "### Changed",
        "",
        "### Fixed",
        "",
        "### Deprecated",
        "",
        "### Removed",
        "",
    ]
    return "\n".join(lines)


CATEGORY_ORDER = ["Added", "Changed", "Fixed", "Deprecated", "Removed"]


def parse_categories(section_body: str) -> dict[str, list[str]]:
    """Parse a section body into category -> list of lines (without the heading)."""
    categories: dict[str, list[str]] = {name: [] for name in CATEGORY_ORDER}
    current: str | None = None

    for line in section_body.splitlines():
        heading_match = re.match(r"^###\s+(.+)$", line)
        if heading_match:
            title = heading_match.group(1).strip()
            current = title if title in categories else None
            continue
        if current:
            categories[current].append(line)
    return categories


def merge_categories(dest: dict[str, list[str]], src: dict[str, list[str]]) -> None:
    for key in CATEGORY_ORDER:
        if src.get(key):
            dest[key].extend(src[key])


def _normalize_lines(lines: list[str]) -> list[str]:
    """Keep only non-empty lines to avoid gaps inside category lists."""
    return [line for line in lines if line.strip()]


def render_release_body(categories: dict[str, list[str]]) -> str:
    parts: list[str] = []
    for name in CATEGORY_ORDER:
        body = _normalize_lines(categories[name])
        if not any(line.strip() for line in body):
            continue
        parts.append(f"### {name}")
        if body:
            parts.append("")
        parts.extend(body)
        parts.append("")
    return "\n".join(parts).rstrip("\n")


def update_links(
    text: str,
    version: str,
    previous_tag: str,
    repository: str,
    previous_final_tag: str | None,
) -> str:
    unreleased_link = f"[unreleased]: https://github.com/{repository}/compare/v{version}...HEAD"

    base_tag = previous_tag
    if "rc" not in version:
        base_tag = previous_final_tag or previous_tag

    release_link = f"[{version}]: https://github.com/{repository}/compare/{base_tag}...v{version}"

    updated = re.sub(r"^\[unreleased\]: .*", unreleased_link, text, flags=re.M)

    if re.search(rf"^\[{re.escape(version)}\]: ", updated, flags=re.M):
        updated = re.sub(
            rf"^\[{re.escape(version)}\]: .*", release_link, updated, flags=re.M
        )
    else:

        def insert_after_unreleased(match: re.Match) -> str:
            return match.group(0) + "\n" + release_link

        new_updated = re.sub(
            r"^\[unreleased\]: .*$",
            insert_after_unreleased,
            updated,
            flags=re.M,
            count=1,
        )
        if new_updated == updated:
            new_updated = updated.rstrip("\n") + "\n" + release_link + "\n"
        updated = new_updated

    return updated


def main() -> None:
    args = parse_args()
    changelog_path = pathlib.Path(args.path)
    if not changelog_path.exists():
        sys.exit(f"Changelog not found at {changelog_path}")

    release_date = args.date or date_cls.today().isoformat()

    text = changelog_path.read_text()
    start, end = find_unreleased_section(text)
    unreleased_body = text[text.find("\n", start, end) + 1 : end].rstrip("\n")

    rest = text[end:]

    rc_bodies: list[str] = []
    if "rc" not in args.version:
        section_pattern = re.compile(r"^## \[(?P<title>[^\]]+)\][^\n]*\n", re.M)
        matches = list(section_pattern.finditer(rest))
        base_prefix = f"{args.version}rc"

        collecting = False
        for idx, match in enumerate(matches):
            title = match.group("title")
            is_rc = title.startswith(base_prefix)

            if is_rc and not collecting:
                collecting = True
            if collecting and not is_rc:
                break
            if not collecting:
                continue

            body_start = match.end()
            body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(rest)
            rc_bodies.append(rest[body_start:body_end].rstrip("\n"))

    new_unreleased = build_unreleased_block(args.branch)

    aggregated = parse_categories(unreleased_body)
    for body in rc_bodies:
        merge_categories(aggregated, parse_categories(body))

    release_body = render_release_body(aggregated)

    release_section = f"## [{args.version}] - {release_date}\n{release_body}\n"

    updated = text[:start] + new_unreleased + "\n" + release_section + rest
    updated = update_links(
        updated,
        args.version,
        args.previous_tag,
        args.repository,
        args.previous_final_tag,
    )

    if not updated.endswith("\n"):
        updated += "\n"

    changelog_path.write_text(updated)


if __name__ == "__main__":
    main()
