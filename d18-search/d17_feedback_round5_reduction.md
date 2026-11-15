# Critical perfect matchings: a width reduction and short core certificates

**Result.** Every perfect first matching containing the case-606 critical
edge dc is now excluded at arbitrary even active width. For at most two
A--B gates, [rounds three](d17_feedback_round3_hand.md) and
[four](d17_feedback_round4_hand.md) give hand proofs. For three or more,
this note gives a hand reduction to 1,080 canonical first matchings and
an independently checked, SAT-free arithmetic certificate for them.

The finite verification **is a premise** of the last step. This is a
structured finite-assisted proof, not a completed hand classification of
the three-or-more-cross branch. Its new contraction lemma and full-row
existence lemma are hand results independent of that computation.
The full case-606 hand proof and the full D17/D18 goals remain open.

## 1. Safe contraction of common real partners

Consider a family with five sentinels at every state, on n=2h wires. A
peak is h-3 RR gates. Let M be perfect, and fill the final counted
matching N to be perfect. Then N peaks exactly when it has two SS edges.

An M-edge joining two common real coordinates can be deleted together
with its two coordinates. This lowers every M count and the peak by one.
Its two output types are always real, so deleting their incident N-edges
loses no SS edge. Completing the remaining N matching preserves all its
SS edges, and hence every N-peak. This concerns two layers of type counts;
it does not claim to preserve the sorting function of an entire network.

There is a stronger contraction. Suppose M contains u--r and v--s, with
r,s common real coordinates. Assume u and v are each universally
comparable with type zero, and universally comparable with each other.
Thus each external comparison has a fixed type routing over the family,
and so does the comparison u--v, in either physical orientation.

**External-real contraction lemma.** Replace the two M-edges u--r,v--s by
u--v, and delete r,s. There is a second matching on the reduced family
that preserves peak coverage.

*Proof.* The two old gates retain respectively two, one, or zero RR gates
according as both, one, or neither of u,v is real. The new gate retains
one, zero, or zero. Thus its total loss is at most one, exactly the
decrease in the peak threshold.

Follow the fixed type routings of the old two gates, and delete the two
always-real output tracks from N. This removes no SS edge. Pull the
remaining N edges through the fixed routing of the new comparator u--v,
and complete N to a perfect matching on n-2 wires. Every old SS edge is
preserved. The threshold for a second-layer peak is still two SS edges,
so every old N-peak survives. Both matchings remain ordinary matchings;
orientations in the final counted layer do not affect its RR count. ∎

The same argument works for any fixed odd sentinel count 2t+1, replacing
the second-layer threshold two by t. In all applications here the
variable coordinates are one-sided types {-1,0} or {0,+1}, as required
for their fixed routing against a common real.

## 2. Normalization to 1,080 cases, independent of width

Use the usual signed A fork G={AB,BC,CE,BD} and B family
qab,qbc,qce,rce,qbd. We need only the three B columns qbc,qce,rce.
In them c is a common sentinel, d is real and paired to c by the
critical comparator, and a is always real. The other B coordinates obey

    q <= b <= 0 <= r <= e.

Every pair among the five noncritical B coordinates {a,b,q,e,r} is
therefore universally comparable across these selected states.
The only incomparable A pairs are CD and DE. Across A and B, an
incomparable pair must have the same nonzero sentinel sign, and its B
endpoint cannot be a.

Let C>=3 be the number of A--B gates in the perfect M. The critical gate
uses c,d, so C<=5. Delete all M-pairs of common reals. Any remaining
common real must be paired to a variable coordinate. Apply the external
contraction as follows.

* C=3: two A and two B vertices are noncross. The noncross B vertices
  are either paired together already, or each paired to a common real;
  in the latter case contract them into a B--B edge. Do the same for
  the two A vertices if they are comparable. Thus either both pairs
  are internal, or the A pair is CD or DE and its two common-real
  partners remain.
* C=4: one A and one B vertex are noncross, each paired to a common
  real. If comparable, contract them, yielding C=5. Otherwise the two
  common real partners remain. There are ten possible incomparable
  A/B pairs: four negative and six positive.
* C=5: all variable vertices are cross-paired, so no common-real
  partner remains after deleting the common-real M-pairs.

This leaves the following canonical forms. Common real labels are
interchangeable; a common permutation of all coordinates preserves the
two-layer type-count property by reorienting the first comparators and
absorbing their fixed output swaps into N.

