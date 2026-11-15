# Three sorted triples cannot be merged in four layers

**Theorem.** A comparator network merging three independently sorted
triples requires at least five layers.

The proof uses only the hand H6 profile: a six-wire depth-five
sorter whose first layer has three comparisons has at least two
comparisons in its second layer. H6 follows from D(5)>=5 and the
five-wire thin lemma, as recalled in the
[previous hand proof](h9_feedback_round2_031246.md#3-the-exceptional-forms-force-incompatible-six-real-pairings).

Suppose a four-layer merger exists, and call its first matching N.
Delete comparisons within an input triple, since those never fire.
In each sorted triple call its middle position a *middle*, and its
other two positions *endpoints*.

Keep either adjacent pair of each triple, replacing the remaining
endpoint by the appropriate signed infinity. There are eight
restrictions, each leaving six reals presented as three sorted
pairs. A single layer of three pair comparisons creates all such
inputs. Prefix it to the restricted four-layer merger. H6 therefore
requires N to have at least two RR edges in **each** restriction.

Sum these eight demands. An N edge joining two middles belongs to
all eight real sets; a middle--endpoint edge belongs to four; an
endpoint--endpoint edge belongs to two. No internal-triple edge is
present. Thus their respective weights are 8,4,2, and the required
sum is at least 16.

There are three middles and N has at most four edges. If N has no
middle--middle edge, at most three edges have weight 4 and any
fourth has weight 2, for a total at most 14. If N has a
middle--middle edge, the remaining middle allows at most one
weight-4 edge. The total is at most

```
8 + 4 + 2 + 2 = 16.
```

Equality is necessary. Hence N has exactly one middle--middle
edge, one middle--endpoint edge, two endpoint--endpoint edges,
and one idle endpoint v. Moreover every one of the eight
restrictions has exactly two RR edges.

Let A be the triple containing v, and let u be A's other endpoint.
Consider the four deletion triples choosing u and one endpoint
from each of the other two input triples. All three deleted
endpoints are used by N. Since exactly two of N's four edges must
remain RR, these three endpoints must occupy exactly two N edges.
Therefore each of the four deletion triples contains an
endpoint--endpoint edge of N.

This is impossible. At most one of the two endpoint--endpoint
edges can use u, and such an edge occurs in only two of the four
deletion triples. Any other edge uses neither endpoint of A
(v is idle), so it occurs in at most one of the four. The two
edges cover at most three deletion triples. Contradiction. □

The theorem also excludes any four-layer merger with a larger
input family containing three independently sorted triples, for
example a family obtained by splitting one or more of the triples
into smaller sorted blocks. It is a reusable obstruction, not by
itself a new full second-layer class of H9.

The [checker](verify/h9_feedback_round3_merge333.py) verifies the
eight restrictions, the edge weights, the equality shapes and the
four-deletion cover bound. Its exhaustive matching cross-check is
corroboration; the counting proof above does not depend on it.
