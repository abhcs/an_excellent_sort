# Critical two-idle matchings: partial rows and a finite closure

**Result.** For the case-606 signed family, no two counted matching layers
cover all twenty states at peak h-3 when the first matching contains the
critical B edge dc. The active width may be any even n=2h>=12, with any
even number of additional common real coordinates and any physical
embedding of the labels.

This combines the accepted critical-perfect result from
[round five](d17_feedback_round5_reduction.md), the at-most-one-cross hand
theorem from [round three](d17_feedback_round3_hand.md), and the new
two-idle reduction below. The mixed two-idle last step uses an independent,
SAT-free certificate for 1,584 canonical first matchings. **That finite
verification is a premise.** This is a finite-assisted critical-branch
theorem, not a complete hand proof of case 606 or of D17/D18. The remaining
case-606 branch has no dc and has mixed A--B comparisons.

## 1. Family, normalization, and first peaks

Use the same signed product family as before:

    G = {AB,BC,CE,BD},       A-, B-, C+, D+, E+;
    B columns = qab,qbc,qce,rce,qbd,
    q-,a-,b-,c+,d+,e+,r+.

All other coordinates are common reals. Select columns qbc,qce,rce for
the local path argument. Critical dc has one sentinel, c, in each selected
state. Its common sentinel output is k; the other two B sentinels form
the path b--q--e--r, with edges qb,qe,er.

Fill the last counted matching N to be perfect. It peaks exactly when
two of its edges lie inside the transported five-sentinel set. If M has
m edges, i idle sentinels, and s SS edges, then

    RR_M = m-5+i+s.                                      (1)

The comparable-idle augmentation from
[round two](d17_feedback_round2_normalization.md) preserves dc. Every
four-element antichain of the full twenty-state type order contains d,
which dc already uses. Thus a hypothetical critical cover can be
augmented until M is perfect or has exactly two idle wires. The perfect
case is already excluded, with the explicit finite premise in round five.

For two idles, the full-family incomparable idle pairs can only be CD or
DE, or a same-sign A/B pair. All noncritical B coordinates are ordered:

    q <= b <= a <= 0 <= r <= e.

Pairs containing c or d cannot be idle. If the B idle is a, it is always
real in the selected three columns. Its comparison with the A idle then
has fixed routing, so it can be added for those columns. This produces a
critical perfect cover of those twelve states, contradicting the
round-five result, which uses only those states. We may therefore restrict
mixed idles to the following ten patterns:

    A idle in {A,B}, B idle in {q,b};       four patterns;
    A idle in {C,D,E}, B idle in {e,r};     six patterns.  (2)

For any near-perfect critical M, a selected state can peak in M only if
**both** idle wires are sentinels. Indeed m=h-1. If i=0, dc accounts for
one used sentinel, leaving at most two SS gates, and (1) is at most h-4.
If i=1, the other used sentinels apart from dc number three, so s<=1 and
again (1)<=h-4. If i=2, a peak occurs exactly when the other two used
sentinels apart from c form one SS gate.

## 2. Both idles in A: a hand closure with any number of crosses

The idle pair is CD or DE. Neither is a G-edge, so no selected state has
both idles as sentinels. Consequently all selected states require N.
Consider just the incident A rows BC and BD; D is idle in either pattern.

Their transported sentinel triples outside the B path have the form
{k,u,x} and {k,u,w}, with distinct k,u,x,w. Here u is the image of B,
w is the unchanged idle D, and x is the image of C in row BC. If BC is
itself an M-edge, its opposite signs keep the B and C images distinct,
and the same description holds.

Every used A vertex outside C has the same active/inactive status in these two
rows. Its cross gate therefore gives the same B routing in both. A cross
gate at the common vertex B also has the same routing in both rows.
The only possible change is a same-sign cross at C: a single B-path
coordinate y in row BC is replaced by x in row BD. Opposite-sign crosses
have fixed routing, and a cross to a has no variable B sentinel in these
columns. The matching blocks ensure that all other named positions stay
distinct.

