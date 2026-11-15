# A hand closure of the critical edge with at most one cross gate

**Theorem.** For the case-606 signed family, no two matching layers cover
all states at peak h-3 if the first matching contains the critical B edge
dc and has at most one A--B edge. The active width is any even n=2h>=12,
with an arbitrary even number of common real coordinates. The first
matching can have any size. The labels can have any physical embedding.

This closes a branch left open by the earlier
[row-forcing and normalization arguments](d17_feedback_round2_normalization.md).
It is a hand proof. Tiny SAT probes suggested the local matching lemmas,
but neither those solver results nor the finite scan in the verifier
is a premise. The full case-606 hand proof remains open.

## 1. Three selected columns and a path lemma

Use capitals for the A fork and lower case for B:

    G = {AB,BC,CE,BD},       A-, B-, C+, D+, E+;
    B triples = qab, qbc, qce, rce, qbd,
    q-,a-,b-,c+,d+,e+,r+.

As before, fill the second matching N to be perfect. A five-sentinel
state peaks in N exactly when it contains two N-edges.

Select just the three B columns qbc,qce,rce. In every selected state,
the first comparator dc contains exactly one sentinel, c. After that
comparator, its sentinel has a common output position k. The remaining
B sentinel pairs form the path

    b--q--e--r,       H={qb,qe,er}.                  (1)

All other B--B comparisons have fixed type routing across these columns:
their coordinate functions satisfy q<=b<=0<=r<=e, and a is always real.
Comparisons with a common real also have fixed routing. These routings
can be absorbed into the B labels used below.

**One-row path classification.** Let T be a three-set disjoint from the
four vertices of H. A matching contains two edges in every five-set
T+qb, T+qe, T+er if and only if it contains one of the following cores:

    Q: er and an internal perfect matching of T+q;
    E: qb and an internal perfect matching of T+e.   (2)

*Proof.* There must be an internal T-edge. Otherwise both endpoints of
each H-edge would need distinct partners in T, requiring four partners
in a three-set. Let p be the T-vertex left over. The triples {p,x,y},
xy in H, must each contain a matching edge. If p pairs to q, the edge er
is forced; if it pairs to e, qb is forced. Pairing p to either path
endpoint leaves two incident H-edges to be matched; pairing it outside
H leaves all three H-edges. Both are impossible. This proves (2), and
each displayed core suffices. ∎

**Two incident rows are incompatible.** Suppose k,u,v,w,q,b,e,r are
distinct. No matching has two edges in all six sets

    {k,u,v}+P, {k,u,w}+P,       P in {qb,qe,er}.      (3)

Apply (2) to T={k,u,v} and T'={k,u,w}. If both choose Q, the perfect
four-sets intersect in {k,u,q}; if both choose E, they intersect in
{k,u,e}. A matching internal to both four-sets would have to match their
odd intersection internally. If the choices differ, one fixed B-edge
conflicts with the other row's perfect four-set: er has e inside the
E four-set but r outside, or qb has q inside Q but b outside. ∎

## 2. The lemma survives one transferred B coordinate

There is one additional local pattern, essential for same-sign cross
gates. Start with the first row {k,u,x}+P, P in H. In the second row
{k,u,w}+P, replace one specified B-path coordinate y by x. All eight
original labels k,u,x,w,q,b,e,r are distinct.

**Transfer lemma.** No matching has two edges in all six resulting
five-sets, for any y in {q,b,e,r}.

It suffices to handle y=b and y=q: reversing the path exchanges b with r
and q with e.

For y=b the second path is x--q--e--r. Its alternatives from (2) are

    Q': er and a perfect matching of {k,u,w,q};
    E': qx and a perfect matching of {k,u,w,e}.

Q with Q' gives an odd three-vertex intersection. Q with E' is impossible
because er leaves the E' four-set at e. E with Q' is impossible because
qb leaves the Q' four-set at q. E with E' would match q to both b and x.

For y=q the second path is b--x--e--r, with alternatives

    X': er and a perfect matching of {k,u,w,x};
    E': bx and a perfect matching of {k,u,w,e}.

Q with X' gives the odd intersection {k,u,x}. Q with E' conflicts at e.
E with X' also conflicts at e, since er leaves E's four-set. E with E'
would match b to both q and x. This proves all four transferred cases. ∎

The middle path edge qe is material: deleting its column from (3) leaves
the explicit covering matching ku,qb,er. This positive control prevents
treating two disjoint B edges as an obstruction.

## 3. Exact transport with zero or one cross gate

Let f(V) be the destination of a singleton A sentinel through M. Distinct
A images coincide only at the endpoints of a same-sign A--A gate. For a
G-edge UV outside M, its transported A sentinels occupy f(U),f(V), even
when a B sentinel shares one of their matching blocks: the two sentinels
then occupy both outputs, so the A singleton position remains occupied.

With no cross gate, the B routing is independent of the A row. The same
holds for an opposite-sign cross gate, whose two type functions are
ordered in a fixed direction across all rows and columns. If the cross
gate uses B vertex a, its B endpoint is always real in the selected
columns, so it does not alter any of the path coordinates in (1).

The remaining case is a same-sign cross gate X--y, y in {q,b,e,r}.
Write x=f(X), and let z be its other output. In a row containing X,
the A sentinel stays at x and the variable type of B vertex y is at z.
This remains exact when both inputs are sentinels: both x and z are
occupied. In a row without X, a sentinel from y instead goes to x and z
is real. Thus, relative to a row containing X, a row without X replaces
the one B-path coordinate z by x. All other B coordinates have the same
fixed routing in both rows.

