#!/bin/sh
# Re-run every cheap check behind the results, in about a minute.
# Heavier runs are listed in README.md and are not run here.
set -e
cd "$(dirname "$0")"
CC=${CC:-gcc}

echo "== compile =="
for f in twolayer exact3 exact4 chain chain2 chain3 rho5 k6verify phibound dedup; do $CC -O2 -o "$f" "$f.c"; done
$CC -O2 -o rho6 rho6.c -lm
echo "   ok"

echo
echo "== handoff section 3: are the inequalities closed at the frontier? =="
./closed.py

echo
echo "== Lemma F: matchings x interval partitions (n=3,5,7,9) =="
python3 frontend_lemma_any.py

echo
echo "== Lemma H: connectivity of the suffix (exhaustive, n=3 and n=5) =="
python3 conn_test.py 2>/dev/null | tail -4

echo
echo "== exact two-layer minima (n=5,7,9; expect 12,30,72) =="
for n in 5 7 9; do ./twolayer $n 2>/dev/null | head -1; done

echo
echo "== exact t-layer minima: found=0 means the bound holds =="
./exact3 5 | tail -1
./exact3 7 | tail -1
./exact4 7 12 | tail -1
./k6verify 8 36 2>/dev/null | tail -1
./k6verify 10 108 2>/dev/null | tail -1

echo
echo "== local ratios: cycles and paths =="
python3 cycletype.py | head -8

echo
echo "== local ratio rho_5 (exact, 123/243) and sampled rho_6 =="
./rho5 10 2>/dev/null | head -1
./rho6 10 20000 2>/dev/null | head -1

echo
echo "== Theorem F' (cluster factorization) on 400 random 3-layer chains =="
python3 cluster.py

echo
echo "== brick descent at n=9 (expect 162,72,40,26,20,14) =="
./chain2 9 6 2>/dev/null | tail -5

echo
echo "all checks completed"