Thus the six required sets have either the ordinary two-incident-row
form or its one-coordinate transferred form. Both are impossible by
the hand path lemmas in round three, Sections 1--2. This proves the
AA-idle case at any width, independently of the finite certificate below.

## 3. Mixed idles give at least two full selected rows

Write I for the A idle and w for the B idle in (2). A first peak in a
selected state must have A row I--U and B-path column w--z, with U--z
an M-cross gate. Conversely these conditions give the necessary SS gate
from Section 1.

The path degree of w is at most two. Moreover, distinct first peaks
must use distinct A rows and distinct B columns: two in one row would
require U to have two partners, and two in one column would require z to
have two partners. There are therefore at most two selected first peaks,
on distinct rows and columns. At least **two of the four A rows** require
N in all three selected columns.

For any fixed A row, every M-comparator has fixed type routing across the
selected B columns. In particular, same-sign A/B collisions occupy both
outputs when both inputs are sentinels; they do not remove an A sentinel.
Each fully required row has the exact five-set form

    T+qb, T+qe, T+er,       |T|=3,

with the four path positions distinct and outside T. Its six necessary
cores are er plus any perfect matching of T+q, or qb plus any perfect
matching of T+e. This is precisely the hand one-row classification from
round three.

## 4. Contraction preserves the two-idle deficit

The external-common-real contraction proved in round five did not need
M to be perfect. Deleting a common-real M-edge reduces n by two, m by
one, and the peak by one. Replacing u--r and v--s, where r,s are common
reals and u,v are comparable one-sided type coordinates, by u--v has
the same width/size change and loses at most one first-layer RR gate.
The fixed type routings identify two always-real output tracks to delete
from N, preserving every SS edge before completing N again. Thus every
old peak remains covered and the deficit h-m is unchanged.

For the present branch, contractions use **full twenty-state** type
comparability. This is essential: Section 6 exhibits actual covers of
the selected three-column family, so the omitted columns cannot simply
be discarded. In particular, a is not treated as a common real when
testing a contraction across blocks.

Let c>=2 count A--B edges. With mixed idles there are four used A and
four used noncritical B coordinates, so c<=4. Delete all common-real
M-pairs, and contract as follows:

* c=2: the two noncross B coordinates are comparable and can be paired
  internally. The two noncross A coordinates can also be paired unless
  they are CD or DE; in that case retain their two common-real partners.
* c=3: the one remaining A and B coordinate each has a common-real
  partner. Contract these if full-family comparable, yielding c=4;
  otherwise retain the two common reals.
* c=4: all used variables are already cross-paired, so no external
  common-real partner remains.

Common-real names can be permuted. More generally, an arbitrary common
permutation of physical coordinates preserves this pure two-layer count
property: reorient each first comparator and absorb its fixed output
swap into N. Its last-layer orientation does not affect incoming RR
counts. Hence the following canonical widths cover arbitrary embeddings
and arbitrary initial numbers of common reals.

| Width | Crosses | Residual noncross form | Number |
|---|---:|---|---:|
| 12 | 2 | internal A pair and internal B pair | 10·C(4,2)^2·2! = 720 |
| 14 | 2 | external A pair CD/DE; internal B pair | 144 |
| 14 | 3 | external incomparable A/B pair, using full-family types | 480 |
| 12 | 4 | cross bijection on the used four A and four B vertices | 10·4! = 240 |

For the second row of the table, there are twelve choices of the idle
pattern and remaining external A pair; choosing the two crossed B
vertices and their bijection gives 12·C(4,2)·2!=144. For the third, each
of the ten idle patterns leaves eight possible same-sign external A/B
pairs, and each leaves 3! cross bijections, giving 10·8·3!=480. This
includes external negative A--a pairs, which a selected-column-only
normalization would incorrectly discard for the full-family argument.

## 5. Independent six-core certificate for the 1,584 forms

