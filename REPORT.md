---
title: "CHAMP: technical assessment of the submitted specification"
subtitle: "Independent cryptographic review · Version 1.0.1"
author: "Mounir IDRASSI ([mounir@amcrypto.jp](mailto:mounir@amcrypto.jp))"
date: "22 September 2026"
lang: en
---

**Scope and version.** This report assesses the supplied ten-page *CHAMP Algorithm Specifications*, its four C implementations, test vectors and statistical reports. All references to specification sections and pages concern that document. Its SHA-256 is recorded in the source inventory and in the references below.

A distinct twelve-page [author-hosted preprint](https://shpilrain.ccny.cuny.edu/Cayley%20hash%20paper.pdf), retrieved on 21 September 2026, cites Mullan–Tsaban in §6.2. The supplied ten-page specification does not. The criticism here concerns the absence of an analysis of the subgroup strategy for the implemented determinant-2 pair, not a claim that the authors have never cited that work. This report is not a comprehensive review of the separate preprint; both document hashes are recorded in [PROVENANCE.md](PROVENANCE.md).

**Independent preparation.** This review's analysis and experiments were completed independently of [Saarinen's report](https://ngcc.dev/reports/hash-04.html) and comments signed [Tsinghua Hash Lab](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/QNMIAAKIPHG5FEK7QZEE2ZYBOWQHCZUE/) and [ISCAS](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/6LSOFTTMTDWFWWRAZDREDYJNG5NXDVEC/). The author learned of these sources on 22 September 2026, after completing the review and reproducibility package. Their citations acknowledge overlap. The subgroup method is credited to Mullan–Tsaban in §2.

**Additional contributions.** Relative to the cited sources, the independently developed additions are the explicit two-stage subgroup search with twelve verified reduced-parameter collision certificates (§2); demonstrated prefix/suffix and three-query sandwich MAC forgeries, and related-digest recovery (§4); a 40-bit preimage recovery using full CHAMP-1024 parameters (§5); and digest-length, initialization and timing findings (§7). The determinant bound, collision-search direction, identity example, serialization mismatch, statistical rows and KAT checks overlap with the cited analyses; see [FINDINGS.md](FINDINGS.md).

**Recommendation.** The submission does not presently justify adoption as a general-purpose cryptographic hash. The main concerns are an applicable subgroup collision-search strategy missing from the security analysis, complete forgery of several naive keyed constructions, substantial restrictions on digest use, and unsupported security arguments. The specification and implementations also disagree on serialization, and the statistical reports do not support the statement that every test passed.

The evidence has important limits: this assessment demonstrates full-parameter forgeries against specified MAC constructions and recovery of a short preimage, but **does not exhibit a practical full-parameter collision, a distinct second preimage, or recovery of a uniformly random long message from one digest**. Collision-cost projections below identify their assumptions. The supplied specification does not assign explicit numerical work factors to each security property; this report does not infer such claims from digest size alone.

## 1. Construction and independently checked implementation behavior

Write

$$
A=\begin{pmatrix}-2&1\\4&-3\end{pmatrix},\qquad
B=\begin{pmatrix}-5&2\\-6&2\end{pmatrix},\qquad
M(x_1\ldots x_n)=G_{x_1}\cdots G_{x_n},
$$

where $G_0=A$, $G_1=B$, and arithmetic is modulo $p$. CHAMP-512 uses $p=2^{128}-15449$; CHAMP-1024 uses $p=2^{256}-36113$. Both generators have determinant 2. The digest is $H(X)=E(M(X))$, where $E$ inverts each nonzero entry, leaves zero unchanged, and serializes the entries in column order. On canonical field encodings, $E$ is a publicly invertible bijection. Let $D=E^{-1}$.

An independent model reproduced all 4,097 short-message vectors for each variant and agreed with both the reference and optimized C implementations: 8,194 vectors checked against two implementations apiece. Eight large all-zero/all-one vectors were independently checked by matrix exponentiation. The large DRBG-expanded and million-iteration loop vectors were not rerun in this assessment. [Reproduction code and coverage](REPRODUCING.md), [run transcript](evidence/reproduce-full.log).

The Julia listing on PDF p. 5 writes each field element in big-endian byte order. All four C implementations and the KATs use little-endian byte order. Section 5 does not resolve that choice explicitly. This is an interoperability defect: even the one-bit message `1` yields different byte strings. The findings below apply under either convention; the demonstrations use the C/KAT convention.

## 2. A subgroup collision-search strategy

Mullan and Tsaban give a subgroup-based approach to short collisions in matrix homomorphic hashes. Their general-case square-root estimate is heuristic. It is materially more relevant than inferring an attack merely from membership in a previously studied family. [Mullan–Tsaban, §4](https://arxiv.org/abs/1306.5646).

For CHAMP's implemented pair, the following adaptation works directly with determinant-2 matrices; no conversion of unequal-length collisions from an $SL_2$ construction is needed. Put

$$
P=\begin{pmatrix}1&2\\2&3\end{pmatrix},\quad
P^{-1}AP=\begin{pmatrix}-4&1\\2&-1\end{pmatrix}=C,\quad
P^{-1}BP=\operatorname{diag}(-1,-2)=F.
$$

These are integer identities and hold at both full parameter sets. Conjugation preserves products and collisions.

First find a positive bitstring $w$, containing a zero, whose conjugated product $T$ is upper triangular. This can be searched by matching projective points

$$
M(u)^{-1}\infty=M(v)\infty,
$$

where products in this paragraph use $C,F$, and $\infty=[1:0]$. A match makes $M(uv)$ upper triangular. Only the search computation uses inverses: the output word is the ordinary positive word $uv$. There are $p+1$ projective points. If the sampled point distributions mix adequately, two lists of approximately $\sqrt p$ words suffice.

Now multiply the two upper triangular matrices $F,T$. For

$$
R=\begin{pmatrix}a&b\\0&d\end{pmatrix},\qquad
S=\begin{pmatrix}e&f\\0&h\end{pmatrix},
$$

direct multiplication gives

$$
RS=SR\quad\Longleftrightarrow\quad f(a-d)=b(e-h).
$$

For nonzero off-diagonal entries, matching the field value $(a-d)/b$ therefore finds commuting products. Diagonal matrices commute with $F$ and can be handled separately. A birthday search on these codes costs approximately $\sqrt p$ samples under a corresponding mixing assumption. Expand the two resulting words back into original CHAMP bitstrings $r,s$, and verify $rs\ne sr$. The resulting collision satisfies

$$
M(rs)=M(sr),\qquad |rs|=|sr|.
$$

This construction automatically respects the determinant constraint. It produces an actual collision, not an identity word or a relation requiring inverse letters in the message.

Our [implementation](code/subgroup.py) produced twelve distinct equal-length collision pairs at reduced field sizes, using safe primes congruent to 7 modulo 8. The three runs at each size used the following total sample counts across the two stages:

| Field bits | Prime | Total samples, three seeds |
|---|---:|---:|
| 16 | 65,063 | 639; 667; 634 |
| 20 | 1,048,343 | 1,691; 3,770; 2,357 |
| 24 | 16,774,679 | 11,880; 9,224; 8,007 |
| 28 | 268,434,263 | 30,771; 33,867; 39,728 |

Every pair was recomputed with the original generators and finalization. A separate verifier recomputed the complete products over the integers before reducing modulo each prime; it also confirmed that these particular pairs do not collide at either full parameter set. Complete messages, digests, seeds and timings are retained in [collision certificates](data/collisions.json). These examples test the mechanism; they do not prove its asymptotic cost or full-size mixing assumptions.

With words of $O(\log p)$ symbols at each stage, the demonstrated approach suggests $O(\sqrt p\log p)$ field work, approximately $\sqrt p$ stored records up to polynomial factors, and messages of $O((\log p)^2)$ bits. The leading exponential work factors would be **$2^{64}$ for CHAMP-512 and $2^{128}$ for CHAMP-1024**, subject to those assumptions. These are neither measured full-parameter attacks nor established lower bounds. The authors should address this strategy explicitly before assigning security levels.

## 3. What follows unconditionally from the determinant

For an $n$-bit message,

$$
\det M(X)=2^n\pmod p.
$$

Consequently, outputs at a fixed length occupy at most

$$
S=|SL_2(\mathbb F_p)|=p(p^2-1)
$$

matrices, regardless of which subgroup the generators produce. A proof that the generators generate a large group would not imply that every matrix in this coset occurs at a particular length.

| Result | CHAMP-512 | CHAMP-1024 | Interpretation |
|---|---:|---:|---|
| Fixed-length range bound | Less than $2^{384}$ | Less than $2^{768}$ | Exact counting bound |
| Classical birthday collision search | $O(2^{192})$ | $O(2^{384})$ | Generic baseline; choose a domain with at least $2S$ messages |
| Some equal-length collision must exist by | 384 input bits | 768 input bits | Pigeonhole principle; does not locate the pair |
| Subgroup collision search | About $2^{64}$ | About $2^{128}$ | Leading exponential factors only; mixing assumptions from item 2 |

The first three rows are independent of the subgroup heuristic. The birthday row assumes sampling at a length with at least $2S$ distinct possible messages and discarding repeated inputs; it is not a bound for a nearly injective short-message domain. The pigeonhole lengths are 384 and 768, since the range sizes are already strictly smaller than the corresponding powers of two.

Let $q=(p-1)/2$. Proof-enabled primality checks confirmed that both $p,q$ are prime, and excluded every larger candidate safe prime at each size. Since $p\equiv7\pmod8$, 2 has order $q$. Thus a collision implies

$$
|X|\equiv |Y|\pmod q.
$$

This is a valid and useful exclusion of different-length collisions within a range of width less than $q$. It does not address same-length collision search.

Two corrections are needed in the specification's statements on PDF pp. 4–5. Equality gives $2^{|X|-|Y|}=1$; allowing $\pm1$ is an unnecessarily weak condition, rather than a contradiction. An identity word has length divisible by $q$, not necessarily equal to $q$ or exactly $2^{255}$.

For CHAMP-1024, $A^q=I$ and $q=2^{255}-18057$. The symbolic messages $\epsilon$ and $0^q$ therefore contradict the literal assertion of no different-length collisions with difference less than $2^{255}$. Matrix exponentiation verifies the identity; the enormous message has not been expanded, and this is not a practical attack. The correct threshold is $q$.

The two variants must also be distinguished. At 256 field bits, $\operatorname{ord}(A)=q$ and $\operatorname{ord}(B)=2q$. At 128 field bits, 17 is a quadratic **nonresidue**, $A$ is nonsplit, and $A^q\ne I$, while $\operatorname{ord}(B)=2q$ still holds. The alternative matrix with trace 5 has the same discriminant 17 and the same splitting distinction. Arguments requiring split generators therefore need separate treatment at the two sizes. [Parameter proofs and transcript](evidence/parameters.log).

The determinant also exposes length modulo $q$. If the length lies in a known interval of width $L<q$, bounded discrete-log methods recover it in $O(\sqrt L)$ group operations, with an appropriate time–memory tradeoff. Testing a proposed length takes a modular exponentiation. Unbounded exact length recovery does not follow. Length hiding is an application requirement, not a universal hash-function requirement.

## 4. Exact failures of particular keyed constructions

The public combination rule is

$$
H(XY)=E(D(H(X))D(H(Y))).
$$

For a naive prefix MAC $t=H(Km)$, one known message–tag pair reveals an equivalent key matrix:

$$
L=D(t)M(m)^{-1}=M(K).
$$

For any chosen replacement $m'$, the attacker returns $E(LM(m'))$. This is universal message forgery after one observed tag, without recovering the key bits or knowing their length. It works for replacements of the same length, so requiring a fixed message length does not fix this construction. A suffix MAC $H(mK)$ fails similarly by multiplying by $M(m)^{-1}$ on the left.

