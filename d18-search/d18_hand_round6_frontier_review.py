#!/usr/bin/env python3
"""Review actual frontier CNFs and certificate manifests without solving."""
import hashlib
import itertools
import json
from pathlib import Path

import netsat
from netsat import prefix_images
from endpoint_cegar import wire_endpoints
from probe_frontier import ProbeModel
from d18_hand_next_reschedule import build as profile_build, PAIRS
from rank_layer_frontier import build as action_build

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Collector:
    def __init__(self, *args, **kwargs):
        self.clauses = []

    def add_clause(self, clause):
        self.clauses.append(clause)


def cnf(path):
    with path.open() as handle:
        header = handle.readline().split()
        clauses = [list(map(int, row.split()[:-1])) for row in handle
                   if row.strip() and row[0] != 'c']
    assert int(header[3]) == len(clauses)
    return clauses


def manifest(result_path, worker):
    result = json.loads(result_path.read_text())
    directory = Path(result['certificate_directory'])
    worker_path=HERE/result.get('worker_source_snapshot',worker)
    assert result['source_sha256'] == sha(worker_path)
    for name, digest in result['dependencies_sha256'].items():
        assert digest == sha(HERE / name)
    assert result['cnf_sha256'] == sha(directory / 'problem.cnf')
    assert result['proof_sha256'] == sha(directory / 'proof.drat')
    checked = json.loads((directory / 'check-terminal.json').read_text())
    assert checked['returncode'] == 0 and checked['verified']
    assert 's VERIFIED' in (directory / 'check.log').read_text()
    return result, cnf(directory / 'problem.cnf')


def main():
    records = []
    netsat.Solver = Collector  # Record construction only: no SAT backend.
    for name in ('beam00', 'beam16', 'beam32'):
        single_path = OUT / f'rank-layer-round6-{name}.json'
        single, actual = manifest(single_path, 'rank_layer_frontier.py')
        rebuilt, _, info = action_build(single['n'], single['prefix'], single['cap'])
        assert rebuilt == actual
        records.append(dict(kind='one-next-layer', case=name, exact_cnf_match=True,
                            clauses=len(actual), source_sha256=single['source_sha256'],
                            existing_drat_check_verified=True))

        prefix_path = OUT / f'prefix-rank-round6-cut8-{name}.json'
        result, actual = manifest(prefix_path, 'prefix_rank_frontier.py')
        data_path = OUT / f'd18_hand_round5_combined-{name}.json'
        data = json.loads(data_path.read_text())
        n, prefix, cap = result['n'], result['prefix'], result['cap']
        assert data['prefix'] == prefix and result['depth'] == len(prefix) + 5
        model = ProbeModel(n, result['depth'] - len(prefix), sorted(prefix_images(n, prefix)),
                           phi=False, nored0=False)
        lower, upper = wire_endpoints(model, list(range(n)), cap)
        count = 0
        for c, d in itertools.combinations(range(n), 2):
            for a in range(max(0, c-cap+1), min(c, n-cap)+1):
                for b in range(max(0, d-cap+1), min(d, n-cap)+1):
                    if abs(a-b) < cap and abs(a-b) % 2:
                        model.add([lower[c][a+1], upper[c][a+cap-1],
                                   lower[d][b+1], upper[d][b+cap-1]])
                        count += 1
        assert count == result['parity_clauses']
        start = model.ncl
        clauses, variables, _ = profile_build(data['rescheduling_items'], assumptions=False)
        mapping = {i+1: model.g[0][edge] for i, edge in enumerate(PAIRS)}
        assert len(set(mapping.values())) == 153
        old_top = model.nv
        for v in range(154, variables+1):
            mapping[v] = model.new_var()
        assert all(v > old_top for k, v in mapping.items() if k > 153)
        clauses += [row['clause'] for row in data['component_cuts']]
        for clause in clauses:
            model.add([mapping[abs(v)] if v > 0 else -mapping[abs(v)] for v in clause])
        assert len(clauses) == result['combined_clauses']
        assert model.S.clauses == actual[:model.ncl]
        records.append(dict(kind='three-free-cut-layers', case=name,
                            checked_cnf_prefix_clauses=model.ncl,
                            combined_clause_start=start, combined_clauses=len(clauses),
                            combined_translation_matches_actual_cnf=True,
                            combined_input_sha256=sha(data_path),
                            combined_encoder_sha256=sha(HERE / 'd18_hand_next_reschedule.py'),
                            source_sha256=result['source_sha256'],
                            existing_drat_check_verified=True))
    report = dict(status='REVIEWED_SOUND_FOR_TESTED_CALLS', uses_sat=False,
                  proof_check_rerun=False, records=records,
                  preconditions=['Saturated-cone parity requires at least one layer after the cut.',
                                 'Imported combined conditions require depth=len(prefix)+5.'],
                  provenance_note='Original worker sources are preserved as recorded_*.py alongside their dependencies; this review supplies combined hashes omitted by those manifests. Current workers enforce both preconditions and record the combined hashes.',
                  source_sha256=sha(Path(__file__)))
    (OUT / 'd18_hand_round6-frontier-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
