# The pure two-layer peak screen is exhausted on the D17 cover

**Result.** Every complete-cover case `n17-r0000` through `n17-r0605`
has an explicitly verified pair of matching layers that gives every
nine-real half-blind restriction four RR gates in at least one layer.
The first layer's signed types are transported exactly before the second
count. Thus **none of these 606 cases can be excluded by this pure
two-layer peak condition alone**.

Together with the existing pure obstructions for cases 606,607,608, this
fully classifies that particular relaxation on the 609-case cover. It
does not construct sorter completions, strengthen the known D17 cover
exclusion count, or prove D(17)>=10. It also does not classify stronger
screens that impose additional profile or data-order constraints.

A new hand lemma explains the large collection of survivors: **any three
odd sets admit one matching that attains the maximum possible number of
internal pairs in every set simultaneously**. Consequently, a first
matching that misses the required maximum on at most three restrictions
always extends to a pure two-layer peak cover, regardless of its signed
transport. The lemma works even when the three odd set sizes differ.

## 1. Three odd sets always admit simultaneous maximum pairings

Let R1,R2,R3 be odd-cardinality subsets of any finite wire set. We seek a
matching N with (|Ri|-1)/2 edges inside each Ri. Give each wire its
three-bit incidence signature sigma(v). Add one wire outside all sets
if necessary to make the ambient width even.

First pair wires having the same signature, leaving at most one wire of
each signature. Such pairs cross none of the three sets. Let P be the
set of remaining distinct signatures. The number |P| is even, and

    XOR_{p in P} p = 111,                            (1)

because each Ri has odd size. The XOR of all eight signatures is 000,
so |P| can only be 2,4,6.

* **Two signatures.** They differ by 111. Pair them; this edge crosses
  each Ri once.
* **Four signatures.** Choose any two and pair them. If their difference
  is x, (1) says the other pair's difference is 111 XOR x. Neither
  difference is zero, since the four signatures are distinct. The two
  differences have disjoint coordinate supports whose union is all
  three coordinates. These two edges therefore cross each Ri once.
* **Six signatures.** The two missing signatures are complementary by
  (1). XOR-translate all signatures so the missing pair is 000,111.
  The remaining signatures are 001,010,011,100,101,110. Pair

      001--011, 010--110, 100--101.

  Their differences are respectively 010,100,001, so again each Ri is
  crossed exactly once. Undo the translation, which preserves differences.

Together with the identical-signature pairs, this is a perfect matching
with exactly one boundary edge per Ri. Hence it has (|Ri|-1)/2 internal
edges in every set. If a dummy wire was added, delete its incident edge;
that edge was not internal to any Ri. This proves the lemma. One or two
odd sets are covered too, by repeating sets to make a list of three. ∎

This is a hand argument over the eight possible signatures, not an
enumeration of wire matchings. The independent checker corroborates its
sixteen possible residual signature sets satisfying even cardinality
and (1); the [small parity record](results/d17-feedback-round9-three-set-parity.json)
contains the explicit pairs.

**Sharpness at four sets.** The four triples

    abc, abx, acy, bcz

cannot all contain an edge of one matching. An edge in abc, say ab,
would force cy and cz in the last two relevant triples, a conflict;
the other two choices are symmetric. More generally, add any common
even-sized set C to all four triples. Their six variable signatures are
distinct and odd; five of them already violate the four-state parity
corollary from [round eight](d17_feedback_round8_cut_lemma.md).
Thus these four odd sets still cannot all attain their maximum internal
matching count. Taking |C|=6 gives a sharp example with four nine-sets.

## 2. Consequence for arbitrary signed transport

Suppose a family consists of states with odd numbers of real wires, and
a first matching M already attains the maximum floor(|R|/2) on all but
at most three states. Transport each remaining state through M and
retain its new real-position set. Each set is still odd. Apply the
three-set lemma to choose N attaining its maximum on all of them.

Every state is now covered by M or N. No hypothesis about the sentinel
signs, coincidences between real-position sets, or the position of the
first-layer idle wires is needed. Only the incoming real sets matter
for N's RR counts. The construction permits repeated gates and empty
retained layers, exactly as the pure relaxation does.

Therefore any proof using only this pure two-layer peak relaxation must
show that **every possible first matching leaves at least four
restrictions uncovered**, and then exploit an incompatibility among
their transported real sets. A first matching with at most three
failures is a definitive counterexample to such a universal obstruction.
This applies to potential D18 applications as well, whenever the
required count is the maximum on an odd real set.

## 3. A cheap exact construction from Hamming costs

For an arbitrary collection R1,...,Rm of odd sets, put edge cost

    d(u,v) = number of i for which exactly one of u,v lies in Ri.

After padding by one never-real dummy if necessary, every perfect
matching has total cost at least m: each odd set has an odd, positive
number of boundary edges. A perfect matching has total cost exactly m
if and only if every set has exactly one boundary edge, equivalently
the maximum possible number of internal RR pairs.

This gives a direct search for a static peak layer by minimum-weight
perfect matching. A positive answer needs no trust in the optimizer:
the proposed matching can simply be replayed against all states.
Negative optimizer results were treated as discovery unless supported
by a separate explicit bound.

The cheap initial price screen found thirty families with strict
single-layer obstructions. Its doubled nonnegative vertex prices q(v)
obey q(u)+q(v)>=2 times the number of real sets containing both u,v,
with sum q(v)<8m. The independent checker verifies every such inequality.
These are only static one-layer obstructions, not prefix exclusions.

