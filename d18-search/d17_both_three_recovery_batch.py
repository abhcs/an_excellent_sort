#!/usr/bin/env python3
"""Bounded complete-cover tests of the reconstructed second-count theorem."""
import hashlib
import json
from pathlib import Path
import sys

from d17_second_recovery_exact import bounded

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checker = ROOT.parent / 'build/drat-trim/drat-trim'
    source = ROOT / 'd17_both_three_recovery_profile.py'
    summary = {'scope': 'Two complete D17 cover cases only; no D18 solve.',
               'source_sha256': sha(source), 'checker_sha256': sha(checker),
               'cases': [], 'all_jobs_terminal': False}
    destination = ROOT / 'results/d17-both-three-recovery-batch.json'
    def save():
        destination.write_text(json.dumps(summary, indent=2) + '\n')
    save()
    for case in (482, 603):
        directory = ROOT / f'results/d17-both-three-recovery-case{case}'
        directory.mkdir(exist_ok=False)
        output = directory / 'result.json'
        command = [sys.executable, str(source), '--case', str(case),
                   '--out', str(output), '--proof']
        solve = bounded(command, 60, directory / 'solve.log')
        (directory / 'solve-terminal.json').write_text(json.dumps(solve, indent=2)+'\n')
        record = {'case': case, 'solve_terminal': solve}
        if not solve['timeout'] and solve['returncode'] == 0:
            result = json.loads(output.read_text())
            if result['status'] == 'UNSAT':
                cert = directory / 'result'
                check = bounded([str(checker), str(cert/'problem.cnf'),
                                 str(cert/'proof.drat'), '-t', '60'],
                                60, directory/'check.log')
                (directory/'check-terminal.json').write_text(json.dumps(check, indent=2)+'\n')
                accepted = (not check['timeout'] and check['returncode'] == 0
                            and 's VERIFIED' in (directory/'check.log').read_text())
                record.update(check_terminal=check, checked_unsat=accepted)
                result.update(independently_proof_checked=accepted,
                              checker_sha256=sha(checker),
                              check_log_sha256=sha(directory/'check.log'))
                output.write_text(json.dumps(result, indent=2)+'\n')
            record['result'] = result
        summary['cases'].append(record)
        save()
        print(json.dumps({'case':case, 'solve_seconds':solve['wall_seconds'],
                          'checked_unsat':record.get('checked_unsat',False),
                          'status':record.get('result',{}).get('status','TIMEOUT_OR_ERROR')}),flush=True)
    summary['all_jobs_terminal'] = True
    save()


if __name__ == '__main__':
    main()
