# Incremental two-run interval tests: correct, but no speedup yet

The full interval formulas remain preferable in the tests recorded here.
Incremental two-run witnesses reduce the initial formula but did not
refute either tested whole prefix within the wall limit. No additional
D13 or D18 cover case is closed by this experiment.

## Mathematical condition

Let f_c be the Boolean function on wire c at a cut, and write |x| for
the number of ones in an input. The established rank-interval lemma gives

    lo(c) = n - max{|x| : f_c(x)=0} - 1,
    hi(c) = n - min{|y| : f_c(y)=1}.

Consequently, for an integer cap K,

    hi(c)-lo(c)+1 <= K

is equivalent to the family of two-run implications

    |x|-|y| >= K-1  ==>  f_c(x) >= f_c(y).                 (1)

For K=4, a violation is a zero on an input with at least three more ones
than an input producing one. The two inputs need not be coordinatewise
comparable. This is a reformulation of the existing interval lemma,
not a new lower-bound theorem.

A wire can reach at most 2^s output positions through s remaining
matching layers. Thus every sorting completion satisfies (1) with K=2^s.
The condition and the algorithm work for arbitrary n and cut depth.

The fixed prefix preserves Hamming weight, so its complete image set
suffices in place of all raw binary inputs. Every image vector used by
the oracle has an original input preimage of the same weight.

## Incremental formulations

[endpoint_cegar.py](endpoint_cegar.py) synthesizes the free layers up to
the cut. A bit-parallel oracle evaluates each candidate on the **entire**
prefix image and finds exact endpoints and their two witnessing inputs.
It then adds violations in either of two forms:

* **Endpoints:** introduce each new input trace once and constrain the
  shared interval endpoints using that trace on every wire. The selected
  wire bounds are present from the start.
* **Pairs:** introduce the two input traces and add only the violated
  instance of (1), without endpoint variables.

Each addition is necessary for every sorting completion. Thus UNSAT
excludes the whole fixed prefix; a candidate passing the exact oracle
only satisfies the selected interval condition. A timeout establishes
neither conclusion. The unused final layers impose no ending-routing
conditions. The inherited redundancy rules delete functionally
redundant comparisons and preserve the named cut-wire functions.

## Bounded results

| Whole prefix / formulation | Terminal result | Traces added | CNF clauses |
|---|---|---:|---:|
| D13 case116, ten wire endpoints | 60 s timeout | 203 / 735 | 112,810 |
| D13 case116, individual pairs | 42 s internal limit | 719 / 735 | 329,608 |
| D18 case410, eighteen wire endpoints | 60 s timeout | 250 / 9,261 | 495,891 |

The [D13 endpoint run](results/endpoint-cegar13-r0116-endpoints.json)
completed fourteen candidate checks before the final interrupted solve.
The [pair run](results/endpoint-cegar13-r0116-pairs.json) completed 586
candidate checks and accumulated 5,194 pair obligations. The
[D18 run](results/endpoint-cegar18-r0410-endpoints.json) completed nine
candidate checks. Exact oracle evaluation took less than 0.03 seconds
in total in each run; synthesis, rather than counterexample discovery,
is the bottleneck in these tests.

For comparison, the existing full-input D13 case116 formula uses
341,202 clauses and has a checked 19.79-second build/solve/export result.
These are recorded runs, not a controlled benchmark; they do not
support replacing the full formula by this incremental method.

The hard caps are enforced by
[endpoint_cegar_bounded.py](endpoint_cegar_bounded.py). Interrupted
children are killed and reaped. In interrupted worker reports, `seconds`
is the last saved checkpoint; `worker_terminal.wall_seconds` is the
actual bounded process duration. All listed trials are terminal.

## Validation

The independent scalar controls in
[endpoint_cegar_verify.py](endpoint_cegar_verify.py) compare exact
endpoints, all relevant input-pair inequalities, and both fixed-network
SAT encodings on 64 small random prefix/continuation pairs. Across two
caps and two encodings, all 256 checks agree: 98 SAT and 158 UNSAT, with
134,107 scalar wire-pair checks. This is a control suite, not an
exhaustive proof of the implementation.

The known depth-nine sorter extending D13 case116 is independently
checked on all 8192 binary inputs and passes the cut-seven oracle in
[the positive control](results/endpoint-cegar13-d9-positive.json).
Its fixed cut needs no added constraints because the very first
candidate satisfies the interval condition.

Both formulations also refute the five-wire, depth-two negative
control. Their incremental DRAT traces are independently verified
against the exported final CNFs:
[endpoint certificate](results/endpoint-cegar5-negative-endpoints.json)
and [pair certificate](results/endpoint-cegar5-negative-pairs.json).
These small checks exercise proof export after incremental additions;
the two main D13/D18 timeout trials produce no UNSAT certificate.

The useful next direction is to exploit the smaller **semantic wire
sets** found by full formulas and prove why those wires must contain a
wide interval. Naively adding fewer input traces does not yet address
that universal hand-proof step.
