# Context-sensitive hand proofs for the last two layers

**D(18) remains unresolved.** This note sharpens the pair-graph approach.
It supplies an exact two-layer completion criterion, further graph
obstructions, and a small example showing why the surrounding bits matter.
All statements apply at arbitrary width; no literature-wide novelty claim
is made. See [the preceding proofs](two-real-hand-proofs.md) for the
collision criterion and last-layer normal-form dependencies.

The subsequent [rank-profile and path-flow result](two-layer-capacity-proofs.md)
replaces branching over matching choices by an exact O(n |U|) path algorithm,
once the prefix image U is known. It also gives a sharp general ending-capacity
bound and records a counterexample to making degree and parity universal.

## The pair graph is exactly the inversion graph

For a prefix P, let U be its binary output set. Its pair graph G joins
i<j when U contains two vectors differing only by exchanging bits 01 and
10 on i,j.

**Theorem.** The edge ij belongs to G if and only if some output of P has
bit 1 on i and bit 0 on j.

**Proof.** One direction follows immediately from the definition. For the
other, lift an input witnessing the inversion to a permutation of distinct
values: assign all its zero positions smaller values than its one positions.
Threshold commutation makes the resulting permutation output inverted at
i,j too.

Connect the increasing input permutation to this input by swaps of
consecutive values r,r+1, at arbitrary input positions. Such swaps generate
all permutations. Under any comparator, the two corresponding runs either
remain identical except for the positions of r,r+1, or coalesce when those
values meet. Comparisons with every other value have the same outcome in
both runs. Thus neighboring output permutations are identical or differ
by swapping consecutive values.

The relative order of the values on output wires i,j starts increasing
and ends decreasing. Swapping consecutive values can reverse this order
only by swapping those two wires themselves. At such a step, threshold
between r and r+1. The two binary outputs differ only at i,j, proving the
required pair edge. ∎

Consequently a missing edge i<j means the forced order f_i<=f_j on every
input. These orders are transitive, and G is their incomparability graph.
In particular, **every nonredundant penultimate comparator is an edge of
G**. One inverted output suffices to certify a required graph edge; two
explicit exchange outputs are useful when their surrounding bits matter.

This also shortens the interval-component proof: if i<j<k and ik is an
edge, at least one of ij,jk is an edge, since the two missing edges would
give f_i<=f_j<=f_k. A connected component therefore cannot jump across a
missing channel. Different interval components have all their values
already ordered relative to each other.

## The penultimate matching must be present in the graph

The preceding path-structure theorem placed G inside a chain of bags of
size at most two. The two-element bags are penultimate comparisons. The
new observation means their internal edges must themselves belong to G,
after redundant comparisons have been deleted. A singleton bag has at
most one last-layer comparison, so it occurs only at a path endpoint or
as an isolated bag.

Equivalently, contracting the penultimate matching in G must give a
disjoint union of paths. Each connected component on m vertices has at
most two unmatched vertices. This is a necessary graph condition, not a
sufficient completion criterion.

Two useful consequences are:

* **No induced four-leaf star K1,4.** The possible neighbors of a wire lie
  in its own penultimate pair and at most two neighboring pairs. An
  independent set can use at most one vertex from each of these groups,
  since each two-element pair is an edge of G. Four independent neighbors
  are therefore impossible.
* **No induced K2,3.** Let a,b be the two independent centers and x,y,z
  their three independent common neighbors. Each center must be paired
  with one of x,y,z: otherwise its three neighbors would need to occupy
  only two neighboring penultimate bags, with at most one per bag.
  Say the pairs are ax and by. The bag of z is distinct from both.
  The required edges ay,bx,az,bz force all three bag adjacencies, forming
  a triangle after contraction. This contradicts the path structure.

This uses **induced** subgraphs: the missing edges certify forced orders
and hence forbid redundant pairings. A bare K2,3 subgraph is not enough.

## A free bit forbids two penultimate comparisons

Suppose U contains four outputs with the following pattern, all other
coordinates fixed:

| u | v | w |
|---|---|---|
| 1 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 1 |
| 0 | 1 | 1 |

**Rectangle lemma.** Neither uw nor vw can occur in the penultimate layer
of a two-layer completion.

**Proof.** Mark u,v as the two finite values. If u is compared with w,
changing w from negative to positive infinity changes the output port
of the value from u. The port of the value from v stays fixed: its mate
cannot be w, and all other background bits are unchanged. The last layer
would have to compare this fixed port to two different ports. That is
impossible in a matching. Interchange u and v for the other exclusion. ∎

More generally, for a required pair uv, collect all its common-bit
contexts. If u and v have distinct penultimate mates p,q, the columns
of bits at p and q must be equal or complementary across these contexts
(treat an idle wire as a constant column). Otherwise two contexts keep
one finite output port fixed and change the other, again demanding two
overlapping last-layer comparisons. Port positions and final adjacency
provide further constraints.