Adding a fixed secret suffix as well as a prefix is insufficient. Suppose decoded tags have the form $T(m)=L M(m)R$. Query tags for $\epsilon,0,1$. Then

$$
T(0)T(\epsilon)^{-1}=LAL^{-1},\qquad
T(1)T(\epsilon)^{-1}=LBL^{-1}.
$$

Multiplying these known conjugated generators according to a new message and then multiplying by $T(\epsilon)$ produces its valid tag. These attacks were checked against all four shipped C implementations. These constructions are assessed as potential uses of CHAMP, not as MAC schemes expressly proposed in the specification. The results are not an analysis of HMAC or every possible keyed construction.

For public digests, if $H(X)$ and $H(Xb)$ are both disclosed, then

$$
D(H(X))^{-1}D(H(Xb))=G_b.
$$

This recovers the appended bit exactly at any prefix length. The demonstrations recover all 5,000 bits from 5,001 consecutive digests in the independent model and check recovery of bit 5,000 using each C implementation. This identifies a confidentiality hazard **when such related digests are published**. Streaming computation itself does not require publishing intermediate digests. This attack therefore does not refute the distinct single-digest prediction claim in §7.1(2); that claim still needs a precise input distribution and security experiment.

Public digest combination also does not, by itself, break commitment binding or file integrity against a protected digest. Changing a commitment value is not opening the same commitment two ways. Recomputing a digest for a modified file does not make it equal an authenticated original digest. Any claimed protocol failure must specify what the adversary may change and what the verifier trusts.

