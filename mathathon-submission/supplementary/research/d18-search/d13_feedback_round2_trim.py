#!/usr/bin/env python3
"""Remove unused semantic wire-bound units and independently recheck DRAT."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('result', type=Path)
    args = ap.parse_args()
    result = json.loads(args.result.read_text())
    p = Path(result['certificate_directory'])
    groups = json.loads((p / 'groups.json').read_text())
    def clauses(path):
        return [list(map(int, s.split()[:-1])) for s in path.read_text().splitlines()
                if s and s[0] not in 'pc']
    core = clauses(p / 'core.cnf')
    unit = {c[0] for c in core if len(c) == 1}
    selected = [g for g in groups if g['selector'] in unit]
    omitted = {g['selector'] for g in groups if g['selector'] not in unit}
    original = clauses(p / 'problem.cnf')
    reduced = [c for c in original if not (len(c) == 1 and c[0] in omitted)]
    target = p / 'wire-core.cnf'
    target.write_text(f'p cnf {result["variables"]} {len(reduced)}\n' +
                      ''.join(' '.join(map(str, c)) + ' 0\n' for c in reduced))
    report = dict(case_id=result['case_id'], retained_bounds=selected,
                  omitted_bound_units=sorted(omitted), original_clauses=len(original),
                  reduced_clauses=len(reduced), deletion_minimal=False,
                  note='Only unused bound units removed; omitted selectors are unconstrained and can be false',
                  wall_cap_seconds=60)
    started = time.monotonic()
    cmd = ['/private/tmp/d18-structural-drat-trim/drat-trim', str(target), str(p / 'core-proof.drat'), '-t', '60']
    try:
        call = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        log = call.stdout + call.stderr
        (p / 'wire-core-check.log').write_text(log)
        report.update(terminal='EXITED', returncode=call.returncode,
                      verified=call.returncode == 0 and 's VERIFIED' in log)
    except subprocess.TimeoutExpired:
        report.update(terminal='TIMEOUT_KILLED', verified=False)
    report['seconds'] = time.monotonic() - started
    report['sha256'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in (target, p / 'core-proof.drat', Path(__file__))}
    (p / 'wire-core.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