Now take two distinct incident edges in the graph of folded A rows.
If their B routing is common, (3) excludes them. Otherwise one row
contains X and the other does not. Since X has a cross partner, f(X)
cannot equal any other A image; it is the nonshared endpoint of the
first folded edge. The two rows have exactly the transferred form of
Section 2. They too are impossible.

Consequently, any collection of G-rows outside M which require N in all
three selected B columns must fold to a matching. This conclusion is
valid with at most one cross gate, even when the individual A pair is
not forced into N.

## 4. At most one row can be lost to a first-layer peak

Write m=|M|. In every selected column dc hits one sentinel and one real.
For a G-row outside M, its A sentinels cannot form an SS edge. Of the
other four sentinels (two A and two B), a matching with at most one A--B
edge can contain at most one SS edge: two such edges would either pair
the A row internally or require two cross gates. Thus s<=1.

If i is the number of M-idle sentinels, then

    RR_M = m-5+i+s.

Classify the first matching size:

* If m=h, then i=0 and RR_M<=h-4. Every selected state in every G-row
  outside M requires N.
* If m=h-1, there are two idle wires. A peak requires i=2 and s=1.
  Apart from the sentinel in dc, the other two used sentinels must be
  joined by an SS edge. If both idles are A vertices, they determine
  a unique potentially exceptional G-row. If one is A and one B, the
  other used A sentinel must be the A endpoint of the sole cross gate;
  again this determines at most one G-row. Two idle B vertices would
  force the A row itself to be an M-edge, already omitted. An always-real
  idle cannot contribute to i. In every exceptional row, neither A
  endpoint has an A--A partner in M.
* If m=h-2, a peak can touch at most one M-edge. The dc edge already
  uses that allowance, so the other four sentinels must all be idle.
  The four idle wires must therefore be precisely two A and two B
  vertices. The A pair determines one exceptional row, whose endpoints
  are idle and hence have no A--A partners.
* If m<=h-3, the non-RR edge dc gives RR_M<=m-1<=h-4, so no selected
  state peaks in M.

We may therefore discard at most one G-edge E0. If it is discarded,
its endpoints have no A--A partners. Every other G-edge outside M
requires N in all three selected columns.

## 5. The folded fork still has two incident edges

Without E0, use the previously proved
[folded-fork lemma](d17_hand_defects_twelve_cross.md): the G-edges outside
M never fold to a matching under the sign partition {A,B}/{C,D,E}.

When E0 is discarded, its endpoints have no A--A partners. Only the other
three A vertices can contain an A--A gate P. Opposite signs do not merge
images. The only opposite-sign G-edge disjoint from another G-edge is
P=BD, E0=CE; deleting these still leaves incident edges AB,BC. If P is
not a G-edge, deleting it changes no row. With same signs, the following
table exhausts P disjoint from E0 and displays distinct incident edges
after folding; identified letters have the same image.

| P | E0 | Incident surviving folded edges |
|---|---|---|
| AB | CE | BC, BD |
| CE | AB | BC, BD |
| CE | BD | AB, BC |
| CD | AB | BC, CE |
| DE | AB | BC, CD |
| DE | BC | AB, BD |

If P is absent, deleting any one fork edge plainly leaves two incident
edges. Thus in every case the fully required rows still fold to a
nonmatching graph. Section 3 forbids that graph. This proves the theorem. ∎

## 6. Checks, additional motif, and remaining scope

[`d17_feedback_round3_verify.py`](d17_feedback_round3_verify.py) imports no
solver. It checks the exact one-row classification on 232 local
matchings, the ordinary and four transferred two-row patterns on 764
matchings apiece, all 26 local A matchings, and the 16 applicable
deleted-edge configurations. As a separate corroboration, it checks all
61,512 fourteen-wire first matchings containing dc and at most one
cross gate: the exceptional-row classification, existence of incident
folded rows, exact signed transport, and their incidence signatures
always agree with one of the five proved local patterns. This took
1.17 seconds. The [record](results/d17-feedback-round3-verified.json)
and [terminal status](results/d17-feedback-round3-verify-terminal.json)
are saved. The proof's arbitrary-width statement follows from the local
matching-block arguments, not from extrapolating that finite check.

An additional small obstruction emerged from the feedback. Let K be a
common two-set, X and Y disjoint two-sets, and u,v,z three other distinct
vertices. Require two matching edges in each of

    K+u+X, K+u+Y, K+v+X, K+v+Y, K+z+{x,y},
    x in X, y in Y fixed.

Give the two K vertices prices 2 and 3, each X/Y vertex price 1, and all
others price zero. Every edge's occurrence count is at most its endpoint
price sum, but total price is nine while the five demands require ten.
This is a reusable five-state counting contradiction. It explains the
first zero-full-row example in the round-two note, although the path
lemmas above give the broader branch closure.

The tiny SAT feedback files `d17_feedback_round3_probe.py` and
`d17_feedback_round3_classify.py` are retained as discovery records.
Their bounded runs finished in under a second. They are not used by
the final verifier or hand proof.

The remaining case-606 hand gap includes first matchings without dc and
mixed partially required rows, and first matchings with dc and at least
two A--B edges. The earlier normalization still reduces a hypothetical
cover to a perfect or two-idle first matching. In the old critical-perfect
full-row screen, the present theorem closes all 141 one-cross survivors,
leaving 611 previously undecided cases with two or more crosses. Those
counts are bookkeeping, not a proof that any survivor is feasible.
No full case-606, D17, or D18 hand theorem is claimed.
