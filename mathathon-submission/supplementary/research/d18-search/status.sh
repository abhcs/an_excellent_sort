#!/bin/sh
# status.sh -- one-screen summary of the d18-search runs (safe to run any time).
cd "$(dirname "$0")" || exit 1
echo "== solver processes (paused = frozen by ./pause.sh; elapsed is wall clock, sleep and pauses included)"
ps -axo stat=,etime=,args= | awk '$3 ~ /[Pp]ython[0-9.]*$/ && $4 ~ /(^|\/)(netsat|crosscheck_e18_4)\.py$/ {
    sub(/.*\//, "", $4); line = ($1 ~ /^T/ ? "paused " : "running") "  " $2
    for (i = 4; i <= NF; i++) line = line " " $i
    print substr(line, 1, 120) }'
echo
echo "== single runs: last line of each log"
for f in logs/e18_*.log logs/m18_*.log logs/crosscheck_*.log; do
    [ -f "$f" ] && printf '%-34s %s\n' "$(basename "$f")" "$(tail -n 1 "$f" | cut -c1-90)"
done
echo
echo "== case splits / batches (results/*.jsonl): status counts"
for f in results/*.jsonl; do
    [ -f "$f" ] || continue
    printf '%-40s %s\n' "$(basename "$f")" \
        "$(grep -o '"status": "[A-Z0-9]*"' "$f" | sort | uniq -c | tr -s ' ' | tr '\n' ' ')"
done
echo
echo "== e18_3 26-case split, both worker pools merged (SKIPPED / ERROR3 = taken by the other pool)"
python3 - <<'EOF'
import json, os
done = {}
for f in ('results/conq_e18_3_cases.jsonl', 'results/conq_e18_3_cases_b.jsonl'):
    if os.path.exists(f):
        for line in open(f):
            r = json.loads(line)
            if r['status'] not in ('SKIPPED', 'ERROR3'):
                done[r['idx']] = (r['status'], r['time'])
running = []
for d in ('results/conq_e18_3_cases_runs', 'results/conq_e18_3_cases_b_runs'):
    if os.path.isdir(d):
        for fn in os.listdir(d):
            if fn.startswith('run_'):
                i = int(fn[4:9])
                txt = open(os.path.join(d, fn)).read()
                if i not in done and 'SKIPPED' not in txt:
                    running.append(i)
counts = {}
for s, _ in done.values():
    counts[s] = counts.get(s, 0) + 1
print(f'finished {len(done)}/26: {counts}; in progress: {sorted(set(running))}; '
      f'not started: {sorted(set(range(26)) - set(done) - set(running))}')
for i in sorted(done):
    print(f'  case {i:2d}: {done[i][0]} in {done[i][1]}s')
EOF
echo
echo "== 18-channel DEPTH-10 networks found (empty unless we succeeded)"
grep -h "FOUND a sorting network: n=18, depth=10" logs/*.log results/*_runs/*.log 2>/dev/null
grep -l '"status": "FOUND"' results/conq_e18*.jsonl results/conq_symbeam_pb*.jsonl results/conq_L4*.jsonl 2>/dev/null
