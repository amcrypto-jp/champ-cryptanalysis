# Findings and supporting evidence

This index accompanies [REPORT.pdf](REPORT.pdf), version 1.0.1, by Mounir IDRASSI.
Section numbers refer to that report. The evidence classes distinguish what was
proved algebraically, executed, inferred under assumptions, or observed in source.

| ID | Finding | Evidence | Limit |
|---|---|---|---|
| C1 | Subgroup collision construction applies directly to the implemented pair (§2) | Exact conjugation and commuting criterion; [search](code/subgroup.py); twelve complete [certificates](data/collisions.json); [independent verifier](code/check_collisions.py) | Collisions demonstrated only for 16–28-bit primes |
| C2 | Projected leading collision exponents 64 / 128 (§2) | Two searches over about p projective points/codes | Heuristic mixing and word-length assumptions; substantial memory; no full-parameter run |
| A1 | Fixed-length range at most p(p²−1); same-length collisions forced at 384 / 768 bits (§3) | Determinant identity and exact counting | Existence does not locate a collision; fixed-length surjectivity is not assumed |
| A2 | Exact different-length constraint and corrected q threshold (§3) | Determinant order; [Sage checks](code/parameters.sage) and [transcript](evidence/parameters.log) | The symbolic A^q identity has an astronomical message length |
| P1 | Naive prefix and suffix MACs permit arbitrary-message forgery from one known pair (§4) | Algebra; [full-parameter model and four C tests](evidence/reproduce-full.log) | Applies to these constructions, not HMAC |
| P2 | Naive sandwich MAC permits forgery after queries ε, 0, 1 (§4) | Conjugated-generator recovery; same transcript | Chosen-message access includes the empty and one-bit messages |
| P3 | Consecutive prefix digests reveal appended bits at any length (§4) | 5,000-bit model recovery; late-bit check in each C build | Requires related digests; does not settle isolated-digest prediction |
| P4 | Modular meet-in-the-middle short-preimage search (§5) | 40-bit full-parameter example plus reduced-prime wrapped example | Exponential storage; not a long-input or second-preimage break |
| A3 | Known-length digests are efficiently distinguishable from uniform (§6) | Exact determinant predicate and acceptance count | Does not by itself establish a protocol break |
| S1 | Four STS rows are marked as failing (§6) | Exact [row extracts](data/nist-flagged-rows.json), input hashes and source verification | Multiple-testing false alarms are possible; no exploitable bias claimed |
| S2 | Signed average growth and directed girth do not establish the claimed security (§6) | Sign-invariance counterargument, determinant proof and A^q identity | No generic practical length attack asserted |
| I1 | Julia/C serialization mismatch (§1) | Specification p. 5; independent big/little-endian comparison and KAT agreement | This is an interoperability defect; algebraic attacks work under either encoding |
| I2 | Unsupported digest lengths return success and write the full output (§7) | Guard-buffer tests in all four C builds | No out-of-bounds access in the demonstration; actual harm depends on caller allocation |
| I3 | Global table initialization is unsynchronized (§7) | Exact [source locations](PROVENANCE.md) | Source-level C data race; no dynamic failure reproduced |
| I4 | Constant-time behavior is not established (§7) | Message-indexed tables and conditional arithmetic, with source locations | No timing or cache attack demonstrated |

No practical full-parameter collision, distinct second preimage or recovery of a
uniformly random long input from one digest is supplied. A deterministic outer
hash cannot remove collisions already present in the inner matrix product.

**Relation to public comments.** The comparison below concerns
[Saarinen's report](https://ngcc.dev/reports/hash-04.html) and the comments by
[cuihr26, signed "Tsinghua Hash Lab"](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/QNMIAAKIPHG5FEK7QZEE2ZYBOWQHCZUE/),
and [Cryptanalysts001, signed "ISCAS"](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/6LSOFTTMTDWFWWRAZDREDYJNG5NXDVEC/),
in the versions retrieved on 22 September 2026. The analysis and experiments in
this package were complete before the author became aware of those sources;
[PROVENANCE.md](PROVENANCE.md) records the chronology and source hashes.

| Findings | Relationship to the cited sources |
|---|---|
| A1 | The determinant range restriction and generic birthday bounds overlap. The ISCAS comment explicitly avoids a uniformity or mixing assumption. |
| C1–C2 | The attack direction overlaps. The Tsinghua-signed comment reports a toy commuting-pair collision; this package additionally supplies the explicit two-stage subgroup search, twelve complete certificates over 16–28-bit safe primes, and an independent verifier. Full-parameter cost remains heuristic. |
| A2, S2 | The CHAMP-1024 identity example and criticism of the length-attack rationale overlap in part. This report further develops generator-splitting distinctions, sign invariance and directed-girth analysis. |
| I1, S1 | Serialization and flagged statistical rows are shared observations; this package supplies source locations and reproducible evidence. Independent KAT checks are also reported in the thread. |
| P1–P4 | The thread gives a general warning about keyed uses. The explicit prefix/suffix and three-query sandwich MAC forgeries, related-digest recovery and demonstrated short-input preimage search are additional results. |
| I2–I4 | The digest-length, initialization and timing findings are additional to the cited sources. Their evidence limits remain as stated above. |
| A3 | The exact distinguishing predicate and acceptance probability develop a consequence of the shared determinant restriction. |

This comparison identifies overlap and additional detail relative to the cited
sources; it is not a claim of first discovery in the wider literature.