## 5. Short-input recovery and preimage-search bounds

For a target matrix $T$ known to hash an $m$-bit input, split a candidate as $uv$, with lengths as close as possible to $m/2$. Store $M(u)$, and look up

$$
T M(v)^{-1}.
$$

This finds an $m$-bit preimage using $O(2^{m/2})$ stored values and operations up to polynomial factors. It works directly modulo $p$; no lifting to integers or assumption about entry growth is required. Our independent implementation recovered a 40-bit input from its CHAMP-1024 digest in about 6 seconds on the recorded environment. That timing describes this run, not a universal practical cutoff. A second demonstration succeeds after integer wrap at a reduced prime. [Transcript](evidence/reproduce-full.log).

The distinction from exhaustive guessing is significant: a generic random hash of a uniformly chosen 40-bit input normally requires searching roughly $2^{40}$ possibilities. Nevertheless, this example does not recover arbitrary 128-bit or long high-entropy inputs in practical time.

Integer exposure is a separate observation. Recovering centered matrix entries exposes the exact integer product only when all original entries lie in $[-\lfloor p/2\rfloor,\lfloor p/2\rfloor]$. Random samples cannot establish a universal no-wrap threshold. In particular, all-zero inputs leave this interval at **59 bits for CHAMP-512 and 117 bits for CHAMP-1024**, providing a worst-case counterexample to any larger universal centered-lifting threshold. Exposure of a matrix is also not automatically efficient recovery of its word factorization.

