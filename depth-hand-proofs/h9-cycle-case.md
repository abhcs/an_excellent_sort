# A hand proof for the six-cycle case of (H9)

This closes the class

$$L_1=(0,1)(2,3)(4,5),\qquad L_2=(0,3)(1,4)(2,5)$$

in [the H9 proof](h9.md). No seven-layer sorting network on nine wires
has these first two layers. The proof uses two sentinel placements to
force the next two layers, then a nine-row table of four-sentinel
placements. It uses no SAT result or exhaustive search as a premise.

The general invariant below also applies to other widths. Its application
to this class raises the hand coverage of H9 from 17 to 18 of its 50
second-layer classes. It does not resolve $D(13)$, $D(17)$ or $D(18)$.

## 1. Two sentinel placements move together

Consider two separate runs of the same network. In run $P$, every input
is either a real or $-\infty$; in run $Q$, every input is either a real
or $+\infty$. Only the positions of the sentinels matter, so write every
real as $0$. Let $S_P,S_Q$ be the sentinel supports at some layer boundary,
and let $R_P,R_Q$ be their complements.

**Lemma 1 (disjoint supports).** If $S_P\cap S_Q=\varnothing$, it remains
empty after every later layer. In particular,

$$|R_P\cap R_Q|=n-|S_P|-|S_Q|$$

is invariant.

*Proof.* Each wire has one of three joint types,

$$a=(-\infty,0),\qquad c=(0,0),\qquad b=(0,+\infty).$$

Both coordinates respect the same order $a<c<b$. A comparator therefore
just sorts these three types. No type is created or destroyed. $\square$

**Corollary 2 (odd intersection).** If $R_P$ and $R_Q$ have even sizes
and their intersection has odd size, no matching pairs up both sets.

*Proof.* If a vertex lies in both sets, its partner would also have to
lie in both. The matching would pair up their odd-sized intersection.
$\square$

Here, to *pair up* a set means that every vertex in the set is matched
with another vertex of the same set.

There is a useful extension when the sentinel supports overlap.

**Lemma 3 (intersecting supports).** Add the joint type
$d=(-\infty,+\infty)$. A comparator preserves the multiset of its two
types unless its inputs have types $c,d$, in either order. In that case
its outputs have types $a,b$. Thus in a layer with $h$ such comparisons,

$$|S'_P\cap S'_Q|=|S_P\cap S_Q|-h,\qquad
  |R'_P\cap R'_Q|=|R_P\cap R_Q|-h.$$

If that layer contains $m_P,m_Q$ comparisons between reals in the two
runs, and their numbers of reals are $r_P,r_Q$, then

$$2m_P\le r_P-h,\qquad 2m_Q\le r_Q-h.$$

*Proof.* The types form a diamond: $a$ is below $c$ and $d$, and $b$ is
above both. Only $c,d$ are incomparable coordinatewise, and their
coordinatewise minimum and maximum are $a,b$. Each such comparison
uses a distinct real wire in each run without comparing it to another
real, proving the inequalities. $\square$

Consequently, on an even number of wires, two placements leaving even
numbers of reals can start with an odd intersection by sharing an odd
number of sentinel wires. The odd-intersection obstruction persists
until a $c,d$ comparison changes its parity. A layer containing such a
comparison cannot pair up either real set. This gives a precise extra
event that a larger-case argument could try to force or exclude.

For disjoint supports on even $n$, however, two even real sets have an
even intersection. The direct application of Corollary 2 used below
therefore does not apply to $n=18$. Lemma 3 alone does not close that gap.

## 2. The first two layers of a five-layer six-wire sorter

**Lemma 4.** In a sorting network on six wires with at most five layers,
each of its first two layers has at least two comparators, and at least
one of them has three.

*Proof.* Use the hand results $D(5)\ge5$ and [README Lemma 3](README.md):
five wires cannot be sorted in at most five layers with at most one
comparator in each of the first two layers.

If the first layer has at most one comparator, one sentinel blinds that
layer. The remaining five reals would be sorted in at most four active
layers, contradicting $D(5)\ge5$.

