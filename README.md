# CHAMP: technical assessment of the submitted specification

**Mounir IDRASSI** · [mounir@amcrypto.jp](mailto:mounir@amcrypto.jp)  
Version 1.0.1 · 22 September 2026

This release contains a public technical report and reproducible evidence about
the supplied CHAMP specification. Read the [PDF report](REPORT.pdf) or
[Markdown report](REPORT.md) on GitHub. For an offline web version, download
[REPORT.html](REPORT.html) and open it locally. The editable sources are
[REPORT.md](REPORT.md) and [REPORT.tex](REPORT.tex).

**AI-use disclosure.** Moonshot AI's kimi-k3 was used for the main review.
OpenAI's GPT-6 Astra was used for polishing and preparing the publication package,
including additional technical analysis, cross-checking of claims, and
development of reproducibility code. Mounir IDRASSI is responsible for the final
report and its conclusions.

**Independent preparation.** The findings, derivations and experiments were
completed independently of [Saarinen's CHAMP report](https://ngcc.dev/reports/hash-04.html)
and public comments signed
[Tsinghua Hash Lab](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/QNMIAAKIPHG5FEK7QZEE2ZYBOWQHCZUE/)
and [ISCAS](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/6LSOFTTMTDWFWWRAZDREDYJNG5NXDVEC/).
Mounir IDRASSI became aware of these sources on 22 September 2026, after this
review and its reproducibility package were complete. They are cited as related
work identified afterward. See [PROVENANCE.md](PROVENANCE.md) for the chronology
and [FINDINGS.md](FINDINGS.md) for the overlap and additional contributions:
the explicit subgroup search and collision certificates, demonstrated naive-MAC
forgeries, related-digest and short-input recovery, and digest-length,
initialization and timing findings.

The principal finding is a concrete adaptation of a subgroup collision-search
strategy to CHAMP's determinant-2 matrices, with twelve reduced-parameter
collision certificates. Its projected full-parameter work factors depend on
mixing assumptions. The package also demonstrates forgeries against naive keyed
constructions and a short-input preimage search at the full parameters, and
documents specification and implementation issues. **It does not demonstrate a
practical full-parameter collision, a distinct second preimage, or recovery of a
uniformly random long input from a single digest.**

| File | Purpose |
|---|---|
| [REPORT.pdf](REPORT.pdf) | Typeset public report, with the requested byline |
| [REPORT.html](REPORT.html) | Standalone report with native MathML; no network needed for rendering |
| [FINDINGS.md](FINDINGS.md) | Finding-to-evidence index and limits |
| [REPRODUCING.md](REPRODUCING.md) | Exact commands, dependencies and test coverage |
| [PROVENANCE.md](PROVENANCE.md) | Document versions, source locations and input hashes |
| [AI_DISCLOSURE.md](AI_DISCLOSURE.md) | AI tools used and their roles in preparing the review |
| [LICENSING.md](LICENSING.md) | MIT for code; CC BY 4.0 for the report and original results; scope and attribution |
| [CHANGES.md](CHANGES.md) | Release history and scope of this revision |
| [GITHUB.md](GITHUB.md) | Repository layout and release publication instructions |
| [code](code) / [data](data) / [evidence](evidence) | Independent programs, complete certificates and recorded transcripts |
| [ABSTRACT.txt](ABSTRACT.txt) | Plain-text abstract for a publication or repository submission |
| [ANNOUNCEMENT.md](ANNOUNCEMENT.md) | Ready-to-paste community announcement |
| [AUTHOR_LETTER.txt](AUTHOR_LETTER.txt) | Cover letter for the CHAMP authors |
| [CITATION.cff](CITATION.cff) / [references.bib](references.bib) | Citation metadata and bibliography |
| [SHA256SUMS](SHA256SUMS) | Checksums of the distributed files |

After extracting the archive, run:

```sh
python3 verify_package.py
python3 run.py
```

The second command verifies all saved collisions and runs the quick mathematical
demonstrations using only Python's standard library. [REPRODUCING.md](REPRODUCING.md)
also gives the commands for the 40-bit preimage demonstration, complete seeded
collision replay, C/KAT comparisons and proof-enabled SageMath parameter checks.

The original specification, implementations and KATs are not redistributed.
Their exact hashes are supplied for optional conformance checks against a
separately obtained copy. The mathematical model and saved certificates work
without those files. The distinct author-hosted preprint is identified explicitly;
the report's page references concern the supplied ten-page specification.

This package prepares material for distribution; its contents do not claim that
the authors have already been contacted or that the report has undergone peer
review. No public repository URL or DOI has been assigned in this package.

Copyright © 2026 Mounir IDRASSI for the original contributions. The code is
licensed under the [MIT License](LICENSE); the report, original documentation
and original results under [CC BY 4.0](LICENSES/CC-BY-4.0.txt). See
[LICENSING.md](LICENSING.md) for the file scope, attribution and third-party
exceptions. The research programs are not production cryptographic software.
