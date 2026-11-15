# Sorting networks: depth lower bounds, and the $D(11)\ge8$ question

A research bundle on **optimal depth** of sorting networks: how the depth bounds for $1\le d\le8$ are
proved, what general properties of depth-optimal networks do the work, and why the last open bound in that
range resists.

## What is here

```
results/
  depth-lower-bounds-small-n.md   the main document: the reduction, the toolbox T1-T11,
                                  the five frontier bounds with several proofs each,
                                  and an honest accounting of what is new (§10)
  d11-handoff.md                  START HERE for the D(11) question: why it is hard,
                                  every failed strategy and the result that rules it out
  d11-block-lemma-route.md        D(11), strategy A: block lemma, Lemma H, the residual (R)
  d11-image-size-route.md         D(11), strategy B: image size, Lemma S, four no-go theorems
  d11-compression-structure.md    D(11), strategy C: factorization theorems, local ratios
  sorting-network-lemma-compendium.md   the lemma compendium from the literature (A1..G3)
  sorting-networks-size.md              companion on minimal size (S1..S12)
code/
  README.md                       per-script table: what each check establishes and its cost
  verify.sh                       re-runs every cheap check in about a minute
  *.c, *.py                       the checks themselves
```

## Status in one line

$D(1..17)=0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10$. The bounds through $D(10)\ge7$ are derived by hand in
`results/depth-lower-bounds-small-n.md`, but from $D(7)\ge6$ on the arguments take computer-found size
values as input ($S(7)=16$, $S(9)=25$). **$D(11)\ge8$ is not proved**; it is known computationally
(arXiv:1310.6271, 1412.5302, SAT), and `results/d11-handoff.md` records why three strategies failed and
what a next attempt must avoid.

## Running the checks

```sh
cd code && ./verify.sh      # ~1 min, needs gcc and python3
```

Nothing here needs a SAT solver; `code/sat_encode.py` emits CNF instances if you have one.

## Conventions

Channels are numbered 0..n-1 in the code and 1..n in the prose. A *layer* is a matching of comparators
$(i,j)$, $i<j$, minimum to $i$. A *maximal layer* has $\lfloor n/2\rfloor$ comparators. $D(n)$ is the
minimum depth, $S(n)$ the minimum size.

## Corrections (2026-11-14)

Size records were checked against Dobbelaere's list of sorting networks (October 2026), and the record
networks for $n=11..17$ were re-run on all $2^n$ inputs. The original text is in
`../sorting-networks-depth.zip`.

* **Counting is closed at $n=17$ too.** `results/d11-handoff.md` §3 and §6.1, `code/closed.py` and
  `code/README.md` used $S(17)\le74$ and concluded that capacity was open at 17. But 74 is the smallest
  known *10-layer* network: a 71-comparator network exists, and capacity would need $S(17)\ge73$.
  `closed.py` had used the smallest *depth-optimal* sizes for $n=13..17$ (46, 52, 57, 61, 74); it now
  uses the smallest of any depth (45, 51, 56, 60, 71) and reports all three frontiers closed.
* **Lemma S's target is open.** The handoff §5.3 called $\min|F_6|\ge18$ true. Only $\min|F_6|\le23$ is
  known, and the hypothesis of Lemma S implies $D(11)\ge8$ without being implied by it. Matching fixes in
  the handoff §10, `results/d11-compression-structure.md` §3.4, and the table in
  `results/d11-image-size-route.md` §2.2, whose column "exact" is now "smallest found".
* **Harder proved the lower bounds.** arXiv:2012.04400 shows that $S(11)=35$ and $S(12)=39$ are optimal;
  the networks themselves are classical. The handoff §9 credited it with the upper bounds, and
  `results/depth-lower-bounds-small-n.md` §1 said $S(11)$ was open. Related wording changed in the
  handoff §3 and §6; `closed.py` now treats $S(11)$ and $S(12)$ as known.
* **"By hand" qualified.** From $D(7)\ge6$ on, the hand arguments use computer-found size values
  ($S(7)=16$, $S(9)=25$): the status line above, and `results/depth-lower-bounds-small-n.md` §4.
* **Small slips.** `closed.py`'s sentinel threshold was one too low when $(d-1)(n-2)$ is even (44 instead
  of 45 at $n=13$; no verdict changed). In the 4-channel counterexample (`results/d11-block-lemma-route.md`
  §1, compendium C4) the state after two layers on input $1100$ is $0011$, and six inputs, not nine, leave
  two blocks mixed. Also a dangling "§6.5" (handoff §5.3), "at most 2048 states" where 486 was meant
  (`results/d11-block-lemma-route.md` §3), and a 46-comparator network at $n=13$ where 45 is known
  (handoff §3).
