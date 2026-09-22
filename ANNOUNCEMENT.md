**CHAMP: technical assessment and reproducible evidence**

I am sharing a technical assessment of the supplied CHAMP Algorithm
Specifications, together with independent reproduction code, recorded results and
complete reduced-parameter collision certificates.

The report gives a direct adaptation of the Mullan–Tsaban subgroup strategy to
CHAMP's implemented determinant-2 matrices. Twelve small-field collision pairs
are included and separately verified. Extrapolation suggests leading work
factors of 2^64 and 2^128 for CHAMP-512 and CHAMP-1024, respectively, subject to
explicit mixing assumptions and substantial memory requirements. These are
projections, not measured full-parameter attacks.

The assessment also demonstrates universal forgeries against naive prefix and
suffix MACs, a three-query attack on a naive sandwich MAC, recovery from related
prefix digests, and a 40-bit preimage search using the full CHAMP-1024 parameters.
It identifies an encoding disagreement between the Julia listing and C/KATs,
unsupported security arguments, four flagged statistical-test rows, and API and
initialization issues.

No practical full-parameter collision, distinct second preimage, or recovery of
a uniformly random long message from one digest is claimed. The report distinguishes
the supplied ten-page specification from the separate author-hosted preprint,
which already cites Mullan–Tsaban.

This review's findings, derivations and reproduction experiments were completed
independently of [Markku-Juhani O. Saarinen's CHAMP report](https://ngcc.dev/reports/hash-04.html)
and public comments signed
[Tsinghua Hash Lab](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/QNMIAAKIPHG5FEK7QZEE2ZYBOWQHCZUE/)
and [ISCAS](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/6LSOFTTMTDWFWWRAZDREDYJNG5NXDVEC/).
I became aware of these sources on 22 September 2026, after completing this
review and its reproducibility package, and added the citations to acknowledge
related work identified afterward. The report and findings index distinguish
the overlapping observations from our additional contributions.

The accompanying release, `CHAMP-Review-v1.0.1.zip`, includes the report in PDF,
HTML and editable formats, the evidence and exact reproduction instructions.
The code is licensed under MIT; the report and original results under CC BY 4.0,
with scope and third-party exceptions detailed in [LICENSING.md](LICENSING.md).
I welcome corrections, independent replications, and analysis of the full-size
mixing assumptions, especially from the CHAMP authors.

AI-use disclosure: Moonshot AI's kimi-k3 was used for the main review. OpenAI's
GPT-6 Astra was used for polishing and preparing the publication package,
including additional technical analysis, cross-checking of claims, and
development of reproducibility code. I am responsible for the final report and
its conclusions.

Mounir IDRASSI · [mounir@amcrypto.jp](mailto:mounir@amcrypto.jp)  
22 September 2026
