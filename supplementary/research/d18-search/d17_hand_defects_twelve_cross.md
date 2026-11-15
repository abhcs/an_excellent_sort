# Safe B images: all small first matchings and further cross-edge branches

**Later completion.** The [four-gate and perfect arguments](d17_feedback_twelve_structure.md)
and [five-gate argument](d17_hand_defects_twelve_five.md) close all branches
left by this note. Its narrower criteria and counts below are retained
as intermediate lemmas; they are not the current overall proof status.

**Result.** In the twelve-wire case-607 obstruction, the first matching
must have at least four gates. This is now a hand consequence of sentinel
transport. In addition, a perfect first matching must have at least three
A--B edges, with a stronger restriction when there are exactly three.
The criteria below also exclude every five-gate first matching with at
most one A--B edge.

These statements concern the signed family in
[d17_hand_defects_twelve.md](d17_hand_defects_twelve.md):

    A={4,5,6,7,8}, B={10,11,12,15,16}, U={1,2},
    G={56,67,78,46}.

There are two A sentinels on an edge of G, and one B sentinel at any B
vertex. Signs are 4+,5-,6-,7+,8+ and 10+,11-,12+,15-,16+. Every other
wire is real. A peak is four real-real gates in M or in the following
matching N after exact transport by M.

We fill only N, which is safe because it is the last counted matching.
For this perfect N, peaking is equivalent to pairing two of the three
sentinels. We do not fill M.

## 1. Two common third positions force a matching graph

Let H be a graph of possible pairs of sentinel positions, and let p,q
be two distinct positions outside all vertices of H. Suppose a matching
N pairs two sentinels in each of the triples

    {u,v,p}, {u,v,q}       for every uv in H.

**Two-image lemma.** H is a matching.

*Proof.* If uv is not an N-edge, the two triples force N to contain
up,vq or uq,vp. The endpoints u,v therefore cannot participate in any
other required H-edge: such an edge could be neither an N-edge nor a
second bypass using the same N-partners of p and q. Every H-edge that
is an N-edge is disjoint from every other one. Hence all H-edges are
disjoint. ∎

Two common third positions do **not** force the particular edge uv into
N: N={up,vq} satisfies both triples without uv. The conclusion is about
the whole required-pair graph. This distinction is tested in the checker.

## 2. Safe B choices and their exact image count

For a singleton sentinel at v, define f(v) to be its position after M:
the smaller endpoint for a minus sentinel, the larger endpoint for a plus
sentinel, and v if idle. Two distinct positions have the same image only
when they are the endpoints of an M-edge and have the same sign.

Let

* c be the number of A--B edges of M;
* b be the number of B--B edges whose endpoints have equal signs;
* z be the number of idle B vertices.

Call a B choice **safe** if that B vertex is not paired to A. Its image
is disjoint from every A singleton image, since it belongs to a different
M-block. For an A-edge uv outside M and a safe B choice w, the three
transported sentinel positions are exactly

    {f(u),f(v),f(w)}.

There are 5-c safe B choices. Their only image identifications come from
the b same-sign B--B edges. Thus the number of distinct safe images is

    t=5-c-b.                                             (1)

If only used safe B vertices are retained, the number is

    t_used=5-c-b-z.                                      (2)

This count is exact, including idle vertices and B--U comparisons.
It is a sufficient notion of safety; an opposite-sign A--B edge can
provide additional safe behavior, which is outside this note's criteria.

## 3. The folded fork is never a matching

For every M, including matchings with cross edges, let H contain the
folded pair f(u)f(v) for each G-edge uv outside M. Then **H is not a
matching**.

If none of 65,67,64 belongs to M, its three edges at f(6) would need
f(5)=f(7)=f(4) for H to be a matching, impossible because an image has
at most two preimages. If 67 belongs to M, the other neighbors 5- and
4+ cannot coalesce. If 64 belongs to M, neighbors 5- and 7+ cannot
coalesce. Therefore the only possible escape is M-edge 65, together
with M-edge 47 so that the remaining neighbors coalesce.

But then H contains 57 and 7f(8), two distinct incident edges. The
M-blocks 65 and 47 ensure f(8) is neither 5 nor 7. Contradiction.

