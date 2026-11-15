# A hand closure of perfect critical matchings with two cross gates

**Theorem.** In the case-606 signed family, a perfect first matching that
contains the critical B edge dc and exactly two A--B comparators cannot
cover all twenty states at peak h-3 together with a second matching.
The active width is any even n=2h>=12, with any even number of common
real coordinates, in any physical embedding.

Together with [round three](d17_feedback_round3_hand.md), this excludes
every perfect critical first matching with at most two cross gates.
The theorem is a hand argument using small exact matching classifications.
The [checker](d17_feedback_round4_verify.py) uses no SAT. The full case-606
hand proof is still open.

## 1. Setup and which rows need the second layer

Continue to use

    A fork G={AB,BC,CE,BD},       A-,B-,C+,D+,E+;
    B triples qab,qbc,qce,rce,qbd, with q-,a-,b-,c+,d+,e+,r+.

Select the three B columns qbc,qce,rce. The comparator dc contains one
sentinel in each selected state. After it, a common sentinel k remains,
and the other B sentinel pairs form the path b--q--e--r. The coordinate
a is real in all selected columns.

Complete the second matching N to be perfect. It must have two SS edges
in every selected state that misses its first-layer peak.

Let X,Y be the two crossed A vertices. In a G-row outside the first
matching M, a first-layer peak requires two SS edges. Since dc contains
just one sentinel, both SS edges must be A--B gates. This is possible
only in the row XY. Discard that G-row if it exists, whether or not it
actually peaks. Every other G-row outside M requires N in all three
selected columns.

The discarded edge has no A--A partner at either endpoint. The folded-fork
and deleted-edge lemmas from round three therefore say that the remaining
folded rows contain two distinct incident edges. Here f(V) denotes the
singleton image of an A vertex; only same-sign A--A gates identify images.

## 2. Exact classification with two transferred coordinates

The ordinary and one-coordinate-transfer two-row obstructions were proved
in round three. With two cross gates, the only genuinely new pattern is
when the two incident rows each contain a different crossed A vertex,
and both cross gates have equal sentinel signs at their endpoints.

Use eight distinct positions k,u,x,y,q,b,e,r. The two A rows are xu and
uy. Let the B partner of x be p, and the B partner of y be t. In the
first row the type at t moves to y; in the second row the type at p moves
to x. All other path coordinates are unchanged. Each row therefore has
three five-sets: its A pair and k, together with the three edges of its
modified B path.

If either cross gate has opposite signs, its routing is fixed across
both rows and only the earlier zero/one-transfer lemma is needed. A
cross gate using a also causes no transfer of a path coordinate. Thus
the new case has distinct p,t in {q,b,e,r}.

Recall the exact one-row path classification: for a common triple T,
the three demands T+qb, T+qe, T+er force either

    Q: er plus an internal perfect matching of T+q,
    E: qb plus an internal perfect matching of T+e.

Apply this to each modified path. Up to reversing the path, there are
four positions for p,t. The following table lists the compatible choices
of Q/E for the first and second rows:

| Crossed B partners p,t | Q,Q | Q,E | E,Q | E,E |
|---|---|---|---|---|
| q,b | impossible | impossible | impossible | impossible |
| q,r | impossible | impossible | impossible | impossible |
| q,e | impossible | impossible | inner core I | impossible |
| b,r | impossible | outer core O | impossible | impossible |

Reversal covers the pairs e,r and b,e. The two surviving cores are

    I: qb, er, and an internal perfect matching of {k,u,x,y};
    O: ku, xq, ye.                                  (1)

This is an exact hand classification, not just a necessary test. Here
are the four checks behind the table.

* For q,b, the Q four-sets intersect in the odd triple {k,u,x}. Each
  mixed choice has a fixed edge leaving the other four-set. With E,E,
  the first fixed edge qy leaves the second four-set at y.
* For q,r, the Q fixed edges are ey and er, which conflict. Q,E has
  the fixed edge xb leaving the first four-set at x. E,Q has er leaving
  the first four-set at e. E,E would match b to both q and x.
* For q,e, Q,Q conflicts at r, Q,E has xb leaving the first four-set,
  and E,E conflicts at b. The surviving E,Q choice fixes qb and er;
  the two four-sets are both {k,u,x,y}, giving exactly I.
* For b,r, Q,Q conflicts at e, E,Q has qb leaving the second four-set,
  and E,E conflicts at q. In Q,E the fixed edges ey and qx force those
  pairs inside the two four-sets; both then force ku. This is O.

The cores in (1) are real boundary controls: each covers all six local
five-sets of its corresponding pattern. Thus the two-row argument alone
cannot discard these cases; another fork row is needed.

