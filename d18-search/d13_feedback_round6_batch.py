#!/usr/bin/env python3
"""Three nearby unclosed D13 cases, each with30s solve and30s DRAT caps."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
CHECKER = Path('/private/tmp/d18-structural-drat-trim/drat-trim')


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded(command, cap):
    started = time.monotonic()
    try:
        call = subprocess.run(command, capture_output=True, text=True, timeout=cap)
        return dict(terminal='EXITED', returncode=call.returncode, stdout=call.stdout,
                    stderr=call.stderr, wall_cap_seconds=cap, seconds=time.monotonic() - started)
    except subprocess.TimeoutExpired as error:
        def text(x):
            return x.decode() if isinstance(x, bytes) else (x or '')
        return dict(terminal='TIMEOUT_KILLED', stdout=text(error.stdout), stderr=text(error.stderr),
                    wall_cap_seconds=cap, seconds=time.monotonic() - started)


def main():
    audit = []
    source = HERE / 'd13_rank_parity_probe.py'
    source_sha = sha(source)
    for case in (2, 57, 113):
        assert sha(source) == source_sha, 'Do not change the reviewed worker during this batch'
        output = OUT / f'd13_feedback_round6-r{case:04d}.json'
        terminal = bounded([sys.executable, str(source), '--case', str(case), '--mode', 'wire',
                            '--proof', '--out', str(output)], 30)
        terminal['case_id'] = f'n13-r{case:04d}'
        save(output.with_name(output.stem + '-terminal.json'), terminal)
        if terminal['terminal'] == 'EXITED' and terminal['returncode'] == 0:
            result = json.loads(output.read_text())
            terminal['result_status'] = result['status']
            if result['status'] == 'UNSAT':
                directory = Path(result['certificate_directory'])
                check = bounded([str(CHECKER), str(directory / 'problem.cnf'),
                                 str(directory / 'proof.drat'), '-c', str(directory / 'core.cnf'),
                                 '-l', str(directory / 'core-proof.drat'), '-t', '30'], 30)
                log = check['stdout'] + check['stderr']
                check['verified'] = check.get('returncode') == 0 and 's VERIFIED' in log
                (directory / 'check.log').write_text(log)
                save(directory / 'check-terminal.json', check)
                terminal['check'] = {k: v for k, v in check.items() if k not in ('stdout', 'stderr')}
                if check['verified']:
                    result.update(independently_proof_checked=True, check_seconds=check['seconds'],
                                  checker_sha256=sha(CHECKER))
                    save(output, result)
        save(output.with_name(output.stem + '-terminal.json'), terminal)
        audit.append(terminal)
        save(OUT / 'd13_feedback_round6-audit.json', audit)
        print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    main()
