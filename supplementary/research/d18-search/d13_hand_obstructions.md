# Short conditional hand obstructions inside case 116

**Result.** One specified five-layer continuation of case 116 cannot be
extended to a depth-eight sorter. There are two short proofs below:

* six explicit probes keep rank 6 on at least five wires after **every**
  sixth matching;
* a six-wire counting bound prevents ranks 3 and 9 from both reaching
  four positions, although either rank can do so separately.

These are hand-checkable finite certificates for the specified **five-layer**
prefix. They do not refute every continuation of the two-layer cover case.
The complete case-116 result still uses the checked structural SAT proof in
[certificate-guided-frontier.md](certificate-guided-frontier.md).
The interval and single-rank one-sided-edge lemmas were already proved in
the updated main-tree `depth-hand-proofs/d13.md`, Lemmas 15 and 17. The
progress here is the explicit small certificates and the simultaneous-rank
counting argument, not a claim that those earlier lemmas are new.

## 1. A finite-probe matching bound

A rank-k probe is a binary input with one star and exactly n-1-k fixed
ones. Run the network once with the star 0 and once with it 1. The outputs
still differ at exactly one wire. That wire can hold rank k: assign ranks
above k to the fixed ones, ranks below k to the fixed zeros, and k to the
star. Thus a fixed 0 beside an output star represents a value below k;
a fixed 1 represents a value above k.

Let S_k be any set of wires on which an explicit probe table puts its
rank-k star. Call a pair a,b in S_k **separated** if the table contains
both of these witnesses:

* the star is at one of a,b and the other wire is 0;
* the star is at one of a,b and the other wire is 1.

The witnesses need not have the star at the same endpoint. Comparing a,b
sends their two witness stars to opposite outputs. Consequently that
comparison cannot merge the two possible rank-k positions into one.

**Separation lemma.** If every pair in S_k is separated, then after any
one matching layer rank k still has at least |S_k| possible positions.

*Proof.* Partition the wires into the matching's edges and idle singletons.
A block meeting S_k once contributes at least one position. A block meeting
it twice contributes both positions by separation. Distinct blocks have
disjoint output wires, so these contributions add to at least |S_k|. ∎

This argument uses only the displayed probes. It does not require computing
the full attainable-rank relation or assuming it has a particular form.

Here is a version that combines ranks. Assign nonnegative weights λ_k.
For a possible edge e={a,b}, let

    w(e) = sum of λ_k over ranks for which a,b are both in S_k
           and the displayed probes do not separate a,b.

A comparison can lose at most w(e) units from the sum of the tracked
position counts. Suppose nonnegative wire prices p_c satisfy

    w({a,b}) <= p_a + p_b       for every pair a,b.

Then every matching M satisfies

    sum_k λ_k |P_after(k)| >= sum_k λ_k |S_k| - sum_c p_c.       (1)

*Proof.* Apply the preceding block argument separately for each rank,
allowing one lost position when the two endpoints are not separated.
Sum the weighted losses over the matching. They are at most
sum_{e in M} w(e), at most sum_{e in M}(p_a+p_b), and at most sum_c p_c
because matching edges have disjoint endpoints. ∎

In particular, simultaneous bounds |P_after(k)|<=b_k require

    sum_k λ_k (|S_k|-b_k) <= sum_c p_c.

With full rank supports and the exact one-sided edges, this is the usual
weighted matching upper bound applied to Lemma 17. A finite probe table
suffices to prove the displayed inequalities directly, without an exact
edge computation or a matching enumeration.

## 2. The five-layer prefix

All labels are zero-based. These are the relabelled case-116 wires used by
the checked structural result. The first two layers are that result's
prefix; the final three are one continuation.

```text
L1: (0,6) (1,7) (2,9) (3,12) (4,11) (5,10)
L2: (0,5) (1,8) (2,10) (3,11) (4,12)
L3: (1,3) (2,4) (5,11) (6,9) (7,10) (8,12)
L4: (0,1) (3,7) (4,8) (5,6) (9,12) (10,11)
L5: (1,2) (3,4) (5,8) (6,7) (9,10) (11,12)
```

The SAT relaxation found this continuation in 8.2 seconds. Exact binary
replay confirms that after L5 every rank has at most eight possible wires
and every wire has at most eight possible ranks. So the degree-eight cut
conditions alone do not reject this continuation. SAT was used to find
an example, not as a premise of either proof below.

## 3. Six probes reject every sixth matching

Use rank k=6 and S={2,4,5,8,9}. Every input below has six fixed ones.
Strings list wires 0 through 12 from left to right. The last column restricts
the output to the five wires of S in their displayed order.