## 3. The A fork leaves only one exceptional arrangement

For any incident pair of required folded rows, identical cross membership
gives the ordinary two-row obstruction. Membership differing in one
crossed vertex gives the single-transfer obstruction. Membership differing
in both vertices gives the table above. The crossed A vertices have
distinct images from all other A vertices, so in the latter case they
are precisely the two nonshared endpoints x,y.

If X,Y have the same sign, a double transfer uses B partners of that same
sign. The only available same-sign path pairs are q,b or e,r; these are
impossible by the table. Therefore only opposite-sign A pairs need
further discussion. Their six possibilities reduce as follows:

| Crossed A vertices | Required incident rows giving an earlier obstruction |
|---|---|
| A,C | BC and CE have identical cross membership; f(B) and f(E) have opposite signs and cannot merge. |
| A,E | Use AB and either BC or BD outside M. At least one exists, since BC and BD share B. Their cross membership differs only at A. |
| B,C | AB and BD both contain B and not C; their other endpoints A,D have opposite signs. |
| B,D | AB and BC both contain B and not D; A,C have opposite signs. |
| B,E | AB and BC both contain B and not E; A,C have opposite signs. |
| A,D | If BC is outside M, AB and BC differ only at A. Thus BC must belong to M. |

Every displayed row is outside M and is not the discarded XY row. A
crossed vertex cannot be an A--A partner, so its image cannot merge with
the other endpoint in the A,E or A,D cases. This justifies the distinct
folded edges asserted in the table.

Only the following arrangement remains:

    crossed A vertices A,D;          BC is an M-edge.          (2)

The two required center rows AB and BD have the form of Section 2.
Their B partners must therefore be the inner pair q,e or the outer
pair b,r, with A matched to the negative member and D to the positive
member. Every other sign or path configuration was already excluded.

Write x=f(A), y=f(D), u=f(B), v=f(C), w=f(E). The A--A gate BC has
opposite signs, so u and v are distinct. Vertex E is paired to a common
real: all other A vertices are used, and another A--B gate would exceed
two crosses. Thus v,w are distinct from each other and lie outside
{k,u,x,y,q,b,e,r}. At width twelve (2)
is consequently impossible already; larger even widths permit it but
the next argument excludes it.

## 4. The remaining CE row contradicts both cores

The CE row is outside M and contains neither crossed A vertex. Its
three selected states therefore require N.

**Inner pair q,e.** In this row q transfers to x and e transfers to y.
The sentinel sets are

    {k,v,w,x,b}, {k,v,w,x,y}, {k,v,w,y,r}.           (3)

Core I contains qb,er and a perfect matching of {k,u,x,y}. In the first
set of (3), b is matched outside to q; of the four-set, only k,x occur.
The only possible two internal edges are therefore kx and vw. The last
set similarly forces ky and vw, since r is matched outside to e. A
matching cannot contain both kx and ky. Contradiction.

**Outer pair b,r.** Its core O is ku,xq,ye. In the middle B column qe,
the CE sentinel set is

    {k,v,w,q,e}.

Each of k,q,e is already paired outside this set, respectively to u,x,y.
Only v,w can supply an internal edge, so two internal edges are
impossible. This completes the final arrangement and proves the theorem. ∎

## 5. Scope and independent checks

All transport arguments distinguish fixed routing, same-sign collision,
and opposite-sign separation inside disjoint matching blocks. They do
not depend on numeric wire order. Extra common real coordinates only
change h and supply distinct external partners; the first-peak test and
the requirement of two SS edges in a perfect second matching are
unchanged. This gives the stated arbitrary-embedding and even-width
scope without extrapolating a finite computation.

The verifier checks each of the six exact double-transfer classifications
on all 764 partial matchings of their eight local positions. It then
corroborates the hand classification for all 3,600 perfect fourteen-wire
first matchings containing dc and exactly two cross gates. The local
two-row obstructions cover 3,588; six realize the inner exceptional core
and six the outer core. Direct signed replay of CE excludes every one of
those twelve, using the exact upper bound from the already forced edges.
The [audit](results/d17-feedback-round4-verified.json) passed in 0.08
seconds, with a [terminal record](results/d17-feedback-round4-terminal.json).
No solver was invoked.

The earlier critical-perfect full-row screen had 222 undecided matchings
with two cross gates; this theorem closes that entire class, leaving 389
of its old undecided cases with three or more cross gates. These counts
do not assert feasibility. Remaining hand gaps include critical perfect
matchings with at least three crosses, critical nonperfect matchings with
at least two crosses, and the noncritical mixed branches. No full case-606,
D17, or D18 hand theorem is claimed here.
