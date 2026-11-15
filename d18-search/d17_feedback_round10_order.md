# An image-rescheduling bound excludes two more D17 cover cases

**Result, conditional on the established H9 theorem.** In a sorting
network on nine reals of depth at most seven, the first layer has at
least three comparators. This strengthens the earlier condition that
one of the first two layers has four comparators. The proof uses an
exact four-wire image identity, not just retained-gate counts.

Adding this necessary condition to the existing D17 profile screen
excludes complete-cover cases **604 and 605**. Both exported UNSAT
proofs passed independent DRAT checks. Cases 600 and 587 survive the
strengthened condition. These are two additional conditional cover
exclusions, not a global D17 lower bound or a fully hand-derived result.
Full H9 remains an explicit computer-assisted premise of the new
first-layer bound; its hand coverage is incomplete.

Separately, all 606 cases that survived the pure peak relaxation also
have positive witnesses for the old nonempty/nonrepeat profile screen.
Thus the new first-layer bound is a material strengthening of that
screen, not a repair of its old normal forms.

## 1. The four-wire N-poset has two schedules

Let P be the set of all four-real vectors satisfying

    x0 <= x2,  x0 <= x3,  x1 <= x3.                 (1)

Its Hasse graph is the four-vertex N-shaped path. The two-layer prefix

    C = 01 | 02 13

has image exactly P. The three inequalities follow from its comparisons.
Conversely, for any target x in P, give C the input

    (x0,x3,x2,x1).

Its first pair is already ordered because x0<=x3. The second layer
returns x0,x2 on wires 0,2 and x1,x3 on wires 1,3, hence the target.

The alternative prefix

    D = 01 23 | 12

has image exactly the poset

    y0 <= y2,  y1 <= y2,  y1 <= y3.                 (2)

For sufficiency, input (y0,y2,y1,y3), whose first-layer pairs are already
ordered. Its middle comparator returns y1,y2. The fixed permutation

    x = (y1,y0,y3,y2)

maps (2) to (1). Thus a disconnected four-wire component using one
first-layer and two second-layer gates can be replaced by a component
using two first-layer and one second-layer gate, preserving its entire
real image up to a fixed output relabeling.

The statement allows arbitrary embeddings and comparator orientations.
Within a one-then-two path, name the first comparator's outputs a<=b
and the two free inputs c,d. The later comparisons are the pairs (a,c)
and (b,d); relabel their min/max outputs to obtain C. Any reversed
orientations change only those fixed output labels. This concerns an
independent interaction component, so it preserves the product image
with all other components.

### A purely hand forbidden product image

The already hand-proved H9 prefix

    01 23 45 | 03 46 57

from [the commuting-restriction proof](../depth-hand-proofs/h9_feedback_commute.md)
has image P times P times one free singleton, up to a fixed permutation.
On wires 0,1,2,3 its two-then-one component compares opposite-role
endpoints and is a copy of (2); on 4,5,6,7 it is C. Therefore **the
product of two N-posets and one independent real cannot be sorted in
five further layers**. This particular image obstruction uses the
existing hand proof, not full computed H9.

As in the accepted signed-poset lifting theorem, a fixed input-track
permutation is absorbed into generalized suffix comparators and then
untangled. Layer counts are preserved. A fixed final output permutation
must be the identity on strictly increasing inputs once all gates are
ascending. Thus the image obstruction applies to arbitrary wire labels.

## 2. A seven-layer nine-real sorter starts with at least three gates

Suppose its first matching M has at most two gates. Write N for its
second matching, which has at most four.

If |N|<=3, both first layers have at most three comparators, contradicting
H9. This is the branch where we explicitly use the full established
computer-assisted theorem; we do not assert that all such prefixes have
already been covered by the current hand cases.

Now let |N|=4. A gate of N whose endpoints are unused by M commutes past
all of M and can be moved to the first layer.

* If |M|=0 or 1, at least four or two N-gates respectively avoid all
  M endpoints. Move enough of them backward to obtain two layers of
  at most three gates each. H9 excludes the resulting sorter.
* If |M|=2 and some N-gate avoids M, move one backward. This gives
  layer sizes (3,3), again forbidden by H9.
* Otherwise |M|=2 and every one of the four N-gates touches M's four
  used wires. Because N is a matching, each touches exactly one such
  wire and one previously unused wire. The interaction graph consists
  of two independent one-then-two four-wire paths and one singleton.
  Their image is P times P times a singleton, forbidden by the pure
  hand product obstruction above. Equivalently, replace one path by
  its two-then-one image-equivalent schedule, obtaining a (3,3) prefix
  and applying H9.

These cases exhaust N, proving |M|>=3. Empty layers and repeated gates
cause no exception: the statement of H9 permits them, and commuting
disjoint gates preserves the network function. In the last case a
repeated M/N gate would touch two M endpoints, forcing another N-gate
to avoid M, contrary to that case's hypothesis. ∎

For a signed restriction that blinds the first two layers of a
depth-nine seventeen-wire sorter, exactly nine free real tracks remain
in a seven-layer pruned network. Untangling preserves the first retained
layer's size, so original layer 3 must contain at least three RR gates
on **every** such restriction.

