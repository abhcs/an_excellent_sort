# Rank profiles, sharp ending capacity, and an exact path test

**D(18) remains unresolved.** These results constrain all possible two-layer
endings, rather than only particular graph configurations. They give a sharp
capacity bound for normalized endings, identify its equality case, and reduce
completion of a specified prefix to a path dynamic program. They apply at
arbitrary width. No claim of literature-wide novelty is made.

The only imported sorting-network normal forms are the last-layer adjacency
and penultimate adjacent-block properties from Codish, Cruz-Filipe and
Schneider-Kamp, [*Sorting Networks: the End Game*](https://arxiv.org/pdf/1411.6408).
The pair-graph and nonredundancy arguments are proved in
[the preceding note](two-layer-context-proofs.md).

## A rank profile identifies every unresolved block

Let U be the full binary image of a standard comparator prefix P. Define
c_z to be the number of outputs with exactly z zeros, for 0<=z<=n. Each
c_z is at least one because sorted inputs are fixed.

**Theorem 1.** c_z=1 if and only if no required-pair edge crosses the cut
between wires z-1 and z. Thus consecutive indices with c_z=1 give exactly
the interval components of the prefix pair graph.

**Proof.** If c_z=1, every input with n-z ones produces the sorted vector
0^z 1^(n-z). Monotonicity then forces all wires below z to be zero at
smaller weights, and all wires at least z to be one at larger weights.
No output can invert a pair across this cut. The inversion characterization
of the pair graph therefore forbids every crossing edge.

Conversely, if there is no crossing edge, there can be no inverted output
pair across the cut. A vector with n-z ones other than 0^z 1^(n-z) would
put a one on the left and a zero on the right, giving just such an inversion.
Hence there is only one output of this weight. ∎

These components already contain their correct ranks. Comparisons between
different components in a sorting suffix are redundant and may be removed.
Within any one component, the suffix's comparison graph must be connected,
because every required pair must be able to meet.

## Only paths and four-cycles remain

Write the two remaining layers as M,N and remove redundant gates. N pairs
adjacent wires. Contract its pairs; M can join only neighboring N-blocks.
Each block has at most two M incidences, and a singleton has at most one.

Consequently a connected component of M union N is an alternating path
or a four-cycle. A cycle of greater length would give a cycle on a line of
N-blocks, which is impossible. A four-cycle uses two consecutive N-pairs
with two M-edges between them.

For a path component, singleton N-blocks can occur only at its endpoints.
Every interior N-block is a pair. There is exactly one M-edge between each
successive pair of N-blocks. Therefore a given interval component has only
**two possible final-layer tilings**: pair successive wires starting at its
first wire, or starting at its second wire. The four-cycle option is added
when the component has four wires.

For example, on one connected 18-wire component, the two path families
have respectively 512 and 256 choices of the M ports. Their orientations
need not be enumerated: the dynamic program below handles them directly.

## Exact capacity profiles of an ending

For an ending S=M;N, let F(S) be all binary vectors that S sorts, regardless
of whether those vectors can be the image of a preceding prefix. Let b_z
count its accepted vectors with z zeros.

Reverse S from the sorted vector 0^z 1^(n-z). Reversing a comparator with
output 01 gives two predecessors; output 00 or 11 gives one; output 10
gives none. For an alternating path component this gives:

| Location of the zero/one cut | b_z |
|---|---:|
| Outside the component | 1 |
| Between consecutive N-blocks | 2 |
| Inside an endpoint N-pair | 3 |
| Inside an interior N-pair | 5 |

There are two small exceptions: a component consisting of a single
comparator has profile (1,2,1), and a singleton has (1,1).

**Proof of the entries.** Between N-blocks, only the one M-edge crossing
the cut is reversible in two ways. Inside an endpoint N-pair, reversing N
gives two states; the one incident M-edge is active in exactly one, giving
2+1=3 predecessors. Inside an interior N-pair, the two incident M-edges
are both active in one of the two states and neither is active in the
other, giving 4+1=5. Swapping the choices of ports exchanges which state
has four predecessors, without changing the count. ∎

A four-cycle has profile **(1,4,4,4,1)**. At its middle cut, two M-edges
are reversible, giving four states. At either cut inside an N-pair, the
two reversed N states each have one active M-edge, giving 2+2=4.

For disjoint interval components, concatenate their profiles, identifying
the shared endpoint entry 1. In particular their capacities add with one
subtracted for each join.

**Corollaries.** With two layers remaining, every prefix weight level has
at most five outputs. Within any component other than a four-cycle, levels
with more than two outputs cannot be consecutive. The full necessary
profile test is stronger: split c at its entries equal to one, then require
each segment to be dominated by one of the two path profiles, or by the
four-cycle profile for a four-wire segment.

Two short certificates require only exhibited outputs:

* Six distinct outputs at one weight contradict the level bound of five.
* Four consecutive levels with at least two outputs each, including two
  adjacent levels with at least three each, also exclude completion.
  None of those four levels can be a component boundary, so they lie
  inside one component of at least five wires. It must be a path, whose
  capacity profile cannot have adjacent entries greater than two.

The second certificate needs only ten runs: three at each of the two
heavy levels and two at each of the other levels. The files
[level-cap-certificate18.json](results/level-cap-certificate18.json) and
[heavy-neighbor-certificate18.json](results/heavy-neighbor-certificate18.json)
give six-run and ten-run examples. Their checker evaluates just the supplied
prefix inputs, checks distinct outputs and their weights, and applies the
hand argument. It does not enumerate the full image or invoke SAT.

## A sharp bound for all widths at least 17

The largest capacity of a connected path on m>=2 wires is
floor(7m/2)-3. It is attained by leaving two endpoint wires idle in N when
m is even, and one endpoint idle when m is odd. The opposite even tiling
has capacity one less when m>=4. A four-cycle instead has capacity 14.

**Theorem 2.** For n>=17, a prefix completable in two layers satisfies

    |U| <= floor(7n/2) - 3.

This is sharp as a bound on the accepted-input capacity of normalized
two-layer endings. Equality forces a single alternating path using the
maximal-capacity final-layer tiling.

**Proof.** Give a component of size m and capacity C the deficit
7m/2-(C-1). A singleton has deficit 5/2, a four-cycle has deficit 1, an
even path has deficit at least 4, and an odd path has deficit at least
9/2. Capacities combine as 1+sum(C-1).

If there is a path component of size at least two, these deficits already
give the stated bound, including the half-unit parity correction at odd
n. Equality allows no other component and requires the maximal path
tiling. Otherwise every component is a singleton or four-cycle. With s
singletons and q four-cycles, the deficit is q+5s/2=n/4+9s/4. For n>=17
this is strictly greater than the deficit required for equality. ∎

For n=18 the bound is **60**. Equality requires

    c = (1,2,5,2,5,2,5,2,5,2,5,2,5,2,5,2,5,2,1)

and final layer N={(1,2),(3,4),...,(15,16)}. There are 256 choices of M,
all obtained by choosing which port of each N-pair faces left.

Normalization matters. Arbitrary two-layer networks, which need not occur
as nonredundant endings of complete sorters, can sort many more binary
vectors. The bound is applied after removing redundancy and invoking the
ending normal forms. Also, sharpness for ending capacity does not assert
that its whole accepted set is an attainable eight-layer prefix image.

## Exact completion in O(n |U|) time once U is known

Fix one path tiling N in a rank component. A paired N-block has two choices
of which port faces left; its other port faces right. A singleton endpoint
has one choice. These choices automatically define a matching M with
one edge between successive N-blocks.

For a binary component input x of weight w, consider the cut after its
first c wires. Define

    delta_c(x) = number of ones in those c wires - max(0, w-(m-c)).

This is the number of ones that must leave the left side before sorting.
N does not cross this cut, and exactly one M-comparator does. Therefore
the two chosen ports u,v at that boundary must satisfy, for every x:

    delta_c(x) = 1 if x_u=1 and x_v=0, and 0 otherwise.

These are constraints on only the two neighboring block choices. Each
boundary has at most four choice pairs to check. A path dynamic program
finds a consistent sequence of port choices, or proves none exists.

This condition is sufficient too: if every boundary exports exactly the
required number of ones, every N-block has its correct number of ones.
Sorting each N-pair then produces the fully sorted output. Handle the
two four-cycle matchings directly, and solve separate rank components
independently.

**Theorem 3.** This gives an exact two-layer completion algorithm for a
standard comparator prefix. Once its full binary output set U is given,
the work is O(n |U|). No SAT solver and no exponential orientation search
are needed. Generating U can still require exponential work in n; this
does not solve the unrestricted depth problem in polynomial time.

[two_layer_profiles.py](two_layer_profiles.py) implements the count,
profile and exact flow tests. Its verifier checks the inverse profiles
on all 2,559 normal-form suffixes on widths two through eight, and checks
the completion decision against unrestricted suffix enumeration on
1,872 small prefixes. The maximum-capacity recurrence also agrees with
the displayed formula through width 64; the proof above establishes the
unbounded statement.

## Fourteen possible local states, with a one-run obstruction

Let x be a prefix output with z zeros, with two layers remaining. Extend x
virtually by zeros to the left and ones to the right when an index is outside
0,...,n-1. The familiar window condition fixes all positions below z-3 to
zero and all positions at least z+3 to one.

**Theorem 4.** In addition,

    not (x[z-3] = x[z-2] = 1),
    not (x[z+1] = x[z+2] = 0).

Consequently the six-position window has only fourteen possible words,
rather than all twenty words with three zeros and three ones.

**Proof.** Remove redundant suffix gates and write the resulting ending
M;N. The N-blocks are adjacent pairs and singletons, and M joins only
neighboring N-blocks. Reverse the ending from the sorted output with its
cut after position z-1.

If N has no comparator across this cut, reversing N leaves the sorted
word unchanged. Only M-edges between the N-block immediately to the left
and the N-block immediately to the right of the cut can move a one left.
The former block starts no earlier than z-2. Thus position z-3 remains
zero.

If N has the comparator (z-1,z), reversing N gives either 01 or 10 on
that block, with all earlier blocks zero and all later blocks one. Only
the unique one in this central block can move into an earlier block
when M is reversed. Matching disjointness permits this one to move at
most once. Thus at most one of positions z-3,z-2 can be one. Reversing
and complementing the argument gives the second assertion. This also
proves the assertions at the ends, using the virtual padding. ∎

In physical wire order, the excluded six-bit words are

    111000  110100  101100  011100  110010  110001.

Every other three-zero/three-one word is accepted by some normalized
two-layer ending on six wires. This last statement concerns individual
accepted words, not their simultaneous attainability by a prefix.
[two_layer_envelope.py](two_layer_envelope.py) checks the assertions
against every normalized ending on widths two through nine: 7,224 endings
and 123,502 accepted states. It also checks that the union at the middle
six-wire cut contains exactly the fourteen stated words.

This gives particularly small hand certificates. In
[one-run-envelope-certificate18.json](results/one-run-envelope-certificate18.json),
the supplied eight-layer prefix maps input 1576 to output 202752. In
wire order the latter is 000000000001100011, with z=14. Positions 11 and
12 are both one, contrary to Theorem 4. Evaluating this single run therefore
excludes every two-layer completion of that prefix. The checker verifies
the layer matchings and the run, then applies the theorem; it neither
enumerates all inputs nor invokes SAT.

## Five states really can occur in an attainable prefix image

One tempting strengthening was to replace five by four in the level
capacity bound, on the grounds that accepted sets of endings need not
be attainable prefix images. This strengthening is false.

[attainable-five7-d8.json](results/attainable-five7-d8.json) gives a full
seven-wire sorter of depth eight. After its first six layers, five
distinct outputs have four zeros. The file includes one input witness
for each state, and the whole sorter was independently evaluated on all
128 binary inputs. Thus the capacity five is genuinely attained.

It remains sharp at every width n>=7: first extract the largest n-7
values into their final positions by repeated maximum selection, then
apply the seven-wire sorter to the remaining wires. For the witnessed
inputs, place ones on the extra wires. Every maximum-selection comparison
then leaves those inputs unchanged, preserving the five intermediate
states. This construction concerns attainability, not optimal depth.

Even an outer level with only two zeros can attain five states:
[attainable-five8-z2-d9.json](results/attainable-five8-z2-d9.json) provides
an eight-wire example checked on all 256 inputs. The bounded UNSAT and
timeout experiments in the same directory only concern their specified
fixed endings and depths; they imply no universal impossibility.

## Sharing the ending in an exact SAT encoding

[shared_ending_sat.py](shared_ending_sat.py) uses one support flag for each
possible state before the final two layers. Each original input is
evaluated only up to this cut, and its resulting state forces the
corresponding support flag. Each supported state is evaluated through
the common ending once. The fourteen-state restriction supplies both
unit clauses on forbidden support flags and the two short clauses of
Theorem 4 on each original input's intermediate state.

This factorization is exact. Given a sorter, mark its actual intermediate
states as supported to satisfy the interface. Conversely every input
forces a supported state, and the shared ending must sort that state.
Unused flags may be false; reverse implications from flags to occurrence
are unnecessary. The necessary rank-profile restrictions remain in use.

The [calibration](results/shared-ending-sat-checks.json) retains all 904
fixed normal-ending positive controls, excludes all 22 complete
nine-wire depth-six cases, and finds a depth-seven network verified on
all 512 inputs. Two further positive controls reconstruct endings of
known 18-wire sorters and verify all 262,144 inputs each; see
[the crosschecks](results/shared-ending-crosschecks.json).

On complete case n18-r0000 the factored formula has 261,370 variables and
5,664,501 clauses, versus 303,172 and 6,203,577 in the direct capacity
encoding: reductions of 13.8% and 8.7%. Both bounded attempts timed out
after 45 seconds. Formula size is improved; solver speed and case closure
are not established. The new [result](results/shared18-r0000-attempt1.json)
records source hashes and the complete-cover hash.

## Current boundary for D(18)

A bounded search first found an eight-layer prefix with **59 outputs**, so the
proposed shortcut that every eight-layer prefix has at least 60 outputs
is false. The witness is in
[output-count-probe18.json](results/output-count-probe18.json). This
prefix is not claimed to have a two-layer completion.

A subsequent 45-second search targeting the rank profiles found a prefix
with only **50 outputs**, maximum pair degree five, and no parity
obstruction. Its [independent audit](results/degree-parity-counterexample18.json)
evaluates all 262,144 binary inputs. This also disproves the proposed
universal degree-or-parity obstruction for eight-layer prefixes on 18 wires.
It still fails the new profile test and has no two-layer completion. The
ten-run certificate above excludes this particular prefix by hand.

The remaining task is universal: show that every eight-layer prefix
fails the rank-profile or port-flow criterion, or close a complete set
of remaining cases. The criterion is exact for fixed prefixes, but none
of the 411 full two-layer-prefix cases has yet been resolved here.
