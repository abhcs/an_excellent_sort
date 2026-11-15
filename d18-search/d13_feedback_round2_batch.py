#!/usr/bin/env python3
"""Three representative unclosed D13 cases; 30-second solver subprocess caps."""
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')


def main():
    audit = []
    for case in (1, 58, 114):
        output = OUT / f'd13_feedback_round2-r{case:04d}-wire.json'
        start = time.monotonic()
        cmd = [sys.executable, str(HERE / 'd13_feedback_round2.py'), '--case', str(case),
               '--mode', 'wire', '--proof', '--out', str(output)]
        try:
            call = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            terminal = dict(case_id=f'n13-r{case:04d}', terminal='EXITED', returncode=call.returncode,
                            wall_cap_seconds=30, seconds=time.monotonic() - start,
                            stdout=call.stdout, stderr=call.stderr)
        except subprocess.TimeoutExpired as e:
            terminal = dict(case_id=f'n13-r{case:04d}', terminal='TIMEOUT_KILLED', wall_cap_seconds=30,
                            seconds=time.monotonic() - start, stdout=str(e.stdout), stderr=str(e.stderr))
        save(output.with_name(output.stem + '-terminal.json'), terminal)
        if terminal['terminal'] == 'EXITED' and terminal['returncode'] == 0:
            result = json.loads(output.read_text())
            terminal['result_status'] = result['status']
            if result['status'] == 'UNSAT':
                # Checker enforces its own60-second hard subprocess cap.
                check = subprocess.run([sys.executable, str(HERE / 'd13_feedback_round2_check.py'), str(output)],
                                       capture_output=True, text=True, timeout=65)
                terminal['check_process_returncode'] = check.returncode
                terminal['check_stdout'] = check.stdout
                terminal['independently_proof_checked'] = json.loads(output.read_text())['independently_proof_checked']
        audit.append(terminal)
        save(OUT / 'd13_feedback_round2-batch-audit.json', audit)
        print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    main()
