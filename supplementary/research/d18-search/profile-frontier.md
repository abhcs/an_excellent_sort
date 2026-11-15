# What the early-profile lemmas do and do not close

The [seven/eight-wire hand proof](../depth-hand-proofs/h7-early-profiles.md)
gives a stronger necessary condition than first-layer nonemptiness:
the first two layers of a depth-six seven-wire sorter have sizes
$(2,3),(3,2)$ or $(3,3)$. For eight wires at depth six the profiles
are $(3,4),(4,3),(4,4)$.

This note records direct tests of those constraints inside larger
networks. **No D(13), D(17) or D(18) bound is closed by these tests.**

Subsequent [certificate-guided probe tests](certificate-guided-frontier.md)
exclude two complete D(13) prefix cases with independently checked proofs.
Those use rank-position and common-ending constraints; the count-profile
tests originally reported in this note eliminate no cases. A subsequent
[defect encoding of the H9 condition](d17_feedback_results.md) excludes
three D(17) cases with independently checked certificates.

## D(13): every two-layer prefix has a compatible continuation of profiles

A hypothetical depth-eight thirteen-wire sorter leaves a depth-six
seven-wire sorter under every placement that blinds its first two
layers with six sentinels. Hence every such placement has one of the
three seven-wire profiles in original layers 3 and 4.

The complete saturated/reflected prefix cover has 117 cases. Its
[manifest](prefixes/complete13.summary.json) records digest
`2e3dec7b0d501a15ed9871a024d647c89526945f3ad263d3360ce983279f8406`.
For every case, `profile_frontier.py` found two matching layers meeting
the profile condition for the entire half-blind family simultaneously.

The [audit](results/profile-frontier13/audit.json) has **117 SURVIVOR**
results. A [separate direct replay](results/profile-frontier13-independent.json)
checked all 117 matching pairs and all 265 retained profiles, without
using the SAT encoding. These are witnesses that the profile constraints
are compatible, not sorting networks. Thus this particular two-layer
screen cannot eliminate any of the 117 prefix cases. Further layers,
other sentinel counts, or actual comparisons among the reals are needed.

## D(17): three bounded trials remain inconclusive

A hypothetical depth-nine seventeen-wire sorter leaves a depth-seven
nine-wire sorter under each eight-sentinel half-blind placement. All
seven remaining layers must be nonempty, by $D(9)\ge7$. H9 additionally
forces at least one of the first two retained layers to contain four
comparators. H9 is an established computer-assisted result in this
workspace, not a new hand theorem here.

The [seventeen-wire cover](prefixes/complete17.summary.json) has 609
cases, with digest
`711b620bb298deee98e5520595cfb341a13cf3600f4297dd35f3b38cb11d2100`.
The three largest half-blind families each have 20 members, in cases
`n17-r0606`, `n17-r0607` and `n17-r0608`.

Each [five-second trial](results/profile-frontier17-largest/audit.json)
timed out. A [sixty-second Kissat retry](results/profile-frontier17-case606-retry/audit.json)
of case 606 also timed out. That relaxation has 6,946 variables and
41,064 clauses. It is a two-layer structural problem, not a full
seventeen-wire sorting encoding. These results do not establish whether
the profile constraints are satisfiable. These runs eliminate no D(17) case.
The later defect encoding solves cases 606, 607 and 608 in 7–14 seconds;
see the [checked results](d17_feedback_results.md). It expresses the same
H9 condition through the number of real wires not paired with another real.

## Encoding scope

The first two layers are fixed by a cover case. The next two are arbitrary
matchings. Sentinels propagate exactly as ordered types using two threshold
bits, and a gate is counted precisely when both incoming wires hold
reals. The model excludes immediately repeated gates, which can be
deleted from any sorter. It does not fill a middle layer or impose
self-duality on a completion.

An UNSAT answer would refute the corresponding complete-cover case,
provided the encoding were validated for that use. No UNSAT answer was
obtained by the original encoder. SAT only supplies the profile witnesses described above.
Child processes impose wall limits, and timeouts never count as proofs.

```sh
python d18-search/profile_frontier.py --cover d18-search/prefixes/complete13.jsonl \
  --out /private/tmp/profile13-new --seconds 5
python d18-search/profile_frontier.py --cover d18-search/prefixes/complete17.jsonl \
  --out /private/tmp/profile17-new --min-family 20 --seconds 5
```

Use the Python environment with python-sat. These runs are terminal;
no background solve is required to read or check their artifacts.
