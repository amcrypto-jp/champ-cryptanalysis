# Reproducing the evidence

**Release 1.0.1 · 22 September 2026**

Run the commands below from the repository root or extracted package directory. The programs also
resolve their inputs correctly when invoked by absolute path from another
directory. Use Python 3.8 or later. Do not enable `-O` or `PYTHONOPTIMIZE`:
assertions implement the mathematical checks and the programs reject that mode.

**Quick checks, with no external data or Python packages:**

```sh
python3 verify_package.py
python3 run.py --output-dir verification-output
```

This independently verifies the twelve saved collision pairs using integer
products, checks that those pairs do not collide at either full parameter set,
and runs the model demonstrations with a 24-bit meet-in-the-middle target.
It does not compile the original C sources or perform proof-enabled primality
tests. Logs are written to the named output directory; saved evidence is unchanged.

**Full mathematical replay:**

```sh
python3 run.py --full --output-dir verification-full
```

This uses the 40-bit preimage target, regenerates all twelve reduced-parameter
collisions with the recorded seeds, independently verifies the regenerated pairs,
and compares every saved record except its wall-clock timing. The 40-bit search
stores about one million matrices and can use several hundred megabytes of RAM.
The collision search is restricted to small demonstration fields; it does not
attempt the full 128-bit or 256-bit fields.

**Original-source conformance and parameter proofs:**

```sh
python3 run.py --full --submission-root "/path/to/CHAMP" --sage sage --output-dir verification-complete
```

Replace `/path/to/CHAMP` with the original submission directory containing
`Algorithm specifications`, `Implementations and Test_Vectors`, and `Others`.
The program checks all nineteen required source hashes before compiling or
claiming conformance. The separate author-hosted preprint is not a substitute
for that submission. See [PROVENANCE.md](PROVENANCE.md) for exact identification.

The C checks need GCC (or a compatible compiler selected with `--cc`) and a
platform supporting the supplied C code and `-shared -fPIC`. They were tested
on x86-64 Linux, GCC 15.2.0. The Python-only checks do not need a compiler.
`--sage sage` requests SageMath explicitly; use its executable path if necessary.
Parameter proofs were run with SageMath 10.9. The runner returns a nonzero exit
status on any requested check failure and does not silently omit a requested
dependency. C libraries and Sage preprocessor output are built in temporary
directories. The original submission is only read.

Individual checks can also be run directly:

```sh
python3 code/check_collisions.py
python3 code/subgroup.py --bits 16 20 24 28 --trials 3 --output new-collisions.json
python3 code/check_collisions.py new-collisions.json
python3 code/reproduce.py --mitm-bits 40 --submission-root "/path/to/CHAMP"
sage code/parameters.sage
```

| Recorded artifact | Coverage |
|---|---|
| [reproduce-full.log](evidence/reproduce-full.log) | Both full parameter sets; independent model and four C builds; naive prefix/suffix/sandwich MAC forgeries; bit 5000 recovery; full 5000-bit recovery from consecutive digests in the model; ignored digest length; 8,194 short KATs checked against the model and both C versions; eight long constant-message KATs checked by exponentiation; 40-bit modular preimage search; exhaustive 12-bit injectivity checks |
| [parameters.log](evidence/parameters.log) | Proof-enabled primality for both p and q; every larger candidate safe prime excluded; generator-order and splitting checks |
| [subgroup.log](evidence/subgroup.log) and [replay.log](evidence/replay.log) | Three collision searches at each of 16, 20, 24 and 28 field bits; exact seeded replay, apart from timing |
| [collisions.json](data/collisions.json) | Complete bitstrings, primes, seeds, digest bytes, sample counts and original timings |
| [certificates.log](evidence/certificates.log) | Verification by separate integer-product formulas, importing neither the search code nor the model |
| [nist-flagged-rows.json](data/nist-flagged-rows.json) | Four marked results with exact filenames and one-based line numbers |
| [submission-sha256.json](data/submission-sha256.json) | Nineteen input hashes; the source verifier also compares the statistical-row extracts |

Coverage limits: the large DRBG-expanded KATs and million-iteration loop KATs
were not regenerated. No new throughput measurement, dynamic concurrency test,
or timing/cache exploit is claimed. Reduced-parameter collisions do not establish
mixing or attack cost at the full parameters. The Sage script proves primality
through Sage's proof-enabled routines; this package does not contain separately
exported primality certificates.

**Rebuilding the documents.** The prebuilt PDF and HTML require no build tools.
To regenerate them, install Pandoc and Tectonic, plus DejaVu Serif/Sans/Mono fonts,
then run:

```sh
python3 build_documents.py
```

The release was built with Pandoc 3.11 and Tectonic 0.17.0. Tectonic may fetch TeX
resources on its first run. HTML uses native MathML and embedded CSS, with no
JavaScript or remote rendering dependencies. Modern browsers with MathML support
are needed for mathematical layout. PDF byte-for-byte reproducibility is not
promised across font or typesetting versions. Rebuilding a document intentionally
changes its checksum; the distributed `SHA256SUMS` describes the distributed files.