| Width | Cross gates | Remaining form | Number |
|---|---:|---|---:|
| 12 | 3 | one A--A edge and one B--B edge | C(5,2)^2 3! = 600 |
| 14 | 3 | external A pair CD or DE; one B--B edge | 2 C(5,2) 3! = 120 |
| 14 | 4 | one incomparable external A/B pair | 10·4! = 240 |
| 12 | 5 | a bijection between the five A and five noncritical B vertices | 5! = 120 |

No ambient-width cutoff has been assumed: the contractions prove that
these 1,080 forms cover any hypothetical perfect critical cover with
C>=3 at any even width. Contractions use only the selected twelve states;
that suffices, because a cover of all twenty states must cover them too.

## 3. A full row always exists, and it gives only six cores

**Full-row existence lemma.** Every perfect first matching containing dc
has a G-row which misses its first peak in all three selected B columns.

*Proof.* First suppose some A vertex is noncross. If it has degree at
least two in G, at most one incident G-edge can be an M-edge; another
row is outside M and cannot have two cross SS edges. If it is a leaf,
its row works unless that row is an A--A M-edge. In that event its
noncross neighbor has degree at least two, and the previous argument
applies to the neighbor. Thus a noncross A vertex always supplies a
fully required row outside M.

If all five A vertices are crossed, their B partners are distinct. For a
G-row to peak in M, those two partners must be an edge of b--q--e--r.
The fork center B has three neighbors, whereas every vertex of this
B path, including isolated a, has degree at most two. At least one of
the three center rows is therefore fully required. ∎

For a fixed A row, all its A types are constants. Every M-comparison
therefore acts as fixed type routing across the three B columns. Its
transported five-sets have exactly the form

    T+qb, T+qe, T+er,          |T|=3,

with the four path vertices outside T. By the hand path classification
from round three, N contains either er plus a perfect matching of T+q,
or qb plus a perfect matching of T+e. There are exactly six choices,
each consisting of three forced edges.

Once a core K is fixed, let S be any required five-set and write U(K)
for its used endpoints. At most

    edges_of_K_inside_S + floor(|S minus U(K)|/2)     (1)

N-edges can lie inside S. A value below two is an immediate contradiction.
If K already gives one internal edge and exactly two S vertices remain
unused, N must pair those two vertices. These are the only inference
rules in the new certificates.

## 4. Independent arithmetic certificate

[`d17_feedback_round5_certificate.py`](d17_feedback_round5_certificate.py)
generates the canonical forms, chooses a full row, splits its six cores,
and records the inference steps above. It invokes no SAT solver and does
not search arbitrary second matchings.

The separate
[`d17_feedback_round5_check.py`](d17_feedback_round5_check.py) does not
import the generator or any discovery code. It independently enumerates
perfect first matchings at widths twelve/fourteen and filters precisely
the stated canonical forms, checking complete coverage and uniqueness.
For each record it directly replays the signed first matching, verifies
which states require N, reconstructs the exact six initial cores, and
checks every forced edge and final capacity contradiction in (1).

The [certificate](results/d17-feedback-round5-core-certificate.json)
contains 1,080 cases and 6,480 core branches. Of those branches, 4,479
contradict a required set immediately; the other 2,001 use **one** forced
edge and then contradict a required set. No branch needs a longer chain.
The [independent audit](results/d17-feedback-round5-core-check.json)
passed in 0.063 seconds. Generation and checking each had a separate
30-second bound and exited zero; the
[terminal record](results/d17-feedback-round5-certificate-terminal.json)
is saved.

This proves the C>=3 perfect-critical obstruction conditional on the
small finite arithmetic verification. Combining it with the hand C<=2
results excludes all perfect-critical first matchings at arbitrary even
width. Replacing the 1,080-case verification with a symbolic case split
is still a separate open step; no fully hand-classified theorem is
claimed for C>=3.

## 5. Relation to the remaining task

The new external-real contraction is reusable beyond this particular
family. It provides a bounded active width for perfect first matchings
without assuming arbitrary filling or deleting comparators preserves a
cover. The peak loss and the preservation of SS edges are what make
this contraction valid.

The earlier normalization sends a hypothetical case-606 cover to a
perfect or two-idle first matching. The present finite-assisted result
removes the critical perfect branch entirely. Remaining branches include
critical two-idle first matchings with at least two cross gates and
noncritical mixed cases. A pure hand treatment also still needs to
replace the finite classification in Section 4. These are local
structural statements; no new complete D17 or D18 bound follows.

The bounded static SAT probe in `d17_feedback_round5_probe.py` and the
discovery screens `d17_feedback_round5_core_screen.py` and their result
files are retained as feedback, not premises of the independent checker.
All their processes are terminal.
