#!/usr/bin/env python3
"""Reduced-parameter CHAMP collision search using triangular subgroups.

Adaptation of the two-stage commuting-matrix method in Mullan--Tsaban,
https://arxiv.org/abs/1306.5646, Section 4, directly to CHAMP's GL2 matrices.
The algebra is exact; the square-root field-size cost is a mixing heuristic.
Only reduced parameters are searched. No full-parameter collision is claimed.
"""

import argparse
import json
import math
import random
import time
from pathlib import Path

from model import A, B, I, encode, mul, product

if not __debug__:
    raise SystemExit("Assertions are required: do not use Python -O or PYTHONOPTIMIZE")

# P=[[1,2],[2,3]], det(P)=-1. These identities hold over Z, for every odd p.
P = (1, 2, 2, 3)
PINV = (-3, 2, 2, -1)
C = (-4, 1, 2, -1)
D = (-1, 0, 0, -2)
assert mul(mul(PINV, A), P) == C
assert mul(mul(PINV, B), P) == D


def is_prime_small(n):
    """Deterministic trial division; used only for <=32-bit demonstration primes."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, math.isqrt(n) + 1, 2))


def safe_prime(bits):
    """Match both the safe-prime condition and CHAMP's p == 7 (mod 8)."""
    n = (1 << bits) - 1
    while not (is_prime_small(n) and is_prime_small((n - 1) // 2)):
        n -= 8
    return n


def line(x, y, p):
    """Projective point [x:y], encoded by y/x, or None when x=0.

    In this reciprocal-coordinate encoding, [1:0] has code zero.
    """
    return y * pow(x, -1, p) % p if x else None


def search(p, seed):
    started = time.perf_counter()
    rng = random.Random(seed)
    bits = p.bit_length()
    # Longer walks than the shortest possible enumeration: no claim to optimize
    # constants or collision length, and no need for inverse letters in outputs.
    width = 2 * bits
    limit = 40 * math.isqrt(p) + 100
    inverse_lines = {}
    triangular_word = None
    for phase1 in range(1, limit + 1):
        word = f"{rng.getrandbits(width):0{width}b}"
        matrix = product(word, p, (C, D))
        a, b, c, d = matrix
        code = line(a, c, p)  # matrix * infinity
        if code in inverse_lines:
            prefix, before = inverse_lines[code]
            candidate = prefix + word
            t = mul(before, matrix, p)
            assert t[2] == 0
            if "0" in candidate:
                triangular_word, triangular = candidate, t
                break
        inverse_lines.setdefault(line(d, -c % p, p), (word, matrix))
    if triangular_word is None:
        raise RuntimeError("Phase 1 search limit reached; no complexity theorem assumed")

    seen = {}
    for phase2 in range(1, limit + 1):
        choices = f"{rng.getrandbits(width):0{width}b}"
        if "1" not in choices:
            continue
        matrix = product(choices, p, (D, triangular))
        word = "".join("1" if b == "0" else triangular_word for b in choices)
        a, b, c, d = matrix
        assert c == 0
        # For upper triangular invertible matrices, commuting is exactly
        # b'*(a-d) = b*(a'-d'). Scalars and diagonal matrices handled directly.
        if b == 0:
            other_word, other = "1", tuple(x % p for x in D)
        else:
            code = (a - d) * pow(b, -1, p) % p
            if code not in seen:
                seen[code] = (word, matrix)
                continue
            other_word, other = seen[code]
        u, v = word + other_word, other_word + word
        if u == v:
            continue
        assert mul(matrix, other, p) == mul(other, matrix, p)
        # Independently recompute using the original generators and digest.
        hu, hv = product(u, p), product(v, p)
        assert len(u) == len(v) and hu == hv
        assert encode(hu, p) == encode(hv, p)
        return {
            "p": p, "field_bits": bits, "seed": seed,
            "phase1_samples": phase1, "phase2_samples": phase2,
            "samples_over_sqrt_p": (phase1 + phase2) / math.sqrt(p),
            "collision_bits": len(u), "u": u, "v": v,
            "digest_le": encode(hu, p).hex(),
            "seconds": time.perf_counter() - started,
        }
    raise RuntimeError("Phase 2 search limit reached; no complexity theorem assumed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, nargs="+", default=[16, 20, 24, 28])
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if any(not 8 <= b <= 32 for b in args.bits):
        parser.error("This demonstrator accepts field sizes 8..32 bits only")
    if args.trials < 1:
        parser.error("--trials must be positive")
    results = []
    for bits in args.bits:
        p = safe_prime(bits)
        for seed in range(args.trials):
            result = search(p, seed)
            results.append(result)
            print(json.dumps({k: v for k, v in result.items()
                              if k not in ("u", "v", "digest_le")}), flush=True)
    if args.output:
        args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(f"PASS: {len(results)} distinct, equal-length reduced-parameter collisions; "
          "full parameters NOT searched.")


if __name__ == "__main__":
    main()
