#!/usr/bin/env bash
# descent_run.sh STORE WORKERS -- the computer part of D(17) >= 10 by the descent with exceptions
# (README §8.15): prove SS(11,9,2,3); then SS(12,9,3,3), whose good-track children follow from it,
# then SS(13,9,4,3) and SS(14,9,5,3) = S14 the same way; then check everything from definitions.
#
# Environment: PY (python with python-sat; default python3), CADICAL, DRATTRIM (see satcert.py),
# SATCERT_TMP (scratch directory for CNF and proof files), DESCENT_OPTS (extra options for
# descent_cases.py, e.g. "--child-seconds -1 --sat-seconds 3600").
# Resumable: proved facts stay in STORE; rerun the same command.  A level whose cases are not all
# proved stops the script; clear STORE/claims/<level> and rerun (maybe with more --sat-seconds).
set -u
STORE=${1:?usage: descent_run.sh STORE WORKERS}
W=${2:?usage: descent_run.sh STORE WORKERS}
PY=${PY:-python3}
HERE=$(cd "$(dirname "$0")" && pwd)

"$PY" -c 'import pysat' || { echo "need python-sat for $PY"; exit 2; }
"$PY" -c "import sys; sys.path.insert(0, '$HERE'); import satcert; assert satcert.CADICAL and satcert.DRATTRIM, 'set CADICAL and DRATTRIM'; print('cadical', satcert.CADICAL); print('drat-trim', satcert.DRATTRIM)" || exit 2
[ -d "$STORE" ] || "$PY" "$HERE/descent_init.py" init "$HERE/results/descent_base" "$STORE" || exit 2

for ST in SS:11,9,2,3 SS:12,9,3,3 SS:13,9,4,3 SS:14,9,5,3; do
  tag=${ST//[:,]/_}
  if grep -q "\"$ST\"" "$STORE/statements.jsonl"; then
    echo "$ST: already proved"
    continue
  fi
  echo "$(date '+%F %T') $ST: $W workers, logs $STORE/log_${tag}_w*.log"
  pids=()
  for ((w = 0; w < W; w++)); do
    "$PY" "$HERE/descent_cases.py" "$ST" "$STORE" "$W" "$w" ${DESCENT_OPTS:-} > "$STORE/log_${tag}_w$w.log" 2>&1 &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p"; done
  if [ -s "$STORE/COUNTEREXAMPLES.jsonl" ]; then
    echo "!!! $ST has a completion: see $STORE/COUNTEREXAMPLES.jsonl"
    exit 3
  fi
  "$PY" "$HERE/descent_cases.py" "$ST" "$STORE" --assemble || {
    echo "$ST: some cases are still open (see the logs). Clear $STORE/claims/$tag and rerun."
    exit 1
  }
done
echo "$(date '+%F %T') checking SS:14,9,5,3 from definitions"
"$PY" "$HERE/check_facts.py" "$STORE" SS:14,9,5,3 --jobs "$W"