## An exact finite criterion

Choose a penultimate matching M, allowing idle wires. For a required pair
uv and each common-bit context z:

1. If M compares u with v, they already meet.
2. Otherwise route each marked value through M. If u is idle, its port is
   u. If its mate is p, its port is min(u,p) when z_p=1, and max(u,p) when
   z_p=0. Apply the same rule to v.
3. Require the last layer to compare the resulting two ports.

**Theorem.** P admits a two-layer sorting completion exactly when some M
makes the union of these requirements an adjacent-channel matching.
When searching M it is sufficient to consider nonredundant comparisons
of channel distance at most three.

**Proof.** Necessity follows from the two-real collision criterion and
the established nonredundant last-two-layer normal forms. For sufficiency,
use the required matching as the final layer. Every witnessed exchange
edge of U coalesces. The outputs of each weight are connected by exchanges,
so their final outputs are identical. The already-sorted vector of that
weight belongs to U and is fixed, so all those outputs are sorted. ∎

[two_layer_context.py](two_layer_context.py) implements this criterion.
Its variables are the partners in M; each wire has at most seven choices,
including being idle. It precomputes the last-layer requirements for each
pair of partner choices, propagates reciprocal matching choices and
incompatible final comparisons, and branches only when propagation does
not finish. It uses **no SAT solver**. A time limit returns TIME_LIMIT,
never UNSAT. This closes two remaining layers of a specified prefix; it
does not enumerate all eight-layer prefixes on 18 wires.

## Why graph tests and three-free-wire tests are not enough

Consider this prefix on five wires:

```
[(0,1),(2,3)]
[(1,3),(2,4)]
[(1,4)]
```

Its pair graph is a triangle on 0,1,2 with the path 0--4--3 attached.
It passes the implemented degree, parity, topology, induced-subgraph and
three-free-wire tests, but has no two-layer completion. Here is a hand
proof. Binary strings below list wires 0 through 4 from left to right.

The outputs 10011, 00111, 11011 and 01111 form the rectangle on exchange
wires 0,2 with free wire 1. Thus M cannot compare 1 with 0 or 2. The prefix
also forces wire 1 below wires 3 and 4: the second layer establishes the
first order, and the third lowers wire 1 further while establishing the
second. Comparisons 13 and 14 in M would be redundant. Delete them. Wire 1
is now idle.

Outputs 10011, 01011 and 00111 require pairs 01 and 12. An idle wire can
meet both starting wires 0 and 2 in one remaining comparison only if they
occupy the same M-pair. Hence M must contain 02.

On the exchange 01011 versus 00111, the marked value from wire 2 stays on
2, since its mate 0 contains zero. Therefore N must contain 12.
But outputs 10010 and 00011 require pair 04. Its value from 0 moves to 2
through M=02. Its value from 4 can only stay on 4 or move to 3: wires 0,2
are already paired and 1 is idle. Thus N also needs 24 or 23, both of which
conflict with 12. This is impossible.

[context-obstruction5.json](results/context-obstruction5.json) supplies
seven explicit input/output runs for the outputs used in this argument.
The contradiction itself uses no last-layer adjacency restriction.

## Simpler three-free-wire certificates

If U contains all eight assignments on three output wires with every
other wire fixed, two further layers are impossible. Set the fixed wires
to signed infinities. By threshold commutation, sorting those eight
binary assignments would sort three arbitrary finite values. Each layer
can compare at most one pair of these values, so two layers provide at
most two informative comparisons. They cannot distinguish six orders.

The previously studied 18-wire prefix has such a face. Its
[eight-run certificate](results/three-cube-certificate18.json) is simpler
than its parity and radius-ball certificates. A 45-second search from that
family did not remove every three-dimensional face. A different seed,
the 78-comparator depth-eleven network in
[Dobbelaere's table](https://bertdobbelaere.github.io/sorting_networks.html#N18L78D11),
did produce a cube-free eight-layer prefix after 22.6 seconds of bounded
search. Its [independent audit](results/cube-free-prefix18-independent-audit.json)
enumerates all 262,144 binary inputs. Therefore the proposed universal
three-free-wire obstruction at width 18 is **false**. That prefix still
violates the degree bound and has no two-layer completion. Absence of a
three-dimensional face is not sufficient even on five wires, as the
example above shows.

The implementation agrees with unrestricted enumeration of both suffix
layers on all 1,196 prefixes of depth at most three on three or four wires.
It additionally checks all 676 three-layer five-wire prefixes beginning
with the canonical maximal first layer, against all unrestricted pairs
of suffix layers.
It recovers the last two layers of two independently verified 18-wire
depth-eleven networks by propagation alone. The main missing step remains
a complete argument for every eight-layer prefix at width 18.
