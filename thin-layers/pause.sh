#!/bin/sh
# pause.sh [resume]: suspend (SIGSTOP) or resume (SIGCONT) every thin-layers job: thinsat.py,
# batch.py, the certificate scripts, and the CaDiCaL / drat-trim binaries they start.
# A paused run survives sleep but not a reboot.  batch.py's per-case wall-clock limit keeps counting
# while paused, so a long pause can turn in-flight cases into TIMEOUT records; batch.py re-runs
# TIMEOUT cases when restarted (only UNSAT/FOUND are terminal).
cd "$(dirname "$0")"
act=stop; [ "$1" = resume ] && act=cont
for s in batch.py thinsat.py drat_check.py crosscheck.py prefix_cert_all.py exc_cert.py close_fixed.py cadical drat-trim; do
  python3 tools/procs.py $act $s 2>&1 | grep -v '^0 matched' | grep matched | sed "s/^/$s: /"
done