| Input probe | Output after L5 | On wires 2,4,5,8,9 |
|---|---|---|
| `111111*000000` | `00000011*1111` | `000*1` |
| `1111101*00000` | `00000*0111111` | `00*11` |
| `111*011000100` | `001000110*111` | `1000*` |
| `1010111001*00` | `00*0010110111` | `*0110` |
| `00111100*1010` | `0010*00011111` | `1*011` |
| `10111010100*0` | `0000*10110111` | `0*110` |

Every wire of S has a star. For each of its ten pairs, the last column
contains both a star/0 and a star/1 witness. This is a check of twenty
pair conditions in a six-row table. Therefore the separation lemma gives

    |P6(6)| >= 5

for **every** choice of L6, including partial matchings. A two-layer
sorting suffix permits at most four positions for any rank, by the
backward cone bound. This prefix cannot have a depth-eight completion. ∎

## 4. Two ranks compete for six wire prices

The following probe tables witness these sets after L5:

    S3 = {0,1,2,3,4,5,6,9},
    S9 = {2,4,6,7,8,9,10,11}.

Give price 1 to the six wires

    T = {0,2,4,6,9,10},

and price 0 to all others. The only zero-price wires in S3 are {1,3,5};
the only zero-price wires in S9 are {7,8,11}. In the corresponding table,
every pair in each of these triples is separated.

| Rank | Input probe | Output after L5 |
|---|---|---|
| 3 | `111111111*000` | `000*111111111` |
| 3 | `1111111*00101` | `00101*1111111` |
| 3 | `11111110011*0` | `0*10011111111` |
| 3 | `1111111110*00` | `00*0111111111` |
| 3 | `11111111*0100` | `0010*11111111` |
| 3 | `110111111010*` | `*010101111111` |
| 3 | `11*1110110011` | `001110*111111` |
| 3 | `011111011101*` | `0*11100111111` |
| 3 | `*101110110111` | `001110111*111` |
| 9 | `11*1000000000` | `0000000*00111` |
| 9 | `10110000*0000` | `00000001*0101` |
| 9 | `1*01000010000` | `00000000101*1` |
| 9 | `111*000000000` | `0000000100*11` |
| 9 | `11100*0000000` | `000000*100011` |
| 9 | `1101*00000000` | `000000000*111` |
| 9 | `1000011000*00` | `00*0000000111` |
| 9 | `01000101*0000` | `0000*00100011` |

Use λ3=λ9=1. An edge that might reduce either tracked count must touch T:
otherwise it lies inside one of the separated triples. An edge that might
reduce both counts must have both endpoints in

    S3 intersect S9 = {2,4,6,9},

which is contained in T. Thus w({a,b})<=p_a+p_b for every pair, without
any further table. Formula (1) gives

    |P6(3)| + |P6(9)| >= 8+8-6 = 10.

At least one of these ranks therefore has five or more positions. This
is a second proof that every sixth matching fails a necessary condition
for a two-layer sorting suffix. ∎

This incompatibility is genuinely simultaneous: direct replay verifies
that the following matching makes rank 3 have exactly four positions,

    (0,1) (2,6) (3,9) (4,5),

while this one makes rank 9 have exactly four positions,

    (2,4) (6,8) (7,9) (10,11).

So each of these two individual one-rank requirements is feasible. Their
shared matching is the obstruction. These two feasibility checks illustrate
the distinction; they are not premises of the counting proof.

## 5. Verification, controls, and the remaining gap

[d13_hand_verify.py](d13_hand_verify.py) replays every displayed probe twice,
checks the separated pairs and wire-price premises, and verifies both
individual-rank matching controls. It uses no SAT solver. Its
[record](results/d13-hand-verification.json) includes source and certificate
hashes. The certificates are also available as
[six-probe JSON](results/d13-hand-case116-rank-separation-certificate.json)
and [two-rank JSON](results/d13-hand-case116-two-rank-certificate.json).

As a positive control, the verifier checks the existing depth-nine sorter
extending the same two-layer prefix on all 8192 binary inputs. At its cut
after L7, both rank and wire degrees are at most four. At its cut after L6,
the verifier confirms that **no** rank has a separated five-wire set;
such a set would incorrectly reject its known next layer.

The solver invocation used only to find the five-layer example had a hard
120-second wall cap. It terminated `SURVIVOR`, not timeout or UNSAT; see
[terminal record](results/d13-hand-case116-cut5-terminal.json).

```sh
python d18-search/d13_hand_verify.py
```

The unproved next step is a structural argument ensuring one of these small
certificates, or a different wire-price certificate, for **every** five-layer
continuation of case116. This note does not enumerate or cover those
continuations. It closes no additional two-layer cover case and gives no
D(18) exclusion. It provides a concrete replacement for SAT at one
conditional branch and a reusable way to combine ranks in later branches.
