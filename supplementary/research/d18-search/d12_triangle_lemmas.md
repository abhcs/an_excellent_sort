# Four short obstructions for transported sentinel triples

**Proof status.** A later [complete hand classification](fixed-sentinel-obstruction.md)
proves the twelve-wire obstruction without the finite scan. The results
below retain the four-triple explanation extracted from that scan and
provide independent, reusable hand lemmas.

All 3,957 labelled four-triple cores in the twelve-wire scan have one
of the four forms below, up to a common relabeling. Each form has a
short hand proof. The classification of the scan output is finite;
the lemmas themselves apply to any width and any matching.

Write `abc` for the three-element set `{a,b,c}`. A matching **hits** a
triple when it contains a pair inside that triple. All differently
named letters within a row of the following table denote distinct
vertices. Vertices outside those displayed are unrestricted.

| Type | Four triples | Nonzero vertex prices | Sum of prices |
|---|---|---|---:|
| I: two forks | `xab, xac, xde, xdf` | `p(x)=p(a)=p(d)=1` | 3 |
| II: opposite arms | `axz, byz, cxy, dxy` | `p(x)=p(y)=1`; `p(z)=p(a)=p(b)=1/2` | 7/2 |
| III: triangle with three attachments | `abc, abx, acy, bcz` | `p(a)=p(b)=p(c)=1` | 3 |
| IV: common vertex over a four-cycle | `xab, xac, xbd, xcd` | `p(x)=3/2`; `p(a)=p(b)=p(c)=p(d)=1/2` | 7/2 |

**Four-triple lemma.** No matching hits all four triples in any row.
In fact every matching hits at most three of them.

## 1. Why the prices prove the lemma

For a family of triples, give each pair `uv` weight `w(uv)` equal to
the number of triples containing it. A matching has at most one pair
inside any one triple. Consequently

```
number of triples hit = sum_{uv in the matching} w(uv).
```

This is equality: shared pairs count every triple they hit, and no
triple is counted twice. Thus maximum-weight matching is an exact
formulation of the triple-hitting question, rather than a relaxation.

If nonnegative vertex prices satisfy `w(uv) <= p(u)+p(v)` for every
pair, then a matching's weight is at most the sum of all prices.
Disjoint matching edges spend each vertex's price at most once.

The table supplies such prices. Unlisted vertices have price zero.
The only checks with pair weight two are:

* Type I: `xa` and `xd`, each with endpoint-price sum two.
* Type II: `xy`, with endpoint-price sum two.
* Type III: `ab`, `ac`, `bc`, each with endpoint-price sum two.
* Type IV: `xa`, `xb`, `xc`, `xd`, each with endpoint-price sum two.

Every other occurring pair has weight one and endpoint-price sum at
least one. In type II the potentially tight pairs `az,bz` each have
two half-price endpoints. In type IV the four cycle pairs each have
two half-price endpoints. All non-occurring pairs have weight zero.

The sums are either three or seven halves, both below four. The number
of triples hit is an integer, so it is at most three. This proves all
four templates without a case enumeration. □

## 2. Two additional reusable graph formulations

**Common-vertex criterion.** Let all triples have the form `xuv`, where
`uv` ranges over the edges of a graph `G` not containing `x`. A matching
hits every triple if and only if `G-v` is a matching for some vertex
`v` of `G` (also allowing the empty graph).

*Proof.* If `x` is paired to `v` in `G`, every edge of `G` avoiding `v`
must itself belong to the matching; those triples cannot use `x`.
If `x` is idle or paired outside `G`, all of `G` must be a matching,
which also implies the stated condition. Conversely, if `G-v` is a
matching, take its edges together with `xv`. Every edge of `G` either
meets `v`, whose triple is hit by `xv`, or belongs to `G-v`. □

This immediately explains type I (`G` is two disjoint two-edge paths)
and type IV (`G` is a four-cycle). Removing one vertex cannot turn
either graph into a matching. It also gives obstructions with more
than four triples whenever no vertex deletion makes `G` a matching.

**Linear-family bound.** Suppose a family of `k` triples shares no pair
between distinct triples, and its union has fewer than `2k` vertices.
No matching hits them all. Each chosen pair could hit only one triple,
so hitting all `k` requires `k` disjoint pairs and at least `2k` vertices.
This is another width-independent obstruction, although it is not
needed for the four types found in the twelve-wire scan.

## 3. Relationship to the twelve-wire restriction family

The [fixed-sentinel note](fixed-sentinel-obstruction.md) gives twenty
signed twelve-wire states, each with nine reals and three sentinels.
For a fixed first matching `M`, keep only states with at most three
real-real gates in `M`, and transport their signs through `M` exactly.
Their three sentinel positions are the triples to be hit next.

The next matching `N` may safely be completed to a perfect matching:
it is the last counted layer, so filling it cannot decrease any count
or affect a later transport. In a perfect matching on twelve wires,
a nine-real state has four real-real gates precisely when two of its
three sentinels are paired. Hence a four-triple template among the
transported states proves that this particular `M` has no covering `N`.

The scanner found a four-triple obstruction for every one of the
140,152 possible first matchings, including partial matchings. Its
3,957 distinct labelled cores classify as follows:

| Type | Distinct labelled cores | First matchings assigned that type |
|---|---:|---:|
| I | 1,187 | 8,162 |
| II | 299 | 3,772 |
| III | 834 | 30,501 |
| IV | 1,637 | 97,717 |
| Total | 3,957 | 140,152 |

These counts come from
`results/d12-triangle-scan-four-cores.jsonl`. The universal choice of
four states still rests on the finite scan; the four lemmas replace
the matching search at its leaves with explicit inequalities. No
claim is made here that the four templates classify every possible
four-triple obstruction in arbitrary hypergraphs.

## 4. Independent verification

`d12_triangle_lemmas_classify.py` classifies cores by their vertex-to-triple
incidence masks, trying the 24 permutations of the four triples. A
multiset of these masks determines the hypergraph up to vertex
relabeling, so this is exact isomorphism classification.

`d12_triangle_lemmas_verify.py` independently verifies all four explicit
templates and all 3,957 labelled cores. For each labelled core it
assigns prices from its vertex degrees, then checks every pair-price
inequality and the strict total-price bound directly. Independently,
a subset dynamic program computes the exact maximum number of triangles
hit by a matching, obtaining three for every core. A separate
degree-preserving bijection search supplies an explicit isomorphism
for every core, recorded in
[`results/d12_triangle_lemmas_catalogue.jsonl`](results/d12_triangle_lemmas_catalogue.jsonl).
Neither check relies on the incidence canonicalizer or a SAT solver.
The verifier also transports
all twenty signed states through each saved representative `M` and
checks that every core triple comes from a state missed by `M`.

For each template, deleting any one of its four triples admits a
matching hitting the other three. The verifier stores those sixteen
positive controls and checks them directly. The audit is
[`results/d12_triangle_lemmas_verification.json`](results/d12_triangle_lemmas_verification.json).

```sh
python3 d18-search/d12_triangle_lemmas_verify.py
```

The verifier binds its input-core file, signed-state file and own
source by SHA-256. The repeated first-matching counts in the core file
are reported, not independently re-enumerated by this verifier.
