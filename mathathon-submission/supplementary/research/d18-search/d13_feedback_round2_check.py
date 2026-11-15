#!/usr/bin/env python3
"""Bounded independent DRAT check for a round-two structural certificate."""
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
    assert result['status'] == 'UNSAT'
    p = Path(result['certificate_directory'])
    checker = Path('/private/tmp/d18-structural-drat-trim/drat-trim')
    cmd = [str(checker), str(p / 'problem.cnf'), str(p / 'proof.drat'),
           '-c', str(p / 'core.cnf'), '-l', str(p / 'core-proof.drat'), '-t', '60']
    start = time.monotonic()
    try:
        call = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        log = call.stdout + call.stderr
        (p / 'check.log').write_text(log)
        report = dict(terminal='EXITED', returncode=call.returncode, wall_cap_seconds=60,
                      seconds=time.monotonic() - start, verified=call.returncode == 0 and 's VERIFIED' in log)
    except subprocess.TimeoutExpired:
        report = dict(terminal='TIMEOUT_KILLED', wall_cap_seconds=60,
                      seconds=time.monotonic() - start, verified=False)
    (p / 'check-terminal.json').write_text(json.dumps(report, indent=2) + '\n')
    if report['verified']:
        result.update(independently_proof_checked=True, check_seconds=report['seconds'],
                      checker_sha256=hashlib.sha256(checker.read_bytes()).hexdigest())
        args.result.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
