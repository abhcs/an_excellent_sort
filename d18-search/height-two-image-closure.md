# Poset images, antichains, and necessary comparisons at arbitrary width

This note reconstructs and extends a structural lead from the research
session whose temporary worktree is no longer available. The statements
below have direct proofs. They exclude conditional prefix families, not
the complete D18 cover. In particular, **D(18) >= 11 is still unresolved**.

Write F(P) for the set of all real vectors satisfying the inequalities
of a finite poset P on the wires. Having every state satisfy P is not
enough for the lower bounds below: the reachable family must **contain
F(P)**. Exact equality is a convenient invariant that implies this.

## 1. A matching can preserve an exact height-two image

Suppose P has height at most two. Partition its nonisolated vertices
into lower vertices L and upper vertices U, so every relation goes from
L to U. The remaining vertices I are isolated. Call a matching M
compatible with P if it contains no L--L or U--U edge. A vertex of I
can take either role in its one comparison. The comparator's physical
orientation need not agree with the old roles.

For each comparator, route its old lower endpoint to its minimum-output
coordinate and its old upper endpoint to its maximum-output coordinate.
When both endpoints are isolated, either assignment works. These local
identities or transpositions define a fixed permutation t; unmatched
vertices are fixed. Form Q from

* the relations t(l) <= t(u) for every relation l < u of P; and
* the minimum-output <= maximum-output relation of every gate of M.

**Image theorem.** Q has height at most two, and

    M(F(P)) = F(Q).

For the forward inclusion, let x respect P and y=M(x). For every old
lower vertex l, y[t(l)] <= x[l]; for every old upper vertex u,
x[u] <= y[t(u)]. Thus each old relation gives

    y[t(l)] <= x[l] <= x[u] <= y[t(u)].

The new comparison inequalities hold as well. Every relation in Q still
goes from a lower-role output to an upper-role output, proving the
height bound. Unmatched vertices cause no exception.

For the reverse inclusion, given y respecting Q, set x[v]=y[t(v)].
The transferred old relations ensure x respects P. Each comparator
receives exactly its target minimum and maximum, in one of the two
orders; Q guarantees that sorting them returns y. This is a fixed
permutation preimage, including ties. The proof permits arbitrary
degrees, disconnected components, and repeated comparisons.

Starting with the empty poset, every sequence of compatible layers
therefore has an exact height-two image. The invariant is recursive:
roles are those of the current Q, not the first layer's physical wires.
More generally, if a reachable family contains F(P), its image after M
contains F(Q); other reachable states do not invalidate the argument.

**Extension.** For a general poset, allow comparisons only between a
minimal and a maximal element, with isolated elements taking either
role, and keep non-extremal elements idle. The same proof gives an exact
poset image of height at most max(height(P),2). New relations from
minimal to maximal elements cannot create a longer chain.

## 2. An antichain leaves a full sorting problem

**Antichain lemma.** If the reachable family at a cut contains F(P),
and P has an antichain R of size r, any sorting suffix needs at least
D(r) layers.

Give R arbitrary values in (0,1). Fix every strict predecessor of R to
-1 and every other vertex outside R to 2. These assignments all respect
P: the strict predecessors form a down-set, no two elements of R are
comparable, and no vertex outside that down-set can precede an element
of R. Thus every ordering of the r real values occurs at the cut.

In the suffix, comparisons with fixed small or large values only route
the real values. Their routes are independent of the ordering inside
(0,1). Delete those comparisons and untangle the remaining real tracks
as in the signed-restriction lemma. The resulting network sorts r
arbitrary reals in no more layers than the original suffix. Hence the
lower bound. Equal sentinel values and initially interleaved positions
are harmless.

In particular, if k prefix layers preserve the height-two invariant,
the whole network needs at least

    k + D(width(P)) >= k + D(ceil(n/2))

layers. Either side of a height-two poset, with isolated vertices
assigned to a side, is an antichain, so its width is at least ceil(n/2).

For 18 wires, four such layers force depth at least 4+D(9)=11.
For 17 wires, three such layers force depth at least 3+D(9)=10.
Thus a hypothetical depth-ten sorter on 18 wires must break this
invariant by layer four; a depth-nine sorter on 17 wires must break it
by layer three. These are necessary conditions on the prefix, not
unconditional new bounds. The same formula applies at every width.

An explicit excluded 18-wire family consists of the four layers

    M_s = {(i, 9 + ((i+s) mod 9)) : 0 <= i < 9},  s=0,1,2,3.

All comparisons send a lower-role value to wires 0..8 and an upper-role
value to wires 9..17. The invariant holds throughout, even though the
interaction graph is connected and has degree four at the last cut.
All nine lower coordinates remain arbitrary when upper coordinates are
fixed above them. No six-layer suffix can finish this prefix.

## 3. The next matching must destroy large independent sets

Let H be the comparability graph of an arbitrary poset P: two vertices
are adjacent exactly when P makes them comparable. Suppose the cut
family contains F(P), and let M be the first matching of a d-layer
sorting suffix. If R is independent in H union M, the preceding
sentinel construction makes R arbitrary and M compares no two of its
real values. After pruning, that whole first layer disappears. Therefore

    d >= 1 + D(alpha(H union M)).

This tests an arbitrary next matching, including one that breaks the
height-two invariant. It only requires the full poset family at the
cut; it does not assert that later images are poset families.

For 18 wires after three compatible layers in a hypothetical depth-ten
sorter, seven layers remain. Consequently the fourth matching must
satisfy

    alpha(H union M) <= 8,

because D(9)=7. In particular H union M must contain an odd cycle:
every bipartite graph on 18 vertices has an independent set of size nine.
Merely connecting components, while keeping their union bipartite,
cannot suffice.

There is also an elementary necessary count. For any bipartition A,B
of the height-two comparability graph H, let m_A and m_B count M-edges
whose endpoints both lie in the respective part. Since M is a matching,
A contains an independent set of size |A|-m_A in H union M, and B
contains one of size |B|-m_B. Thus

    m_A >= |A|-8,    m_B >= |B|-8.

For a balanced 9+9 partition, M must have at least one comparison
within each side. These counts and the odd-cycle condition are
necessary, not sufficient: a nonbipartite graph can still have an
independent set of size nine.

## Scope and verification

The proofs use the established smaller-width depth bounds, principally
D(9)=7, and the standard signed-restriction/untangling lemma. They use
no SAT premise. Small binary controls and an independent mathematical
review are recorded by `height_two_recovery_review.py` and its result
file. Those finite controls supplement, rather than replace, the proofs
above. No claim of priority in the literature is made.
