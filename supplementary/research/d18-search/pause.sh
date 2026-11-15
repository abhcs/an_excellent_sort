#!/bin/sh
# pause.sh -- freeze or unfreeze every d18-search solver run (safe to run any time).
#   ./pause.sh          freeze: each SAT solver keeps its state in memory and uses no CPU
#   ./pause.sh resume   carry on exactly where they stopped
# A paused run survives sleep but not a restart: the solvers cannot save their state to disk.
# conquer.py's 4-hour limit per case counts the time the Mac is awake, paused or not, so a case
# close to its limit is cut off (TIMEOUT, not UNSAT) soon after resuming.
cd "$(dirname "$0")" || exit 1
case "${1:-pause}" in
    pause)  sig=STOP; order="conquer netsat" ;;   # pools first, so none of them sees a frozen child
    resume) sig=CONT; order="netsat conquer" ;;
    *) echo "usage: $0 [resume]" >&2; exit 2 ;;
esac
for script in $order; do
    # Match the interpreter and script fields, so that a shell whose command line merely mentions
    # netsat.py (a watcher loop, say) is never caught.
    ps -axo pid=,args= | awk -v s="$script" \
        '$2 ~ /[Pp]ython[0-9.]*$/ && ($3 == s ".py" || $3 ~ ("/" s "\\.py$")) {print $1}' |
        xargs kill -"$sig"
done
ps -axo pid=,stat=,etime=,args= | awk '$4 ~ /[Pp]ython[0-9.]*$/ && $5 ~ /(^|\/)(netsat|conquer)\.py$/ {
    sub(/.*\//, "", $5); n++
    printf "%-7s %5d %11s  %-10s %s\n", ($2 ~ /^T/ ? "paused" : "running"), $1, $3, $5, $7 }
    END { if (!n) print "no d18-search runs found" }'
