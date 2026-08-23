"""
The MIT License (MIT)

Copyright (c) 2026 Pycord Development

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

Convert Sigstore bundles produced by GitHub's actions/attest into PEP 740
attestation files that `uv publish` discovers and uploads to PyPI.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from pypi_attestations import Attestation
from sigstore.models import Bundle


def read_bundles(bundle_path: Path) -> list[Bundle]:
    """Read one or more Sigstore bundles from a JSON or JSON Lines file."""
    text = bundle_path.read_text(encoding="utf-8")
    try:
        documents = [json.dumps(json.loads(text))]
    except json.JSONDecodeError:
        documents = [line for line in text.splitlines() if line.strip()]
    if not documents:
        raise SystemExit(f"error: bundle file '{bundle_path}' is empty")
    try:
        return [Bundle.from_json(document) for document in documents]
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"error: cannot parse '{bundle_path}': {exc}") from exc


def statement_subjects(attestation: Attestation) -> list[dict]:
    """Decode the in-toto statement of an attestation and return its subjects."""
    statement = json.loads(attestation.envelope.statement)
    return statement.get("subject", [])


def sha256_digest(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument(
        "--bundle",
        action="append",
        required=True,
        type=Path,
        help="Sigstore bundle file from actions/attest (repeatable)",
    )
    parser.add_argument(
        "distributions",
        nargs="+",
        type=Path,
        help="Distribution files (wheel or sdist) to write attestations for",
    )
    arguments = parser.parse_args()

    attestations: list[tuple[Attestation, list[dict]]] = []
    for bundle_path in arguments.bundle:
        for bundle in read_bundles(bundle_path):
            attestation = Attestation.from_bundle(bundle)
            subjects = statement_subjects(attestation)
            if len(subjects) != 1:
                raise SystemExit(
                    f"error: a bundle in '{bundle_path}' attests {len(subjects)} subjects; "
                    "PyPI requires exactly one subject per attestation, so run actions/attest "
                    "once per distribution instead of once for all of them"
                )
            attestations.append((attestation, subjects))

    for distribution in arguments.distributions:
        if not distribution.is_file():
            raise SystemExit(f"error: distribution '{distribution}' does not exist")
        digest = sha256_digest(distribution)
        matches = [
            attestation
            for attestation, subjects in attestations
            if subjects[0].get("digest", {}).get("sha256") == digest
            and subjects[0].get("name") == distribution.name
        ]
        if len(matches) != 1:
            raise SystemExit(
                f"error: found {len(matches)} attestations for '{distribution.name}' "
                f"(sha256:{digest}); expected exactly one"
            )
        destination = distribution.with_name(f"{distribution.name}.publish.attestation")
        destination.write_text(matches[0].model_dump_json(), encoding="utf-8")
        print(f"wrote {destination}", file=sys.stderr)


if __name__ == "__main__":
    main()
