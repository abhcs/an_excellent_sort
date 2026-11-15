# A compact exact encoding of the two-layer rank-capacity test

The [fixed-last-matching theorem](fixed-ending-block-capacity.md) reduces
rank-set reachability to cancellation of reciprocal block demands. For
adjacent last-layer blocks, it admits a particularly small clause encoding.

Consider three consecutive blocks A,B,C; a missing end neighbor contributes
zero. Their lengths are one or two. Let L(X),R(X) count wires of X whose
required intervals extend left or right of X. No wire may extend both
ways, since its interval would meet three blocks. Write b=|B|. The block
capacity inequality is

```
max(0,R(A)-L(B)) + max(0,L(C)-R(B)) <= b-L(B)-R(B).
```

Because L(B)+R(B)<=b, this is equivalent to the three inequalities

```
R(A)+R(B) <= b,
L(B)+L(C) <= b,
R(A)+L(C) <= b.
```

Indeed max(0,x)+max(0,y)=max(0,x,y,x+y); substituting the two differences
and canceling terms gives precisely these three bounds. The fourth bound
is the already known nonnegativity of the number of free wires in B.

Each sum involves at most four Boolean demands and b is at most two.
An at-most-b constraint is therefore expressed simply by forbidding each
(b+1)-subset. No cardinality auxiliary variables are needed.

## Conditional clauses

Let e_i denote the last-layer edge(i,i+1). A length-two block is present
exactly when its e_i is true. A singleton v is present exactly when both
adjacent edge variables are false; a missing boundary edge is false.
Each local clause is conditional on its named blocks being present.

Use L[c,k]=(lo_c>=k) and U[c,k]=(hi_c<k). For a block[start,end], a wire's
left and right demands are respectively not L[c,start] and not U[c,end+1].
The encoder imposes:

* no simultaneous left and right demand for any wire of a present block;
* under a present pair of consecutive blocks A,B, each interval at B
  starts at or after A's first position;
* under present B,C, each interval at B ends at or before C's last position;
* the three conditional cardinal bounds above, using only the blocks
  whose demand counts occur in each bound.

Together these are necessary and sufficient for a common preceding
matching to realize all the rank intervals with the chosen adjacent last
matching. The proof is the exact block-capacity theorem; this formulation
eliminates the explicit preceding-layer edge variables from the rank
condition. It does not claim that reachability sorts the actual data.

[rank_block_capacity_cnf.py](rank_block_capacity_cnf.py) adds no variables.
After removing tautologies and duplicate clauses it adds498 clauses at
width13 and758 at width18. The original adjacent-edge matching clauses
and endpoint definitions are assumed already present.

## Why this remains necessary with a fixed sorting prefix

A sorting completion may be taken with an adjacent final layer by the
nonredundant-last-layer theorem, Lemma3 of
[Codish, Cruz-Filipe and Schneider-Kamp, Sorting Networks: the End Game](https://arxiv.org/html/1411.6408#S3).
Redundant comparisons preserve the computed values when removed. If the
fixed prefix itself contains redundant comparisons, retain that original
prefix after finding the normalized ending: its cut image is unchanged.
Thus this normalization does not require changing the prefix under test.

The endpoint variables may overapproximate actual rank intervals. Every
true sorting completion can choose its exact intervals and its normalized
last matching, so it satisfies all new clauses. An UNSAT result can rule
out a completion; SAT remains only a necessary-condition witness.

## Independent controls and scope

[The clause verifier](rank_block_capacity_cnf_verify.py) fixes exact
interval vectors and adjacent S, evaluates the CNF, and independently
enumerates all preceding matchings P to compare forward cones. It checks
all such assignments at widths3 and4 and deterministic samples at5 and6,
13,488 comparisons in total. It does not invoke SAT or the DP implementation.
The known eighteen-wire depth-eleven sorter also passes the fully fixed
network control in the synthesis worker.

The first two D18 four-prefix experiments both reached their30-second
caps. The complete-cover D13 tests are recorded separately. These
experiments change the representation of an existing necessary condition;
no measured speedup or completed lower bound is inferred from a timeout.
