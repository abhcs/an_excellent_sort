#!/usr/bin/env python3
"""Are the two general inequalities CLOSED at a frontier?

At a frontier (n,d) capacity gives d only if S(n) >= (d-1)*floor(n/2) + 1, and the sentinel
inequality only if S(n-1) >= (d-1)*(n-2)//2 + 1.  If an explicit n-channel network with fewer
comparators than that is known, the inequality can never reach d, no matter how the size
bounds improve.  This is the computation behind section 3 of d11-handoff.md.

Size lower bounds: the known values S(1..12) = 0,1,3,5,9,12,16,19,25,29,35,39 (11 and 12 are
Harder's computer-assisted result, arXiv:2012.04400), then van Voorhis S(n) >= S(n-1) + ceil(lg n).
Size UPPER bounds: the smallest known network of ANY depth, from Dobbelaere's list
(https://bertdobbelaere.github.io/sorting_networks.html); the 11..17 networks were re-checked on
all 2^n inputs on 2026-11-14.  An earlier version used the smallest known depth-OPTIMAL networks
(46, 52, 57, 61, 74 for n=13..17), which made capacity look open at n=17.
"""
import math

S_known = {1:0,2:1,3:3,4:5,5:9,6:12,7:16,8:19,9:25,10:29,11:35,12:39}
def s_lower(n):
    S = dict(S_known); k = max(S_known) + 1
    while k <= n:
        S[k] = S[k-1] + math.ceil(math.log2(k)); k += 1
    return S[n]

# size of the smallest known n-channel sorting network of any depth (upper bound on S(n));
# for n <= 12 the value is known exactly
S_upper = dict(S_known); S_upper.update({13:45, 14:51, 15:56, 16:60, 17:71})

FRONTIERS = [(11,8), (13,9), (17,10)]

def main():
    print("capacity:  d >= ceil(S(n)/floor(n/2));  needs S(n) >= (d-1)*floor(n/2)+1")
    for n, d in FRONTIERS:
        need = (d-1)*(n//2) + 1
        lo, hi = s_lower(n), S_upper[n]
        verdict = "CLOSED" if hi < need else f"open (needs S({n})>={need}, known <= {hi})"
        print(f"  n={n:2d}, d={d:2d}: need S({n})>={need:3d};  known {lo} <= S({n}) <= {hi}   -> {verdict}")
    print()
    print("sentinel:  d >= ceil(2S(n-1)/(n-2));  needs S(n-1) >= (d-1)(n-2)//2 + 1")
    for n, d in FRONTIERS:
        need = (d-1)*(n-2)//2 + 1
        lo = s_lower(n-1); hi = S_upper.get(n-1)
        verdict = "CLOSED" if (hi is not None and hi < need) else f"open? need {need}, known <= {hi}"
        print(f"  n={n:2d}, d={d:2d}: need S({n-1})>={need:3d};  known {lo} <= S({n-1}) <= {hi}   -> {verdict}")
    print()
    print("Reading: CLOSED means an explicit construction already has fewer comparators than the")
    print("inequality would need, so no improvement of the size bounds can help. At n=11, n=13 and")
    print("n=17 both inequalities are closed: no counting route reaches any of the three frontiers.")

if __name__ == "__main__":
    main()