Two further distinctions are essential:

- A preimage algorithm may return the original message. It is not a second-preimage attack unless it finds a different message. All 4,096 twelve-bit messages have distinct products at both full parameter sets in our exhaustive check; the meet-in-the-middle search in that domain returns the original. The determinant also excludes different feasible lengths for a second preimage of these targets.
- A saturated $O(\sqrt S)$ target-preimage estimate needs sufficiently long halves and suitably spread forward/backward distributions, so that sampled lists intersect at the target. Range cardinality alone does not prove this estimate for every length or target. A toy success does not supply the missing hypothesis.

Quantum estimates need a specified resource model. In particular, the two split searches form a claw-finding problem on domains of size about $2^{m/2}$. Applying Tani's algorithm yields $O(2^{m/3})$ quantum queries to these product functions, with reversible evaluation and substantial quantum storage requirements. This is an inference from that algorithm, not a tested quantum implementation. [Tani, Corollary 9](https://arxiv.org/abs/0708.2584). Standard BHT collision estimates also require their oracle and balance assumptions to be stated. [Brassard–Høyer–Tapp](https://arxiv.org/abs/quant-ph/9705002). No optimal quantum security level is established here.

## 6. Statistical appearance, security arguments, and graph terminology

A single digest at a known length admits a strong structural test: reject noncanonical field words, decode, and test determinant $2^n$. CHAMP always passes. A uniformly random $4b$-bit string passes with probability exactly

$$
\frac{p(p^2-1)}{2^{4b}}\approx 2^{-b},\qquad b=\operatorname{bitlength}(p).
$$

Thus statistical test-suite success would not make these digests behave as uniform random outputs. A three-query concatenation test is also possible; conditional on two valid decoded outputs, matching their encoded product in a fresh random $k$-bit oracle response has probability $2^{-k}$. These properties prevent directly transferring a random-oracle argument without examining its use of the hash. They do not imply that every protocol with a random-oracle proof is insecure.

The supplied NIST reports themselves contain four marked failures:

| Report | Line | Marked result |
|---|---:|---|
| Primary pair, 512-bit digest | 156 | NonOverlappingTemplate, 95/100 |
| Primary pair, 1024-bit digest | 63 | NonOverlappingTemplate, 94/100 |
| Primary pair, 1024-bit digest | 123 | NonOverlappingTemplate, 95/100 |
| Alternative pair, 512-bit digest | 186 | RandomExcursionsVariant, 56/60 |

