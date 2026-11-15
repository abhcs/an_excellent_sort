# Exact two-layer sorting from four local output tests

Let X be the complete binary image of a fixed comparator prefix. We seek
two remaining layers P,S, where P is arbitrary and S is an adjacent
matching. For x in X, let k be its number of zeros and let y=P(x).

The ending sorts x exactly when

* y(c)=0 for c<k-1, and y(c)=1 for c>k;
* if (k-1,k) is absent from S, also y(k-1)=0 and y(k)=1.

At k=0 or n the all-equal input is already fixed. At every other k,
weight conservation and the first line force the middle pair to contain
one zero and one one. If S contains its edge, it sorts that pair. Every
other S edge joins positions whose forced values agree. This proves both
directions, including when S has idles. No penultimate span assumption
is needed for this equivalence.

## Direct substitution into clauses

Write z_c for the cut-state Boolean variable, g_ij for a penultimate edge,
and e_k for the last edge (k-1,k). For each wire c let H_c be the
disjunction of all incident penultimate gates. Its active output modes are

    idle: not H_c, output z_c;
    min:  g_cj with c<j, output z_c AND z_j;
    max:  g_ic with i<c, output z_i OR z_c.

For each required output bit b, put the negation of its mode guard into
the clause. Also put e_k into the clause when c is k-1 or k. Substitute
the appropriate Boolean expression for the output:

| Output mode | Require zero | Require one |
|---|---|---|
| Idle z | not z | z |
| Minimum u AND v | not u OR not v | u, and separately v |
| Maximum u OR v | not u, and separately not v | u OR v |

This adds no simulation variables. Valid matching constraints ensure
exactly one output mode is active at each wire. The idle clause uses
the positive incident-gate disjunction; a comparator clause uses -g.
These are the formulas implemented by the root-owned
[two_layer_data_ending.py](two_layer_data_ending.py). They are exact data
sorting conditions, unlike the rank-cone relaxation.

## Four-valued profiles for a fixed cut

For a fixed X, precompute the output of each possible P mode at each
wire c. A mode is impossible if some k-zero input gives the wrong bit
away from positions k-1,k. Otherwise record:

* LEFT if some input with k=c has output zero at c;
* RIGHT if some input with k=c+1 has output one at c;
* FREE if neither event occurs.

If both LEFT and RIGHT occur, the mode is impossible because S cannot
use both edges incident to c. LEFT requires (c-1,c), RIGHT requires
(c,c+1), and FREE imposes no S edge. Thus each penultimate gate has two
fixed endpoint labels in {FREE,LEFT,RIGHT,IMPOSSIBLE}; an idle wire has
one such label. Finding P,S reduces exactly to matching these local
labels. This formulation uses the actual Boolean states, not just
independent attainable rank intervals.

## A linear finite-state algorithm after preprocessing

Temporarily require every P edge to have span at most three. Scan the
wires from left to right. Immediately before wire i, remember:

1. P edges crossing the boundary before i;
2. whether S contains (i-1,i).

Crossing P edges can only have relative endpoints

    (-3,0), (-2,0), (-2,1), (-1,0), (-1,1), (-1,2).

Their matching subsets number exactly fifteen: one empty subset, six
one-edge subsets, seven two-edge subsets, and one three-edge subset.
Including the S bit gives at most thirty states per boundary.

If i is already the right endpoint of a remembered P edge, its P mode
is determined. Otherwise choose i idle, or pair it with one of i+1,
i+2,i+3 that is not already reserved. Choose whether S uses (i,i+1),
subject to its matching condition, and check the precomputed profile
at i. Delete the completed P edge, shift the remaining crossing pattern,
and retain one predecessor for each resulting state. At the final
boundary require the empty crossing pattern and a zero S bit.

All constraints on a processed wire are discharged when it leaves the
boundary. Its future effect is exactly the remembered crossing edges
and S bit. Therefore merging equal boundary states loses no completion.
Conversely, every surviving path constructs two valid matching layers
which pass all output profiles, hence sort X. This proves exactness
under the span bound. There are at most eight transition choices per
state. Decision and reconstruction take O(n) time and storage after
preprocessing; using explicit input bit arrays, the profiles take
O(n|X|) time because only seven P modes per wire need evaluation.

For X that is an actual full comparator-prefix image, the span bound
loses no sorting completion. Delete redundant comparisons from a
hypothetical completion. The nonredundant ending has adjacent S and
P edges joining adjacent S blocks, hence span at most three; see Lemma 3
and Lemma 5 of
[Sorting Networks: the End Game](https://arxiv.org/html/1411.6408#S3).
Deleting redundant fixed-prefix gates does not change its image, so the
original fixed prefix can be retained. No assumption of perfect layers
or a particular S tiling is needed.

The implementation [d13_feedback_round9_data_dp.py](d13_feedback_round9_data_dp.py)
therefore gives an exact two-layer completion algorithm for a fixed
comparator prefix at arbitrary width. It is not a compact symbolic
encoding for an unknown prefix: its precomputed profiles must be
recomputed when the cut changes.

## Essential scope distinction and controls

The clause substitution is exact for any correctly weighted cut family
and arbitrary P. The bounded-span DP is exact for that restricted P
class on any family, and is complete for unrestricted P only when the
prefix normal-form theorem applies. These scopes must not be confused.

For example, on six wires take all sorted binary inputs and also the
input 100000 (wire zero has the lone one). P=05 with empty S sorts this
family. A span-three P followed by adjacent S cannot move that one from
wire zero to wire five. The bounded DP correctly rejects it. This is
not the complete image of a comparator prefix to which the normal-form
argument applies.

The [direct verifier](d13_feedback_round9_data_dp_verify.py) compares the
DP with all P and adjacent S on small actual prefix images, checks this
scope counterexample, replays every returned sorter, audits the fifteen
boundary patterns, and tests a 10,000-wire all-FREE profile control. No
SAT solver or external optimization routine is used.
