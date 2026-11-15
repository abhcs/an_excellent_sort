#!/usr/bin/env python3
"""Audit parity-clause semantics, controls, saved certificates and CNF differences.

Does not rerun SAT or DRAT checking; successful independent checker logs
are required and their hashes are recorded.
"""
import collections
import hashlib
import itertools
import json
from pathlib import Path

from interval_frontier import actual_intervals
from netsat import verify_all

HERE = Path(__file__).resolve().parent
OUT = HERE/'results'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    n = 13
    endpoint_checks = 0
    for c,d in itertools.combinations(range(n),2):
        for lo1 in range(c+1):
            for hi1 in range(c,min(n,lo1+4)):
                for lo2 in range(d+1):
                    for hi2 in range(d,min(n,lo2+4)):
                        overlap = max(0,min(hi1,hi2)-max(lo1,lo2)+1)
                        expected = not (hi1-lo1 == hi2-lo2 == 3 and overlap % 2)
                        clauses = []
                        for a in range(max(0,c-3),min(c,n-4)+1):
                            for b in range(max(0,d-3),min(d,n-4)+1):
                                if abs(a-b) in (1,3):
                                    clauses.append(lo1 >= a+1 or hi1 < a+3 or
                                                   lo2 >= b+1 or hi2 < b+3)
                        assert all(clauses) == expected
                        endpoint_checks += 1
    net = json.loads((OUT/'complete13-d9-control/n13-r0116/result.json').read_text())['network']
    assert verify_all(n,net)
    intervals,_,_ = actual_intervals(n,net[:2],net[2:7])
    assert max(hi-lo+1 for lo,hi in intervals) <= 4
    full = [(lo,hi) for lo,hi in intervals if hi-lo==3]
    assert all(max(0,min(b,d)-max(a,c)+1)%2 == 0
               for (a,b),(c,d) in itertools.combinations(full,2))
    records = []
    for case in (1,114):
        path = OUT/f'd13-rank-parity-r{case:04d}.json'
        result = json.loads(path.read_text())
        basepath = OUT/f'd13-rank-parity-baseline-r{case:04d}.json'
        baseline = json.loads(basepath.read_text())
        directory = path.with_suffix('')
        assert result['status'] == 'UNSAT'
        assert result['source_sha256'] == sha(HERE/'d13_rank_parity_probe.py')
        for name,digest in result['dependencies_sha256'].items():
            assert sha(HERE/name) == digest
        for filename,key in (('problem.cnf','cnf_sha256'),('proof.drat','proof_sha256')):
            assert sha(directory/filename) == result[key]
        check = json.loads((directory/'check-terminal.json').read_text())
        assert check['terminal'] == 'EXITED' and check['returncode'] == 0 and check['verified']
        assert 's VERIFIED' in (directory/'check.log').read_text()
        assert result['prefix'] == baseline['prefix'] and result['variables'] == baseline['variables']
        old = collections.Counter((basepath.with_suffix('')/'problem.cnf').read_text().splitlines()[1:])
        new = collections.Counter((directory/'problem.cnf').read_text().splitlines()[1:])
        assert not old-new and sum((new-old).values()) == 222
        records.append(dict(case_id=result['case_id'],cnf_sha256=result['cnf_sha256'],
            proof_sha256=result['proof_sha256'],checker_log_sha256=sha(directory/'check.log'),
            exact_added_clause_count=222))
    report = dict(status='VERIFIED',endpoint_assignments=endpoint_checks,
        known_sorter_binary_inputs=8192,known_sorter_cut7_intervals=intervals,
        certificates=records,source_sha256=sha(Path(__file__)),
        scope='Clause semantics, known-sorter control, saved proof-file and checker-log audit; not a new proof-checker run')
    (OUT/'d13-rank-parity-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('certificates','known_sorter_cut7_intervals')}))


if __name__ == '__main__':
    main()