If the second layer has exactly one comparator, choose one of its
endpoints $v$. A single sentinel can stay at $v$ through the first
layer: use $-\infty$ if $v$ is a lower endpoint there, $+\infty$ if it
is an upper endpoint, and either sign if it is idle. The sentinel
blinds the second layer, giving the same contradiction. An empty
second layer gives that contradiction immediately.

If both first layers have at most two comparators, they now have
exactly two each. Their four-element supports intersect. Put a sentinel
on a common vertex, with the sign that keeps it there in the first
layer. It removes a comparator in both layers. By sentinel pruning
and untangling ([README Tool C](README.md)), the five reals give the
sorter forbidden by README Lemma 3. $\square$

## 3. The third and fourth layers are forced

Suppose the specified $L_1,L_2$ extend to a seven-layer sorter. Delete
comparators repeated in consecutive layers: the second copy never
fires. This preserves both specified layers.

Put

$$A=\{0,1,2\},\qquad B=\{3,4,5\},\qquad C=\{6,7,8\}.$$

Take these placements on the original inputs:

* $P$: $-\infty$ on $0,2,4$;
* $Q$: $+\infty$ on $1,3,5$.

Both blind the first two layers. After $L_2$, the sentinel supports are
$A$ and $B$, respectively, so their six-real sets are $B\cup C$ and
$A\cup C$. Lemma 1 keeps their intersection of size three through
every later layer. Corollary 2 says that a layer cannot pair up both.

For each placement, the remaining five layers sort six reals. Lemma 4
says that its real-real counts in $L_3,L_4$ are at least two each, and
at least one is three. Hence one placement has counts $(3,2)$ and the
other has counts $(2,3)$.

We may assume $P$ has count three in $L_3$. To justify this reduction,
if necessary negate all values and relabel the first six wires by
$i\mapsto5-i$, and the last three by $6\leftrightarrow8$. This exchanges
$P$ and $Q$ after $L_2$ and preserves both specified first layers,
including their orientations. Untangle reversed comparators in later
layers as in Tool C. This preserves sorting, layer sizes and counts of
comparisons between reals. It also preserves the absence of consecutive
repetitions: swapping the endpoints of a gate in subsequent layers
cannot turn a different gate into that same gate.

Since $L_3$ pairs up $B\cup C$, the number $k$ of $B$--$C$ edges is odd,
so $k=1$ or $3$. The only comparisons between $Q$'s reals are those
inside $A$ and those inside $C$. Their number is at most

$$1+\frac{3-k}{2}.$$

It must be two. Thus $k=1$ and $L_3$ also has an edge inside $A$.
Relabel the three initially idle wires of $C$ so that the cross edge
ends at $6$ and its other two wires are $7,8$, in increasing order.
This leaves $L_1,L_2$ unchanged and makes every $L_3$ comparator standard.

For some $a\in A$ and $b\in B$, the third layer is therefore

$$L_3=(A\setminus\{a\})(B\setminus\{b\})(b,6)(7,8),$$

where a two-element set in parentheses denotes its comparator.

After $L_3$, $P$'s real set remains $B\cup C$, while $Q$'s is
$A\cup\{b,7,8\}$: its sentinel at $b$ moved to $6$. The fourth layer
pairs up the latter set. Its comparisons between $P$'s reals can only
be one edge inside $\{b,7,8\}$ and one inside its complement
$\{6\}\cup(B\setminus\{b\})$. Both must occur to give count two.

The first edge cannot repeat $(7,8)$, so it is $(b,y)$, with
$y\in\{7,8\}$. The second cannot repeat the edge $B\setminus\{b\}$,
so it is $(6,z)$, with $z\in B\setminus\{b\}$.

To finish pairing up $Q$'s reals, $L_4$ pairs the other $C$ wire $y'$
with one wire $x'$ in $A$, and pairs the two remaining $A$ wires.
That internal edge cannot repeat $A\setminus\{a\}$, so it is $(a,x)$
for $x\in A\setminus\{a\}$. Thus

$$L_4=(a,x)(x',y')(b,y)(6,z),$$

where $\{x,x'\}=A\setminus\{a\}$ and $\{y,y'\}=\{7,8\}$.
This derives the entire family: nine choices of $(a,b)$ and two choices
each of $x,y,z$.

## 4. Nine rows finish the proof

