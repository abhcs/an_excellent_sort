# Encoding attainable-rank intervals and recording larger-case limits

The [probe tests](certificate-guided-frontier.md) use the necessary bounds
that each rank has at most four possible positions and each wire has at
most four possible ranks when two layers remain. This note records an
equivalent interval encoding and its limits. It closes no additional
D(13), D(17) or D(18) cover case.

## Exact interval endpoints

For a wire c computing the monotone Boolean function f_c, let a_c be the
least number of input zeros capable of making f_c=0, and b_c the least
number of input ones capable of making f_c=1. Its attainable ranks are
exactly

\[
Q(c)=[a_c-1,n-b_c].
\]

The endpoints follow from thresholding input permutations. There are no
gaps: input permutations are connected by exchanges of consecutive rank
labels, and such an exchange changes the output value on any fixed wire
by at most one. A standard prefix fixes the sorted permutation, so
c itself is in Q(c).

Consequently a particularly short obstruction consists of just two runs:
the same wire outputs zero on an input with a zeros and one on an input
with b ones, where a+b <= n-3. Its attainable interval then has length
at least n+2-a-b >= 5, which is incompatible with a two-layer suffix.
This uses the existing attainable-rank interval lemma, not a new bound
on the forcing-set sizes themselves.

## The endpoint formula

The implementation [interval_frontier.py](interval_frontier.py) chooses
an enclosing interval [lo(c),hi(c)] for each wire. It represents the
thresholds lo(c)>=k and hi(c)<=k, enforces monotonicity, nonemptiness,
lo(c)<=c<=hi(c), and width at most four. Every simulated cut-state zero
at weight w forces lo(c)<=n-w-1; every one forces hi(c)>=n-w.

For every rank k, at most four of the chosen intervals may contain k.
The optional routing condition requires all these intervals to be
compatible with the same two ending matchings. These are necessary
conditions; a satisfying assignment is not automatically a sorter.

[interval_frontier_checks.py](interval_frontier_checks.py) independently
compares the endpoint formula with all binary probes on 60 specified
small random networks. It passes 27 positive and 33 negative controls.
The known thirteen-wire depth-nine sorter is another positive control,
with all 8192 binary inputs verified. See
[the check audit](results/interval-frontier-checks.json) and
[the sorting positive control](results/interval-frontier13-d9-positive.json).

## Terminal results

| Test | Result |
|---|---|
| D13 case116, cut6, endpoint bounds and common routing | UNSAT in 6.98 s; solver result only, already covered by the previous checked structural certificate |
| D18 case410, cut8, original full-probe routing | 180-second timeout |
| D18 case410, cut8, endpoint bounds and common routing | 120-second timeout |

The D18 formulas have respectively 15,877,632 and 15,541,053 clauses.
These are large structural encodings, and neither run establishes
satisfiability or unsatisfiability. Their terminal records are
[the full-probe result](results/probe-cover18-r0410-resumed/result.json)
and [the interval result](results/interval-frontier18-r0410.json).
No solver from these trials remains running.

The useful contrasting result is the much smaller
[D17 defect screen](d17_feedback_results.md), which closes three cases
with checked certificates. Its [twelve-wire pattern](fixed-sentinel-obstruction.md)
and the hand projection lemma are better candidates for structural
applications to D18 than simply increasing the time limit on the large
rank formulas. No claim that the pattern is unavoidable on D18 has been
established.
