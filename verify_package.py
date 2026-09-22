#!/usr/bin/env python3
"""Check every distributed file against SHA256SUMS. Does not authenticate authorship."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent
count = 0
for line in (root / "SHA256SUMS").read_text().splitlines():
    expected, name = line.split("  ", 1)
    path = (root / name).resolve()
    if root not in path.parents:
        raise SystemExit(f"Invalid manifest path: {name}")
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"FAIL: {name}")
    count += 1
if not count:
    raise SystemExit("FAIL: empty manifest")
print(f"PASS: {count} distributed files match SHA256SUMS.")