Exact filenames, source hashes and the four flagged rows are recorded in the [source inventory](PROVENANCE.md) and [row extracts](data/nist-flagged-rows.json). The two primary-pair reports state a minimum acceptable ordinary-test count of approximately 96/100. The authors should reconcile these records with the claim that all tests passed. Some failures are expected when many statistical tests are applied; their presence alone does not prove an exploitable bias. More fundamentally, statistical tests cannot replace cryptanalysis. [NIST SP 800-22 Rev. 1a](https://csrc.nist.gov/pubs/sp/800/22/r1/upd1/final).

Testing 100 streams of $10^6$ bits uses 12.5 MB. This is compatible with generating at least 100 MB and testing a subset. The exact generated amount, tested subset, counter encoding and testing procedure should be documented.

The length-attack defense on PDF p. 7 does not establish resistance. A large canonical representative of $2^{-1}$ says little about whether applying the **correct** inverse factor recovers a smaller integer predecessor. Nor does the sign of an average-matrix eigenvalue control the norm of an individual product. Replacing both generators by their negatives changes an $n$-factor product only by $(-1)^n$, leaving every absolute-entry norm unchanged, while reversing the signs of the average matrix's eigenvalues. Furthermore, $\mathbb E[M_n]=((A+B)/2)^n$ concerns signed entries, not $\mathbb E[\|M_n\|]$, typical growth, or a predictor's success probability. The displayed plots do not supply those missing analyses.

The term *girth* must be defined. A positive collision gives two directed paths with a common endpoint, but closing one path by the reverse of the other uses inverse edges. It bounds a cycle in the underlying undirected graph, not necessarily a directed identity cycle. Indeed, for the CHAMP-1024 primary pair the directed girth is exactly $q$: determinants rule out shorter positive identity words, and $A^q=I$ supplies one. This can coexist with same-length collisions forced by counting at 768 bits. Neither a large directed girth nor a counting upper bound for a different graph resolves the actual collision-search problem.

The integer-lifting discussion on PDF p. 6 also needs care with signed entries. Two different integers can both have absolute value less than $p$ and still be equal modulo $p$: 1 and $1-p$ are an example. A sufficient no-aliasing condition is that each coordinate lies in a common interval of width less than $p$, such as the centered interval used above. Freeness over the integers and a valid coordinate bound are separate requirements for such a modular collision exclusion.

A bounded search without an integer relation does not prove freeness. Conversely, lack of a freeness proof is not itself a collision attack. A credible security analysis must address the actual parameters and message domain.

## 7. Implementation and feature claims

All four `CryptHash` implementations ignore `digest_len_bits`. For example, asking the CHAMP-1024 implementation for 512 bits still returns success and writes 1,024 bits. A guarded-buffer test confirms this behavior without making an out-of-bounds access. The API should reject unsupported lengths and document output capacity.

All four implementations lazily initialize global byte tables using an unsynchronized ready flag. Concurrent first calls can race on these shared objects under the C memory model. This is a source-level finding, not a reproduced erroneous digest. Constant tables or properly synchronized initialization would remove that concern.

The implementation is not established to be constant-time. Its memory accesses use message bytes as table indices, and arithmetic contains data-dependent control flow. A public exponent fixes an exponentiation schedule, not the timing of every arithmetic operation. Hash inputs may be confidential in some applications. No timing or cache attack is demonstrated here. Implementations intended for confidential inputs need a separate side-channel assessment.

Streaming without knowing the final length is already supported by SHA-family hashing: complete blocks can be processed as they arrive and padding added at the end. CHAMP's public digest-combination rule is a different functionality. The feature comparison in §§2 and 4 should distinguish them. [FIPS 180-4, §5.1](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf).

The paper's own Table 1 reports lower single-thread throughput than SHA-512; exploiting more cores is a separate resource comparison. No new throughput benchmark is claimed here. Breaking public homomorphism is not a necessary condition for collision resistance, and conventional streaming or parallel hashing does not inherently require publishing a composable final digest.

**Requested revisions before reconsideration.** State separate collision, preimage and second-preimage targets; specify input distributions, message limits and classical/quantum resource models; address the subgroup strategy and its mixing assumptions; formalize the single-digest bit-prediction claim; limit proposed uses to analyzed constructions; correct the determinant statements and serialization; reconcile the statistical reports; and repair or document the API and concurrency behavior. Any revised finalization must be analyzed as part of the construction: simply hashing the matrix again cannot remove collisions already present in the matrix product.

The accompanying [reproduction guide](REPRODUCING.md) maps the computations to source code, complete collision certificates and recorded transcripts. The [source inventory](PROVENANCE.md) identifies the exact reviewed inputs and version boundaries. The [findings index](FINDINGS.md) separates algebraic results, experiments, projections and source-level observations.

**AI-use disclosure.** Moonshot AI's kimi-k3 was used for the main review. OpenAI's GPT-6 Astra was used for polishing and preparing the publication package, including additional technical analysis, cross-checking of claims, and development of reproducibility code. Mounir IDRASSI is responsible for the final report and its conclusions.

**License.** Copyright © 2026 Mounir IDRASSI for the original contributions. This report and its original results are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The accompanying code is licensed under the [MIT License](LICENSE). Third-party material retains its existing terms; see [LICENSING.md](LICENSING.md) for the scope.


## 8. References and reproducibility

1. CHAMP submitters. *CHAMP: Cayley HAshing with Matrix Products — Algorithm Specifications*. Supplied ten-page specification, undated. Reviewed file: `CHAMP Algorithm Specifications.pdf`. SHA-256, split over two lines for readability:

   ```text
   c1201fe48fe45033c9a97e39ff83928e
   683ac1d69703ec31987752f6f7dfaa69
   ```

2. Alexander Demin, Alexey Ovchinnikov and Vladimir Shpilrain. *CHAMP: Cayley HAshing with Matrix Products*. Distinct twelve-page [author-hosted preprint](https://shpilrain.ccny.cuny.edu/Cayley%20hash%20paper.pdf), retrieved 21 September 2026. Version identification only; see the scope note above.

3. Ciaran Mullan and Boaz Tsaban. *SL2 homomorphic hash functions: Worst case to average case reduction and short collision search*. [arXiv:1306.5646v3](https://arxiv.org/abs/1306.5646v3), 23 December 2015, especially §4. Journal DOI: [10.1007/s10623-015-0129-8](https://doi.org/10.1007/s10623-015-0129-8).

4. Seiichiro Tani. *Claw Finding Algorithms Using Quantum Walk*. [arXiv:0708.2584](https://arxiv.org/abs/0708.2584v2), version 2, 3 March 2008, Corollary 9. *Theoretical Computer Science* 410(50), 5285–5297 (2009). DOI: [10.1016/j.tcs.2009.08.030](https://doi.org/10.1016/j.tcs.2009.08.030).

5. Gilles Brassard, Peter Høyer and Alain Tapp. *Quantum Algorithm for the Collision Problem*. [arXiv:quant-ph/9705002](https://arxiv.org/abs/quant-ph/9705002), 1997. *LATIN 1998*, LNCS 1380, 163–169. DOI: [10.1007/BFb0054319](https://doi.org/10.1007/BFb0054319).

6. NIST. *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*. [SP 800-22 Rev. 1a](https://csrc.nist.gov/pubs/sp/800/22/r1/upd1/final), 2010. DOI: [10.6028/NIST.SP.800-22r1a](https://doi.org/10.6028/NIST.SP.800-22r1a).

7. NIST. *Secure Hash Standard*. [FIPS PUB 180-4](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf), August 2015, §5.1. DOI: [10.6028/NIST.FIPS.180-4](https://doi.org/10.6028/NIST.FIPS.180-4).

8. Mounir IDRASSI. *CHAMP: technical assessment of the submitted specification*, accompanying reproducibility package, version 1.0.1, 22 September 2026. The archive contains the independent model, reduced-parameter search, separately implemented certificate verifier, parameter proofs and transcripts. SHA-256 file checksums accompany the release; they establish file integrity, not authorship or cryptanalytic correctness.

9. Markku-Juhani O. Saarinen. *[CHAMP (hash-04)](https://ngcc.dev/reports/hash-04.html)*. ngcc.dev, 21 September 2026; retrieved 22 September 2026.

10. cuihr26 (signed "Tsinghua Hash Lab"). *[Re: Round1: Public Comment: CHAMP](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/QNMIAAKIPHG5FEK7QZEE2ZYBOWQHCZUE/)*. CryptHash Forum, 22 September 2026; retrieved the same day.

11. Cryptanalysts001 (signed "ISCAS"). *[Re: Round1: Public Comment: CHAMP](https://list.niccs.org.cn/archives/list/crypthashforum@list.niccs.org.cn/message/6LSOFTTMTDWFWWRAZDREDYJNG5NXDVEC/)*. CryptHash Forum, 22 September 2026; retrieved the same day.