## 3. Exact change to the D17 encoding

The new encoder
[`d17_feedback_round10_profile.py`](d17_feedback_round10_profile.py)
is the accepted defect encoder with one substantive change per state:

    old: at least one RR gate in the first retained layer;
    new: at least three RR gates in the first retained layer.

The new constraint is a sequential-counter cardinality encoding on the
36 eligible first-matching edges joining the state's nine real inputs.
It adds 99 auxiliary variables per state and replaces one old OR clause
by 168 cardinality clauses. For sixteen states the net changes are
1,584 variables and 2,672 clauses. No change is made to the peak-four
choice or to exact signed transport.

Both first two prefix layers come directly from the existing complete
saturated/reflected cover. The later layers are arbitrary matchings;
they are not filled and have no ending normal form or self-duality
condition. A layer-3 gate repeating layer 2, and a layer-4 gate repeating
layer 3, are forbidden by the usual deletion of an immediately repeated
comparator. Deleting such later redundant gates preserves the fixed
two-layer prefix, so this normal form is compatible with the cover.

The H9 peak condition still requires four RR gates in M or N. A
second-layer nonemptiness condition is added only if a candidate fails
it. Both new refutations finish in the first iteration, before any such
refinement: they are UNSAT even with that second nonemptiness condition
omitted. Thus no unproved extra condition is needed for these results.

## 4. Checked new exclusions and positive controls

| Cover case | Components | Variables / clauses | Solve | DRAT check |
|---|---|---:|---:|---:|
| 604 | H01212, S211212, S211212 | 3,778 / 26,672 | 4.18 s | 3.21 s |
| 605 | H01221, S121221, S121221 | 3,778 / 26,576 | 4.47 s | 3.36 s |

Each solve and each checker had a separate ten-second wall bound and
finished with exit zero. Results and proof manifests are in
[`case604`](results/d17-feedback-round10-first3-case604/result.json) and
[`case605`](results/d17-feedback-round10-first3-case605/result.json), with
their `result/check/certificate.json` manifests. The solver proofs are
independently checked; interpretation of the added cardinality condition
uses the preceding theorem and retains its explicit H9 premise.

Cases 600 and 587 satisfy the strengthened screen in about 0.03 seconds
each. Their new models have at least three first-layer RR gates on every
restriction, a nonempty second layer, no immediate gate repeats, and a
four-gate peak in at least one layer. These are profile witnesses, not
sorting suffixes.

For context, the old screen itself is now exhausted on cases 0--605:
matching repair supplied 603 old-profile witnesses in under a second,
and bounded SAT produced the remaining three, at 476,477,478, each in
under 0.2 seconds including startup. Those models satisfy the original
nonempty/nonrepeat conditions. The old SAT controls at 604/605 therefore
do not conflict with the new UNSAT results: their weak first-count
requirement has been replaced by the necessary lower bound three.

The independent replay checker
[`d17_feedback_round10_check.py`](d17_feedback_round10_check.py) passed in
0.40 seconds ([report](results/d17-feedback-round10-check.json)). It
checks the four-wire image identities and all 945 possible four-gate
second matchings, replays all 1,907 signed restrictions across the 606
old-profile witnesses, and rebuilds both new CNFs without running a
solver. The rebuilt bytes match the independently checked CNF/proof
manifests, including source and checker hashes. Among the 606 old
witnesses, 600 already satisfy the new first-count bound; only witnesses
476,477,478,600,604,605 needed replacement or refutation. The remaining
tests at 476,477,478 all returned positive witnesses in under half a
second including startup, with separate ten-second limits. Together
with the replacement at 600, these give checked positive witnesses for
**every case 0--603**, covering all 1,875 restrictions. They are saved in
[`first3-all604.json.gz`](results/d17-feedback-round10-first3-all604.json.gz)
with SHA-256 `f8451fba48322139ddbddfa17feabfea704ed6e28917686cae193ca2b3f88187`.
Thus this strengthened screen adds exactly the two exclusions 604/605
to the earlier three; it yields no further exclusions among 0--603.
No new run was needed for adjacent cases such as 603, whose existing
witness passed. The final checker replay took 0.38 seconds. All solves,
proof checks and replay processes are terminal.

## 5. Proof scope and next step

The N-poset image identity and its two-component forbidden product are
hand statements with explicit inverses and an already hand-proved H9
class. The universal first-layer lower bound uses full H9 in its other
branches. The new cover exclusions are therefore conditional on the
same established computer-assisted H9 result used by the earlier three
exclusions, together with the checked new finite certificates. They do
not claim a completed hand proof of H9 or D17.

This is a concrete order constraint that pure peak counting missed:
an apparent (2,4) peak can have an image-equivalent (3,3) realization,
which cannot admit the required tail. The shared physical layer 3 must
avoid that failure simultaneously for every restriction, and cases
604/605 cannot satisfy the resulting first-count constraints together
with H9's peak condition. Further tests should build on such real-image
or rescheduling consequences, rather than revisit the exhausted old
peak screen.