In the table, $+i$ and $-i$ mean $+\infty$ and $-\infty$ on original
input $i$. The other five inputs are arbitrary reals. In every row,
$z$ is unrestricted, and so are $x,y$ unless a condition specifies them.
The last column counts comparisons between reals in $L_1,L_2,L_3,L_4$.

| Row | $(a,b)$ | Further condition | Sentinels on original inputs | Counts |
|---|---|---|---|---|
| 1 | $a=0,\ b\in\{3,4\}$ | any | $+0,+1,-2,-4$ | $(0,0,1,1)$ |
| 2 | $a=1,\ b\in\{4,5\}$ | any | $+0,-1,-2,+4$ | $(0,0,1,1)$ |
| 3 | $a=2,\ b\in\{3,5\}$ | any | $-0,-1,+2,+4$ | $(0,0,1,1)$ |
| 4 | $(0,5)$ | $(x,y)=(2,7)$ | $+0,-1,-2,+4$ | $(0,0,1,1)$ |
| 5 | $(0,5)$ | $(x,y)\ne(2,7)$ | $+0,-2,+4,+7$ | $(0,1,0,1)$ |
| 6 | $(1,3)$ | $(x,y)=(2,7)$ | $+0,+1,-2,-4$ | $(0,0,1,1)$ |
| 7 | $(1,3)$ | $(x,y)\ne(2,7)$ | $+0,+1,-2,+7$ | $(1,0,0,1)$ |
| 8 | $(2,4)$ | $(x,y)=(1,7)$ | $+0,+1,-2,-4$ | $(0,0,1,1)$ |
| 9 | $(2,4)$ | $(x,y)\ne(1,7)$ | $+0,-1,+4,+7$ | $(1,0,0,1)$ |

To check the table, replace reals by $0$ and sentinels by $\pm1$.
The six distinct placements, in their order of first appearance above,
have these states after $L_2$:

$$
\begin{array}{c|c|c}
\text{first row using placement}&\text{state after }L_2&\text{counts in }L_1,L_2\\
1&(0,-1,-1,1,1,0,0,0,0)&(0,0)\\
2&(-1,0,-1,0,1,1,0,0,0)&(0,0)\\
3&(-1,-1,0,1,0,1,0,0,0)&(0,0)\\
5&(0,0,-1,0,1,1,0,1,0)&(0,1)\\
7&(0,0,-1,1,1,0,0,1,0)&(1,0)\\
9&(-1,0,0,0,1,1,0,1,0)&(1,0)
\end{array}
$$

Apply the displayed forms of $L_3,L_4$ and count their $0,0$ pairs.
For example, in row 1 the real set after $L_2$ is $\{0,5,6,7,8\}$.
Only $(7,8)$ compares reals in $L_3$. After $L_3$ the real set is
$\{0,3,4,7,8\}$; in $L_4$, only $(b,y)$ compares reals. All other rows are checked by
the same two-layer calculation; the listed exceptional choices of
$(x,y)$ are precisely those requiring a different placement.

Every row leaves exactly two active layers among the first four, each
with one comparator. The last three layers add at most three active
layers. After pruning and untangling, the five reals would therefore
be sorted in at most five layers with at most one comparator in each
of the first two. README Lemma 3 forbids this. The proposed seven-layer
sorter cannot exist. $\square$

## 5. Independent finite checks

[`verify/h9_cycle_proof.py`](verify/h9_cycle_proof.py) uses only Python's
standard library. It verifies all 72 instances of the nine-row table
and records the sentinel state at every layer. Independently, it
enumerates all third and fourth matchings satisfying the necessary
$(3,2)/(2,3)$ count conditions and no consecutive repetition. There
are 54 third layers and 432 layer pairs; the stated duality and idle-wire
relabeling send them to exactly the 72 derived forms.

It also checks the disjoint-support invariant on 570,042 assignments
and matching layers of widths two through seven, and checks the
intersecting-support extension on a further 340,768 assignments and
layers of widths two through six. These checks validate the hand
argument; none is used to establish an unproved enumeration premise.

Run from the repository root:

```sh
python3 depth-hand-proofs/verify/h9_cycle_proof.py --out depth-hand-proofs/results/h9-cycle-proof-checks.json
```

The [result file](results/h9-cycle-proof-checks.json) includes the source
hash, counts, and all 72 trace certificates.
