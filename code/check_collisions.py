#!/usr/bin/env python3
"""Verify the saved collision certificates by a second arithmetic path.

Computes whole products over the integers before reduction, using explicit
generator formulas. Imports neither model.py nor the collision search code.
Also checks that the saved toy examples are not full-parameter collisions.
"""
import json
import argparse
from pathlib import Path

if not __debug__:
    raise SystemExit("Assertions are required: do not use Python -O or PYTHONOPTIMIZE")


def integer_product(bits):
    a, b, c, d = 1, 0, 0, 1
    for bit in bits:
        if bit == "0":
            a, b, c, d = -2*a+4*b, a-3*b, -2*c+4*d, c-3*d
        elif bit == "1":
            a, b, c, d = -5*a-6*b, 2*a+2*b, -5*c-6*d, 2*c+2*d
        else:
            raise ValueError("Certificate contains a non-bit")
    return a, b, c, d


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("certificates", type=Path, nargs="?",
                    default=Path(__file__).resolve().parents[1] / "data/collisions.json")
records = json.loads(parser.parse_args().certificates.read_text())
assert records, "No certificates supplied"
for record in records:
    u, v, p = record["u"], record["v"], record["p"]
    assert u != v and len(u) == len(v) == record["collision_bits"]
    U, V = integer_product(u), integer_product(v)
    assert U != V
    reduced = tuple(x % p for x in U)
    assert reduced == tuple(x % p for x in V)
    width = (p.bit_length() + 7)//8
    digest = b"".join((pow(reduced[i], -1, p) if reduced[i] else 0).to_bytes(width, "little")
                      for i in (0, 2, 1, 3))
    assert digest.hex() == record["digest_le"]
    for full_p in ((1 << 128) - 15449, (1 << 256) - 36113):
        assert tuple(x % full_p for x in U) != tuple(x % full_p for x in V)
    print(f"PASS p={p}, seed={record['seed']}, length={len(u)}: "
          "integer-product verification; not a collision at either full parameter set")
print(f"PASS: independently verified all {len(records)} saved pairs.")
