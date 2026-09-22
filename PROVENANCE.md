# Reviewed inputs and version boundaries

The review target is the supplied ten-page file
`Algorithm specifications/CHAMP Algorithm Specifications.pdf`. It has no visible
version identifier on its title page. Its SHA-256 is:

```text
c1201fe48fe45033c9a97e39ff83928e683ac1d69703ec31987752f6f7dfaa69
```

The four C implementations, associated headers, six selected KAT files and four
NIST reports are identified in [submission-sha256.json](data/submission-sha256.json).
All nineteen paths are relative to the original submission root. This manifest
identifies the files actually used for the published checks. It is not a manifest
of every file in the original submission.

**Separate public preprint.** On 21 September 2026, Vladimir Shpilrain's
[publications page](https://shpilrain.ccny.cuny.edu/papers.html) linked to a
twelve-page [CHAMP preprint](https://shpilrain.ccny.cuny.edu/Cayley%20hash%20paper.pdf)
by Alexander Demin, Alexey Ovchinnikov and Vladimir Shpilrain. The retrieved copy
contains 416,165 bytes and has SHA-256:

```text
d75f4323c051eb0058e54d9b2ffaece6268afb5c18e5a8a25481957e7ef220ef
```

This preprint differs from the supplied specification. In particular, its §6.2
and bibliography cite Mullan–Tsaban, whereas the supplied specification does not.
The implemented primary matrices, primes and invertible entrywise finalization
are unchanged in the descriptions examined. The public report nevertheless
targets the supplied specification; it is not a comprehensive assessment of
the separate preprint, and its page/section references must not be applied to it.
The author-hosted URL can change; the hash identifies the copy inspected here.
No public download location for the exact reviewed submission bundle is asserted.

**Independent preparation and later related-work citations.** The findings,
derivations, research code and reproduction experiments were completed
independently of Markku-Juhani O. Saarinen's
[CHAMP report](https://ngcc.dev/reports/hash-04.html) and the two CryptHash Forum
comments identified below. Mounir IDRASSI brought Saarinen's report and then the
forum thread into this review process on 22 September 2026, after the technical
report and reproducibility package were complete. The comparisons and citations
were added afterward. The subgroup method used in this review is credited to
Mullan–Tsaban in §2 of the report.

Saarinen's page dates both entries (`hash-04-1` and `hash-04-2`) to
21 September 2026 and displays an update time of 18:31:51 UTC that day. The HTML
retrieved on 22 September 2026 contains 5,201 bytes and has SHA-256:

```text
29d0603ac4b3b3229fa843d20f6f88f8652574fd64243e8bc5bcde8c8ffd0165
```

The two substantive comments in the
[CHAMP public-comment thread](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/thread/3TE6PYI75TISXJLDPZMLKZA7LWQFN65T/?noscript)
are cited by their individual message permalinks:

- [cuihr26, signed "Tsinghua Hash Lab"](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/QNMIAAKIPHG5FEK7QZEE2ZYBOWQHCZUE/).
  *Re: Round1: Public Comment: CHAMP*, posted 22 September 2026. The individual
  message HTML retrieved that day contains 31,975 bytes; SHA-256:

  ```text
  7b788c25cb8fd0c34448331e37841f051b8bcfdf79140455efc37aa113698c0f
  ```

- [Cryptanalysts001, signed "ISCAS"](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/6LSOFTTMTDWFWWRAZDREDYJNG5NXDVEC/).
  *Re: Round1: Public Comment: CHAMP*, posted 22 September 2026. The individual
  message HTML retrieved that day contains 31,924 bytes; SHA-256:

  ```text
  28e06ef24d8c13c2e83fe12a776c05d4dd7bc7f1843e532d7407461bb0ed72ef
  ```

The usernames and signatures reproduce the attribution displayed on the posts.
These sources are cited to acknowledge overlapping public analysis identified
after completion. The dates and hashes identify the retrieved material; they do
not establish relative discovery times. [FINDINGS.md](FINDINGS.md) records the
comparison with the cited versions. The third-party HTML pages are not bundled.

**Statistical reports.** Paths are relative to
`Others/NIST pseudorandomness tests/` in the original submission. The factual
extracts are in [nist-flagged-rows.json](data/nist-flagged-rows.json).

| File | Flagged lines |
|---|---|
| `report_m214m3_m52m62_512.txt` | 156 |
| `report_m214m3_m52m62_1024.txt` | 63, 123 |
| `report_m214m3_64m2m1_512.txt` | 186 |
| `report_m214m3_64m2m1_1024.txt` | None |

**Implementation locations.** Each location below is in
`CryptHash_AlgorithmInstance.c`, underneath
`Implementations and Test_Vectors/API_CryptHash/Implementations/`.
Line numbers are one-based in the exact hashed files.

| Subdirectory | Ignored digest length | Global ready flag / table initialization | Message-indexed table access | Example data-dependent arithmetic branch |
|---|---:|---|---|---:|
| `Reference_Implementation/CHAMP-512` | 270 | 235–254 | 279 | 171 |
| `Reference_Implementation/CHAMP-1024` | 299 | 264–283 | 308 | 195 |
| `Optimized_Implementation/CHAMP-512` | 552 | 59–60, 430–435 | 524–525, 538 | 229 |
| `Optimized_Implementation/CHAMP-1024` | 677 | 73–74, 547–552 | 643–646, 663 | 288 |

The ignored-length behavior was tested with a buffer large enough for the full
digest and guard bytes. The initialization race and timing observations are
source-level findings, with no reproduced erroneous digest or leakage exploit.

**AI-use disclosure.** Moonshot AI's kimi-k3 was used for the main review.
OpenAI's GPT-6 Astra was used for polishing and preparing the publication package,
including additional technical analysis, cross-checking of claims, and
development of reproducibility code. Mounir IDRASSI is responsible for the final
report and its conclusions.

**Origin of the included programs.** The Python matrix model, tests, collision
search and certificate verifier were written for this assessment. The subgroup
search adapts the method credited to Mullan–Tsaban; it is not copied from their
implementation. The certificate verifier uses explicit integer recurrences and
imports neither the model nor the search program. Original third-party PDFs,
source files, KAT files and statistical reports are identified but not bundled.

**Reuse terms.** Original software is licensed under MIT; the report, original
documentation and original results under CC BY 4.0. These grants exclude
third-party material, including the statistical-report rows in
`data/nist-flagged-rows.json`. See [LICENSING.md](LICENSING.md) for the exact scope
and complete license texts.

The recorded execution environment was x86-64 Linux
6.6.87.2-microsoft-standard-WSL2, glibc 2.43, Python 3.14.4,
GCC 15.2.0 and SageMath 10.9. Exact per-run output is retained in `evidence/`.
Wall-clock measurements depend on hardware and load and are demonstrations,
not comparative benchmarks.
