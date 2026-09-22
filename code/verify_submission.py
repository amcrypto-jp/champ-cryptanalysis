#!/usr/bin/env python3
"""Identify the reviewed third-party submission and check the STS row extracts."""
import argparse
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]


def verify(root):
    manifest = json.loads((PACKAGE / "data/submission-sha256.json").read_text())
    for name, expected in manifest["sha256"].items():
        path = root / name
        if not path.is_file():
            raise SystemExit(f"Missing reviewed input: {name}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"Reviewed-input checksum mismatch: {name}")
    rows = json.loads((PACKAGE / "data/nist-flagged-rows.json").read_text())
    for row in rows:
        path = root / "Others/NIST pseudorandomness tests" / row["report"]
        lines = path.read_text().splitlines()
        if lines[row["line"] - 1] != row["text"]:
            raise SystemExit(f"Statistical row mismatch: {row['report']}:{row['line']}")
    print(f"PASS: {len(manifest['sha256'])} reviewed-input SHA-256 values and "
          f"{len(rows)} statistical report rows match", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission_root", type=Path)
    verify(parser.parse_args().submission_root)