The generator
[`d17_feedback_round6_certificate.py`](d17_feedback_round6_certificate.py)
selects one full row per case and records a contradiction from each of
its six cores. It uses no SAT solver and does not enumerate second
matchings. For a forced partial matching K and a required five-set S,
the only rules are

    at most |K inside S| + floor(|S minus endpoints(K)|/2)
    internal N-edges can lie in S;

and, if K has one internal edge and exactly two free S vertices, those
vertices must be paired. A capacity below two is a contradiction.

The independent stdlib-only checker
[`d17_feedback_round6_check.py`](d17_feedback_round6_check.py) imports
neither the generator nor any prior proof code. It enumerates the
near-perfect matchings at widths twelve/fourteen and filters exactly the
canonical forms, proving completeness and uniqueness of the list. It
then directly replays signed transport, verifies which of all twenty
states miss their first peak, reconstructs each row's six cores, and
checks every arithmetic inference.

The [certificate](results/d17-feedback-round6-core-certificate.json) has
1,584 cases and 9,504 branches. Of the branches, 4,395 end immediately
and 5,109 use exactly **one** forced edge before contradiction. The
[independent report](results/d17-feedback-round6-core-check.json) is
VERIFIED. Its certificate SHA-256 is
`1d5b34c2cd2f6cc9a36f26aa44aac5ba7894e1ddc452381d6c3f830d1ee808fa`.
Generation and checking had separate thirty-second limits and completed
in 0.200 and 0.145 seconds respectively, with exit zero; the
[terminal record](results/d17-feedback-round6-certificate-terminal.json)
is saved. This finite arithmetic classification is the explicit
non-hand premise of the new mixed-idle closure.

The separate small corroboration
[`d17_feedback_round6_hand_verify.py`](d17_feedback_round6_hand_verify.py)
checks all 2,100 critical AA-idle first matchings at widths twelve and
fourteen. Their BC/BD signatures are always ordinary (1,860) or
single-transfer (240), exactly as proved in Section 2. It also verifies
the first-peak/full-row claims for the 1,584 canonical mixed cases and
replays the six positive controls below. Its
[report](results/d17-feedback-round6-hand-check.json) and
[terminal record](results/d17-feedback-round6-hand-terminal.json) are
saved; it finished in 0.079 seconds. Those checks corroborate the hand
lemmas rather than establish their arbitrary-width scope.

## 6. Why a fourth B column matters

The three selected columns genuinely admit covers in the mixed-idle
branch. In the base twelve-wire labels

    (D,A,B,C,E,d,a,b,c,q,e,r) = (0,1,2,3,4,5,6,7,8,9,10,11),

one example is

    M = {0--11,1--7,3--10,4--6,5--8},      idles {2,9};
    N = {0--4,1--9,2--11,3--6,5--7,8--10}.

Every qbc/qce/rce state has at least three RR comparisons in one of the
layers, but the qab states in rows BC and CE have only two in each.
A second pattern has idles {3,10}. The
[positive-control record](results/d17-feedback-round6-three-column-controls.json)
contains both first matchings and all three completions of each
surviving four-edge core; all six cover the selected columns and fail
only qab states. They are not covers of the full case-606 family.

This explains why the certificate keeps all twenty states and why the
full-family contraction test in Section 4 is necessary. The 1,584-case
certificate proves the mixed branch without extrapolating a false
three-column obstruction.

## 7. Scope after round six

Comparable-idle augmentation sends every hypothetical critical cover
to a perfect or two-idle first matching while preserving dc. The perfect
case is excluded by rounds three through five. The two-idle case with
at most one cross is excluded by round three; AA idles are excluded by
the hand argument in Section 2; B-a idles reduce to the selected perfect
case; and the remaining mixed idles reduce to the independently checked
1,584 forms. Thus the entire critical-dc branch is excluded at arbitrary
even width, with the finite premises from rounds five and six explicit.

The remaining case-606 structural gap is the noncritical mixed branch.
A fully symbolic theorem must also replace the 1,080-case round-five
and 1,584-case round-six classifications. The full case-608 hand gap and
the complete D17/D18 lower-bound goals remain open. No new SAT job was
started in this round; every bounded discovery/check process is terminal.
