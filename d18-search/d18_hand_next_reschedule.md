# A bounded D18 sixth-layer screen using retained depth two

**Outcome.** The strengthened rescheduling condition rejects the first five
layers of `combined-prefix-probe18.json`, already excluded by the separate
[four-restriction hand proof](commuting-prefix-hand-proof.md). Three other
saved five-layer prefixes have directly replayed sixth-layer survivors.
This experiment excludes no additional complete two-layer cover case and
does not prove the full D18 lower bound.

## The necessary condition

Fix any five-layer prefix of a hypothetical depth-ten sorter. Choose seven
or eight real inputs and put signed infinities on the other inputs. Follow
logical real **register tracks**, moving their labels through real-sentinel
comparisons by the fixed routing. At a retained real-real comparison, the
two register values change but their labels remain fixed.

A useful exact normalization is the following. If both participating
register tracks most recently participated in the same retained comparison
with each other, their values are still the ordered minimum and maximum of
that pair. A new comparison of that pair is redundant. If its orientation
is reversed relative to those register values, delete it and swap the two
output register labels. This is a fixed routing change, independent of all
real values. The previous comparison remains in the normalized circuit.
Other real comparisons are retained. Sentinel-sentinel ties have no effect
on the real registers.

Give a retained gate level `1 + max(level of its two input tracks)`, starting
all real tracks at level zero. Gates at the same level have disjoint logical
tracks. Consequently a normalized circuit of maximum level at most two can
be rescheduled into two matching layers, followed by its fixed output
routing. Repeated-gate deletion does not assume that the whole prefix has
disjoint two-track components: the mutual-most-recent condition is local.

Suppose the normalized first five layers have at most two levels and `T`
gates. Let `R` be their physical real-position set, `D` the physical real
positions at level two, and `E` the physical pairs whose two logical tracks
most recently met each other. For a proposed original sixth matching `M`,
put

```
A = {ab in M: a,b in R and ab not in E}.
```

Exactly the gates in `A` survive the same normalization in L6. If one meets
`D`, the normalized circuit has at least three levels. Otherwise the first
six original layers reschedule into two layers with exactly `T + |A|`
gates. Original layers L7 through L10 then yield a sorter on seven or eight
reals in at most six layers, after pruning and untangling. The hand
[early-profile theorem](../depth-hand-proofs/h7-early-profiles.md) requires
at least five gates in its first two layers for seven reals, and at least
seven for eight reals. Therefore every proposed L6 must satisfy

```
some edge of A meets D, OR |A| >= threshold - T,
where threshold = 5 on seven reals and 7 on eight reals.
```

This also handles normalized depth zero or one by padding the rescheduled
prefix to two layers. It is safe to omit restrictions with depth above two
or `T` already reaching the threshold. These omissions weaken the screen.
In particular, survival does not say that any depth-ten completion exists.

## Four bounded tests

The new [collector](d18_hand_next_reschedule_states.cpp) enumerates all
normalized signed placements on the first-layer pairs: 1,538,352 with seven
reals and 1,135,242 with eight reals per tested prefix. It retains the cases
with normalized depth at most two and `T < threshold`. Conditions are
deduplicated by `(R,D,T,E)`; one explicit initial placement and the complete
normalized register circuit are saved for every condition.

The [solver driver](d18_hand_next_reschedule.py) uses only the 153 possible
L6 edge variables, matching constraints, and auxiliary cardinality variables.
It adds no prefix normal forms, no complete-sorter constraints, and no
assumption that L6 is perfect. Every solver subprocess and DRAT checker has
a hard 30-second wall cap. All jobs below exited normally.

| Five-layer prefix | Distinct conditions | Outcome | Worker time |
|---|---:|---|---:|
| combined-prefix-probe18, first five | 1544 | UNSAT, nine-group core, DRAT verified | 0.14 s |
| symbeam_pb_d5, zero-based row 0 | 40 | SURVIVOR | 0.06 s |
| symbeam_pb_d5, zero-based row 16 | 23 | SURVIVOR | 0.06 s |
| symbeam_pb_d5, zero-based row 32 | 108 | SURVIVOR | 0.06 s |

Restricting the combined-prefix formula to its sixteen seven-real
restrictions with `T=2` also gives UNSAT, with a deletion-minimal five-group
core and an independently checked DRAT proof. These include both depth-one
and depth-two retained circuits. This auxiliary core is not claimed to be
minimum or to improve on the existing four-restriction hand proof.

The three saved L6 survivors are:

```
beam00: (0,1)(2,3)(4,5)(6,7)(8,9)(10,11)(12,13)(14,15)(16,17)
beam16: (1,2)(3,8)(4,5)(7,9)(10,11)(12,13)(14,15)(16,17)
beam32: (0,1)(2,8)(3,7)(4,5)(6,9)(10,14)(11,15)(12,13)(16,17)
```

For each representative restriction, an independent Python register replay
reconstructs the normalized prefix, checks the collector's exact routing,
levels and repeated-pair set, and replays the survivor L6. All representatives
are also checked on every binary assignment to their seven or eight real
inputs: **252,416 direct functional comparisons** pass. This checks the
reversed-repeat routing, not just the ternary real-position sets. Since all
coordinates are min/max expressions, the same identities for arbitrary
real values also follow from the threshold principle; the local min/max
argument above is their direct proof.

The [verification report](results/d18_hand_next_reschedule-verification.json)
and [terminal audit](results/d18_hand_next_reschedule-audit.json) bind the
inputs and sources by hash. The two independently checked UNSAT certificates
are under
`results/d18_hand_next_reschedule-combined-certificate/` and
`results/d18_hand_next_reschedule-combined-thin-certificate/`.
Each test has a separate `*-terminal.json`; the auxiliary thin-family run
has its own terminal record too.

## What this adds and what remains

The reusable result is an exact local repeated-pair normalization and a
small next-matching condition based on the normalized retained dependency
depth. It applies even when the retained prefix does not compress to a
single layer. The experiments show that this condition is compatible with
three sampled beam prefixes, so it cannot by itself close those prefixes
at L6. Only the already hand-excluded combined prefix was rejected here.
No run timed out, no survivor was called a sorting network, and no live
solver process remains from this experiment.
