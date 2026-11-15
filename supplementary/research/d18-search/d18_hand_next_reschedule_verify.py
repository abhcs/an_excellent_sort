#!/usr/bin/env python3
"""Direct functional replay of the bounded four-prefix rescheduling experiment."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import time

HERE = Path(__file__).resolve().parent
NS = runpy.run_path(str(HERE / 'd18_hand_next_reschedule.py'), run_name='audit_import')
OUT = HERE / 'results'


def main():
    records = []
    for name in ('combined', 'beam00', 'beam16', 'beam32'):
        source = OUT / f'd18_hand_next_reschedule-{name}.json'
        data = json.loads(source.read_text())
        result = json.loads(source.with_name(source.stem + '-result.json').read_text())
        binary_runs = 0
        for item in data['items']:
            actual = NS['replay'](data['prefix'], item['initial'])
            assert all(actual[k] == item[k] for k in actual)
            for level in (1, 2):
                endpoints = [v for a, b, h in item['gates'] if h == level for v in (a, b)]
                assert len(set(endpoints)) == len(endpoints)
            binary_runs += NS['check_values'](data['prefix'], item)
            if result['status'] == 'SURVIVOR':
                assert NS['passes'](item, result['layer6'])
                extended = NS['replay'](data['prefix'] + [result['layer6']], item['initial'])
                assert max(extended['depths']) >= 3 or extended['total'] >= {7: 5, 8: 7}[item['r']]
        records.append(dict(case=name, status='VERIFIED', representatives=len(data['items']),
                            binary_functional_replays=binary_runs,
                            survivor_layer=result.get('layer6'), input_sha256=NS['digest'](source)))
    # Independently check the additional thin-family core from the bounded solve.
    thin = OUT / 'd18_hand_next_reschedule-combined-thin-result.json'
    result = json.loads(thin.read_text())
    directory = Path(result['certificate_dir'])
    if not directory.is_absolute():
        directory = HERE.parent / directory
    start = time.monotonic()
    try:
        call = subprocess.run([str(NS['CHECKER']), str(directory / 'problem.cnf'), str(directory / 'proof.drat')],
                              capture_output=True, text=True, timeout=30)
        log = call.stdout + call.stderr
        check = dict(terminal='EXITED', returncode=call.returncode, wall_cap_seconds=30,
                     seconds=time.monotonic()-start, verified=call.returncode == 0 and 's VERIFIED' in log)
        (directory / 'check.log').write_text(log)
    except subprocess.TimeoutExpired:
        check = dict(terminal='TIMEOUT_KILLED', wall_cap_seconds=30,
                     seconds=time.monotonic()-start, verified=False)
    NS['save'](directory / 'check-terminal.json', check)
    if check['verified']:
        result['status'] = 'UNSAT_VERIFIED'
        result['certificate_sha256'] = {p.name: NS['digest'](p) for p in directory.iterdir() if p.is_file()}
        NS['save'](thin, result)
    report = dict(status='VERIFIED', records=records, thin_core_check=check,
                  total_binary_functional_replays=sum(r['binary_functional_replays'] for r in records),
                  source_sha256=NS['digest'](Path(__file__)))
    NS['save'](OUT / 'd18_hand_next_reschedule-verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