This proof uses only the signs and the disjointness of M-edges. A--B
edges elsewhere do not affect it.

We will also use the following version when M has five gates: remove
from H any G-edge whose two endpoints are idle in M. The resulting H
is still not a matching. There are only two idle vertices, so at most
one edge is removed. The center argument above is unchanged unless that
edge is incident to 6. Only a removed edge 65 could leave coalescible
neighbors 4,7; then M-edge 47 is forced, and the conflicting folded edges
67 and 7f(8) remain. If the removed edge is 78, the center argument would
force M-edge 47, contrary to 7 being idle. The opposite-sign cases at
64 or 67 still fail.

## 4. Every first matching of size at most three fails

Let m=|M|<=3. No restriction peaks in M, so every restriction must peak
in N after transport. Moreover c+b<=m, and (1) gives t>=2. Choose any
two distinct safe B images.

For every G-edge outside M, both corresponding transported triples must
peak in N. The two-image lemma says that the folded graph H is a
matching. Section 3 says it is not. Contradiction. ∎

This proves m>=4 for a putative solution. It does not rely on the false
shortcut that N sees the original family when M has too few gates to
peak; M's transport is included throughout.

## 5. Larger first matchings

The same argument yields useful sufficient rejection criteria.

**Every A vertex used.** For a G-edge outside M, its two sentinels occupy
two distinct M-edges. A safe B sentinel occupies a third M-edge if used.
Thus its retained count is

    m-2-1_{B sentinel is used} <=3.

For m=6 all B vertices are used; for m<=5 the inequality holds even
for an idle B sentinel. Hence, if every A vertex is used and t>=2,
all required folded edges again contradict the two-image lemma.

**Perfect M.** This is the preceding case. Consequently

    c+b>=4.                                             (3)

Since c+2b<=5, condition (3) implies c>=3. If c=3, the remaining two B
vertices must be paired to each other and have equal signs. Thus all
perfect-M cases with c<=2, and all c=3 cases without that same-sign
B--B edge, are excluded by hand.

**Four gates.** If t_used>=2, choose two used safe B images. A used B
sentinel already removes at least one of M's four gates from the
real-real count, so no such state peaks in M. All folded G-edges outside
M need N, contradicting Sections 1 and 3.

**Five gates.** If t_used>=2, an A-edge outside M with at least one used
endpoint, together with a used safe B sentinel, hits at least two
M-edges. Its retained count is at most three. The required folded graph
omits only edges joining two idle A vertices. The extended fork lemma
in Section 3 again gives a contradiction.

In particular these criteria exclude every five-gate M with c<=1.
For c=0 the earlier no-cross theorem applies. For c=1, if t_used>=2
we are done. Otherwise b+z>=3. Since there are only two idle vertices
and at most two same-sign B--B edges, the only possible case is b=1,z=2:
b=2 would use all four non-cross B vertices and force z=0. With z=2
all A vertices are used and t=3, so the all-A-used criterion applies.

## 6. Exact checks and remaining branches

`d17_hand_defects_twelve_cross_verify.py` checks these statements against
all 140,152 first matchings on the twelve labelled wires. It does not
search for N or use SAT. It verifies the safe-image counts, the two fork
claims, and each asserted failure of a first peak. The
[record](results/d17-hand-defects-twelve-cross-safe.json) is `VERIFIED`.
The proof does not use this enumeration as a premise.

The small-M theorem covers 15,412 first matchings, of which 11,700 have
cross edges. Combining this note's criteria with the previous no-cross
proof leaves the following labelled first matchings unclosed **by these
hand criteria**:

| First size m | Cross-edge counts still present | Count |
|---:|---|---:|
| 4 | 1,2,3,4 | 22,560 |
| 5 | 2,3,4,5 | 11,520 |
| 6 | 3,4,5 | 2,040 |

These are remaining cases for a hand proof, not relaxation survivors:
the full twelve-wire statement already has a checked UNSAT certificate.
The stronger safety analysis for opposite-sign cross edges and the
remaining large-cross patterns can reduce this list further. None is
silently treated as covered here.
