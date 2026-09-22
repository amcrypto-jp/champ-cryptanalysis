#!/usr/bin/env python3
"""Reproduce the report's concrete claims, optionally using all four C builds.

Run from any directory. Requires Python >=3.8; C checks need gcc and the original
submission supplied with --submission-root. Uses temporary build
directories. The million-iteration KATs and DRBG-expanded large KATs are not
claimed as independently verified by this program. --mitm-bits controls the
exponential preimage demonstration (40 needs substantial memory).
"""

import argparse
import ctypes
import platform
import random
import subprocess
import tempfile
import time
from pathlib import Path

from model import (A, B, ALT, I, PRIMES, decode, det, encode, hash_bits, inv,
                   mitm, mul, pack, power, product, unpack)

if not __debug__:
    raise SystemExit("Assertions are required: do not use Python -O or PYTHONOPTIMIZE")


def records(path):
    record = {}
    for line in path.read_text().splitlines() + [""]:
        if not line.strip():
            if "Msg_Len" in record and "Dst" in record:
                yield record
            record = {}
        elif "=" in line:
            key, value = line.split("=", 1)
            record[key.strip()] = value.strip()


def make_c_hash(path, target, compiler):
    subprocess.run([compiler, "-std=c99", "-O2", "-shared", "-fPIC", str(path),
                    "-o", str(target)], check=True, capture_output=True)
    library = ctypes.CDLL(str(target))
    fn = library.CryptHash
    fn.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_void_p]
    fn.restype = ctypes.c_int

    def run(bits, size, requested=None):
        data = ctypes.create_string_buffer(pack(bits))
        output = ctypes.create_string_buffer(b"\xa5" * (size // 8 + 16))
        rc = fn(size if requested is None else requested, data, len(bits), output)
        assert output.raw[size // 8:size // 8 + 16] == b"\xa5" * 16
        return rc, output.raw[:size // 8]

    return run


def check_parameters():
    for size, p in PRIMES.items():
        q = (p - 1) // 2
        assert pow(2, q, p) == 1 and p % 8 == 7
        assert power(B, q, p) == (p - 1, 0, 0, p - 1)
        assert power(B, 2 * q, p) == I
        square17 = pow(17, q, p) == 1
        assert square17 == (size == 1024)
        assert (power(A, q, p) == I) == (size == 1024)
        if size == 1024:
            assert power(ALT, q, p) == (p - 1, 0, 0, p - 1)
        else:
            assert power(A, p + 1, p) == (2, 0, 0, 2)
        bound = p * (p * p - 1)
        assert bound < 1 << (3 * p.bit_length())
        state = I
        for n in range(1, p.bit_length() + 1):
            state = mul(state, A)
            if max(abs(x) for x in state) > p // 2:
                break
        print(f"PARAM CHAMP-{size}: 17 square={square17}, A^q=I={power(A,q,p)==I}, "
              f"B^q=-I; all-zero centered lift first fails at {n} bits; "
              f"pigeonhole at {3*p.bit_length()} bits", flush=True)


def check_protocols(size, p, c_functions):
    rng = random.Random(size)
    bits = lambda n: f"{rng.getrandbits(n):0{n}b}"
    key, suffix_key = bits(256), bits(192)
    known, replacement = bits(400), bits(517)
    known_matrix = product(known, p)
    replacement_matrix = product(replacement, p)
    model_hash = lambda message, size, requested=None: (0, hash_bits(message, p))
    for implementation, c_hash in [("Model", model_hash)] + c_functions:
        h = lambda message: c_hash(message, size)[1]
        # One observed tag reveals an equivalent key state, then arbitrary tags.
        prefix_tag = decode(h(key + known), p)
        equivalent_prefix = mul(prefix_tag, inv(known_matrix, p), p)
        assert encode(mul(equivalent_prefix, replacement_matrix, p), p) == h(key + replacement)
        same_length = replacement[:len(known)]
        assert len(same_length) == len(known) and same_length != known
        assert encode(mul(equivalent_prefix, product(same_length, p), p), p) == h(key + same_length)
        suffix_tag = decode(h(known + suffix_key), p)
        equivalent_suffix = mul(inv(known_matrix, p), suffix_tag, p)
        assert encode(mul(replacement_matrix, equivalent_suffix, p), p) == h(replacement + suffix_key)
        # Three chosen tags suffice for a naive two-sided secret construction.
        t_empty = decode(h(key + suffix_key), p)
        t0 = decode(h(key + "0" + suffix_key), p)
        t1 = decode(h(key + "1" + suffix_key), p)
        conjugated = (mul(t0, inv(t_empty, p), p), mul(t1, inv(t_empty, p), p))
        forged = mul(product(replacement, p, conjugated), t_empty, p)
        assert encode(forged, p) == h(key + replacement + suffix_key)
        # Real late-prefix C digests; not merely the first bits of a long array.
        stream = bits(5000)
        previous = decode(h(stream[:4999]), p)
        current = decode(h(stream), p)
        assert mul(inv(previous, p), current, p) == tuple(x % p for x in (A, B)[int(stream[-1])])
        print(f"CHAMP-{size} {implementation}: prefix/suffix arbitrary-message forgery, "
              "3-query sandwich forgery, bit 5000 recovery PASS", flush=True)
        if implementation != "Model":
            # Full-size guard buffer: the demonstration itself does not overflow.
            rc, wrong_length_digest = c_hash("101", size, requested=size // 2)
            assert rc == 0 and wrong_length_digest == h("101")
            assert wrong_length_digest[size // 16:] != b"\xa5" * (size // 16)
            print(f"C CHAMP-{size} {implementation}: requested {size//2} digest bits, "
                  f"returned success and wrote {size} bits", flush=True)

    stream = bits(5000)
    previous, state = I, I
    recovered = ""
    for bit in stream:
        state = mul(state, (A, B)[int(bit)], p)
        decoded = decode(encode(state, p), p)
        ratio = mul(inv(previous, p), decoded, p)
        recovered += "0" if ratio == tuple(x % p for x in A) else "1"
        assert ratio == tuple(x % p for x in (A, B)[int(bit)])
        previous = decoded
    assert recovered == stream
    print(f"MODEL CHAMP-{size}: recovered all 5000 bits from 5001 consecutive digests PASS", flush=True)

    # One-digest determinant test; its random-oracle acceptance count is exact.
    for n in (0, 1, 17, 128, 1000, 5000):
        message = stream[:n]
        assert det(decode(hash_bits(message, p), p), p) == pow(2, n, p)
    print(f"MODEL CHAMP-{size}: one-query determinant test PASS; random acceptance "
          f"p*(p^2-1)/2^{size} (approximately 2^-{p.bit_length()})", flush=True)


def check_kats(size, p, c_functions, vectors):
    count = 0
    path = vectors / f"KAT_2_12_CHAMP-{size}.txt"
    for record in records(path):
        n = int(record["Msg_Len"])
        bits = unpack(bytes.fromhex(record["Msg"]), n)
        expected = bytes.fromhex(record["Dst"])
        assert len(bits) == n
        assert hash_bits(bits, p) == expected, (path.name, n, "independent model")
        for name, c_hash in c_functions:
            rc, actual = c_hash(bits, size)
            assert rc == 0 and actual == expected, (path.name, n, name)
        count += 1
    assert count == 4097
    assert encode(product("1", p), p, "big") != hash_bits("1", p)
    print(f"KAT CHAMP-{size}: all {count} short vectors agree with independent model "
          "and both C builds; Julia byte-order discrepancy confirmed", flush=True)
    long_count = 0
    for name in ("2_23", "2_33"):
        for record in records(vectors / f"KAT_{name}_CHAMP-{size}.txt"):
            expansion = record.get("Msg_Exp", "").split()
            if not expansion or expansion[0] not in ("0000000000000000", "FFFFFFFFFFFFFFFF"):
                continue
            matrix = power(A if expansion[0][0] == "0" else B, int(record["Msg_Len"]), p)
            assert encode(matrix, p).hex().upper() == record["Dst"].upper()
            long_count += 1
    assert long_count == 4
    print(f"KAT CHAMP-{size}: {long_count} long constant-message vectors checked by "
          "matrix exponentiation; DRBG and Monte-Carlo vectors NOT rerun", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mitm-bits", type=int, default=32)
    parser.add_argument("--skip-kats", action="store_true")
    parser.add_argument("--submission-root", type=Path)
    parser.add_argument("--cc", default="gcc", help="C compiler executable")
    args = parser.parse_args()
    if not 2 <= args.mitm_bits <= 40:
        parser.error("--mitm-bits must be between 2 and 40")
    if args.submission_root:
        from verify_submission import verify
        verify(args.submission_root)
    start = time.perf_counter()
    print(platform.platform(), platform.python_version(), flush=True)
    check_parameters()
    if not args.submission_root:
        print("MODEL-ONLY run: original C implementations and KATs not checked", flush=True)
    with tempfile.TemporaryDirectory(prefix="champ-review-") as build:
        for size, p in PRIMES.items():
            c_functions = []
            if args.submission_root:
                base = args.submission_root / "Implementations and Test_Vectors/API_CryptHash"
                for kind in ("Reference", "Optimized"):
                    source = base / "Implementations" / f"{kind}_Implementation/CHAMP-{size}/CryptHash_AlgorithmInstance.c"
                    c_functions.append((kind, make_c_hash(source, Path(build) / f"{kind}-{size}.so", args.cc)))
            check_protocols(size, p, c_functions)
            if args.submission_root and not args.skip_kats:
                check_kats(size, p, c_functions, base / "Test_Vectors")

    # All 12-bit messages have distinct digests at each full parameter size:
    # finding a preimage in that domain cannot give a distinct second preimage.
    for size, p in PRIMES.items():
        domain = [f"{x:012b}" for x in range(1 << 12)]
        assert len({product(w, p) for w in domain}) == len(domain)
        chosen = domain[1777]
        assert mitm(product(chosen, p), 12, p) == chosen
        print(f"SECOND PREIMAGE CHAMP-{size}: 4096 distinct 12-bit products; "
              "MITM returns the original, no second preimage", flush=True)

    n = args.mitm_bits
    target_word = f"{random.Random(20260921).getrandbits(n):0{n}b}"
    for p in (65519, PRIMES[1024]):
        t = time.perf_counter()
        target = product(target_word, p)
        result = mitm(target, n, p)
        assert result is not None and hash_bits(result, p) == hash_bits(target_word, p)
        exact = product(target_word)
        centered = tuple(x if x <= p//2 else x-p for x in target)
        print(f"MITM field_bits={p.bit_length()}, input_bits={n}: PASS; "
              f"seconds={time.perf_counter()-t:.3f}; centered_integer_lift_exact={centered==exact}; "
              f"target={target_word}; recovered={result}", flush=True)
    print(f"PASS: all requested independent checks; elapsed={time.perf_counter()-start:.3f}s", flush=True)


if __name__ == "__main__":
    main()
