#!/usr/bin/env python3
"""Translate proof-used wire bounds and four-rank parity clauses, no solving."""
import collections
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'


def read_clauses(path):
    with path.open() as handle:
        return [tuple(map(int, line.split()[:-1])) for line in handle
                if line.strip() and line[0] not in 'pc']


def main():
    reports = []
    for case in (2, 57, 113):
        source = OUT / f'd13_feedback_round6-r{case:04d}.json'
        if not source.exists():
            continue
        result = json.loads(source.read_text())
        if result['status'] != 'UNSAT' or not result['independently_proof_checked']:
            continue
        directory = Path(result['certificate_directory'])
        groups = json.loads((directory / 'groups.json').read_text())
        full = read_clauses(directory / 'problem.cnf')
        core = read_clauses(directory / 'core.cnf')
        core_set = {tuple(sorted(c)) for c in core}
        units = {c[0] for c in core if len(c) == 1}
        # The reviewed worker allocates13*12 L variables followed by13*12
        # U variables immediately before the first wire-bound selector.
        lo0 = groups[0]['selector'] - 312
        up0 = lo0 + 156
        parity = []
        for c, d in itertools.combinations(range(13), 2):
            for a in range(max(0, c - 3), min(c, 9) + 1):
                for b in range(max(0, d - 3), min(d, 9) + 1):
                    if abs(a - b) not in (1, 3):
                        continue
                    clause = (lo0 + 12*c + a, up0 + 12*c + a+2,
                              lo0 + 12*d + b, up0 + 12*d + b+2)
                    parity.append(dict(wires=[c, d], first_window=[a, a+3],
                                       second_window=[b, b+3], clause=list(clause),
                                       proof_used=tuple(sorted(clause)) in core_set))
        assert len(parity) == result['parity_clauses'] == 222
        begin = groups[0]['clause_start'] - 222
        assert [tuple(r['clause']) for r in parity] == full[begin:begin+222]
        used = [r for r in parity if r['proof_used']]
        report = dict(case_id=result['case_id'], status='TRANSLATED_CHECKED_PROOF_CORE',
                      deletion_minimal=False, parity_clauses_used=len(used),
                      wire_bound_units_used=[g['index'] for g in groups if g['selector'] in units],
                      parity_window_pairs=dict(collections.Counter(
                          f"{r['first_window'][0]},{r['second_window'][0]}" for r in used)),
                      parity_wire_pairs=dict(collections.Counter(
                          f"{r['wires'][0]},{r['wires'][1]}" for r in used)),
                      used_parity=used, original_clauses=len(full), core_clauses=len(core),
                      input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                      note='Proof tracing only. This is neither deletion minimization nor a hand proof of the prefix obstruction.')
        reports.append(report)
        print(json.dumps({k: v for k, v in report.items() if k not in
                          ('used_parity', 'parity_window_pairs', 'parity_wire_pairs')}))
    (OUT / 'd13_feedback_round6-core-analysis.json').write_text(json.dumps(reports, indent=2) + '\n')


if __name__ == '__main__':
    main()