Minimum Hamming-cost first matchings gave static peak covers for 554
cases. For the other candidate first matchings, we formed the real sets
of just the failed restrictions after exact signed transport and solved
the same matching problem for N. This directly produced pure two-layer
covers for all cases 0 through 603, without SAT. Among these first
matchings, 35 leave one failure, nine leave two, two leave three, and
four leave four; the last four happened also to have a compatible N.

Cases 604 and 605 required different first matchings. Two bounded profile
solves found witnesses that also satisfy the stronger nonemptiness and
nonrepetition conditions. Each completed in under one second. Two other
small probes, at cases 587 and 600, also produced stronger-profile
survivors. All four runs had separate thirty-second wall bounds and
terminal records. No UNSAT conclusion or unchecked proof was used.

## 4. Independent audit of all 606 witnesses

[`d17_feedback_round9_check.py`](d17_feedback_round9_check.py) imports no
SAT solver, matching optimizer, discovery script, or half-blind-family
generator. It independently reconstructs each full nine-real family by
enumerating the 256 choices of one signed sentinel in each of the eight
first-layer pairs, discarding choices with a real-real comparator in
the second prefix layer, and applying that layer by direct comparisons.
It checks repeated real-position masks have the same signed state and
that every family size agrees with the cover record.

For each case 0--605 the checker verifies matching legality, replays both
new layers on every reconstructed state, and verifies that one RR count
equals four. In all it checks **1,907 restriction profiles**. The final
witness collection is only **6,494 bytes**:

[`d17-feedback-round9-all606-covers.json.gz`](results/d17-feedback-round9-all606-covers.json.gz).

Its SHA-256 is
`6ec11ec8065878d5600de80723606789bff06badd6a54e0f1dd6bba6d653fcdd`.
The [independent report](results/d17-feedback-round9-check.json) is
VERIFIED, and binds the checker and witness digests. It also directly
checks the stronger controls at cases 587,600,604,605: each restriction
has nonempty first and second retained layers, at least one four-gate
layer, no L2/L3 repeated gate, and no L3/L4 repeated gate.

The exhaustive cover manifest remains
`711b620bb298deee98e5520595cfb341a13cf3600f4297dd35f3b38cb11d2100`.
The independent check finished in 0.213 seconds under its thirty-second
limit; the [terminal record](results/d17-feedback-round9-check-terminal.json)
is saved. The four SAT controls and all matching/price screens are also
terminal. The pure cover witnesses, rather than solver SAT statuses or
optimizer claims, are the evidence for this result.

## 5. What is exhausted, and what remains useful

The existing universal obstructions for cases 606--608 together with
these 606 positive models settle the **pure two-layer maximum-count
question on the supplied full two-layer nine-real restriction families**.
Another obstruction based only on that same question cannot exclude an
additional complete D17 cover case.

The negative premises here are genuinely pure. Case 606 uses the
[finite-assisted signed-family theorem](d17_feedback_round7_reduction.md);
case 607 uses its [hand signed-family obstruction](fixed-sentinel-obstruction.md).
For case 608, the relevant premise is the **direct fourteen-wire pure
certificate**, not the older `d17_feedback_defects.py` formula with
nonemptiness and nonrepetition assumptions. Its
[encoder](d17_feedback_fourteen.py) uses `first=0`, `adjacent=False`, and
`no_repeat=False`, and adds no retained-layer nonemptiness requirement.
The [verified audit](results/d17-feedback-fourteen-audit.json) and
[DRAT-check manifest](results/d17-feedback-fourteen-main/result/check/certificate.json)
bind the 2,150-variable, 19,412-clause UNSAT formula. The twenty states are
exactly case 608 after deleting its three common negative-sentinel wires
0,3,11; the fixed-sentinel pruning lemma lifts this pure obstruction back
to the seventeen wires.

The new
[binding audit](results/d17-feedback-round9-pure608-binding.json)
reconstructed that signed family independently and rebuilt the direct
encoder's CNF while intercepting solver construction. It is byte-identical
to the already checked CNF, with SHA-256
`afe0be3fae6418512cbc9ed7b0b724158998e59dbf30ce6f957a2d8ed4ede049`.
The current encoder, library, states, proof, and checker hashes also agree
with the old verified manifest. No new SAT or DRAT run was needed; this
binding check finished in 0.156 seconds and is terminal. The classification
therefore retains a checked computational premise for case 608, while
allowing arbitrary first/second matchings, empty retained layers, and
repeated gates throughout the pure question.

This does not rule out stronger profile constraints, other restriction
sizes, additional prefix layers, or a proof that uses actual order
relations among the surviving real values. In particular, the positive
models are not sorters and do not assert that the restrictions can share
a valid sorting suffix. Most pure models were deliberately allowed to
have an empty second retained layer or repeated gates; the separate
stronger controls are limited to the four named cases.

The useful next target is therefore prefix-image containment or rank/order
coupling, rather than another search for a two-layer peak obstruction
inside these same 606 families. A nine-real restriction whose retained
prefix image contains a partial order requiring six further layers would
contradict a five-layer tail, even when its first two RR counts satisfy
all peak conditions. Such an order argument distinguishes actual data
constraints that the present positive count models do not encode.
No additional whole-cover exclusion or global D17/D18 bound is claimed
in this round.
