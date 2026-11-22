#!/bin/sh
# finalize_s11.sh: certificates for S11 after the batch.  (1) re-solve the cases recorded before CNF
# dumping existed, writing their CNFs; (2) DRAT-check every case CNF; (3) re-decide three sample cases
# with the independent encoder depth-hand-proofs/verify/satnet.py.
cd "$(dirname "$0")"
PY=${PY:-python3}
D=/private/tmp/claude-501/-Users-abhishek--claude-spares-spare-8LJXq4/c54486b5-433d-4286-8fa9-f685212181d8/scratchpad/cnf11
for c in 83 84 85; do
  [ -f $D/case$c.cnf ] && continue
  L2=$($PY -c "import json; print(json.dumps(json.load(open('results/l2classes_11_4.json'))['reps'][$c]))")
  $PY thinsat.py 11 8 4 --capped 3 --l2 "$L2" --dump $D/case$c.cnf > logs/S11_redump_case$c.log 2>&1 &
done
wait
( nice -n 10 $PY drat_check.py $D results/S11_drat.jsonl --workers ${DRAT_WORKERS:-6} > logs/S11_drat.log 2>&1 ) &
for c in 0 60 150; do
  L2=$($PY -c "import json; print(json.dumps(json.load(open('results/l2classes_11_4.json'))['reps'][$c]))")
  ( nice -n 10 $PY crosscheck.py 11 8 4 3 "$L2" >> results/S11_crosscheck.jsonl 2> logs/S11_crosscheck_case$c.err ) &
done
wait
