#!/usr/bin/env python3
"""Check the four small merger certificates and the resulting D18 witnesses.

No SAT solve is run. Uses bounded drat-trim checks and independent trace
replays, plus a reproducible rerun of the normalized component collector.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from d13_feedback_round3_components import audit_component_chains
from merge_component_verify import call, value_check

HERE = Path(__file__).resolve().parent
CHECKER = Path('/private/tmp/d18-structural-drat-trim/drat-trim')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    certificates = []
    for shape in ('711', '621', '531', '522'):
        manifest = HERE / f'results/merger-partition-round4-{shape}.json'
        data = json.loads(manifest.read_text())
        assert data['blocks'] == list(map(int, shape)) and data['depth'] == 4
        assert data['status'] == 'UNSAT_UNCHECKED' and not data['normal_forms']
        assert data['source_sha256'] == digest(HERE/'d13_feedback_round3_merger_bare.py')
        directory = manifest.with_suffix('')
        cnf, proof = directory/'problem.cnf', directory/'proof.drat'
        assert digest(cnf) == data['cnf_sha256'] and digest(proof) == data['proof_sha256']
        run = subprocess.run([str(CHECKER), str(cnf), str(proof)],
                             capture_output=True, text=True, timeout=20)
        assert run.returncode == 0 and 's VERIFIED' in run.stdout
        (directory/'check.log').write_text(run.stdout + run.stderr)
        certificates.append(dict(blocks=data['blocks'], binary_inputs=data['inputs'],
            cnf_sha256=digest(cnf), proof_sha256=digest(proof),
            checker_returncode=run.returncode, checker_verified=True))
    source = HERE/'results/merge-component18-round4-three.json'
    rows = json.loads(source.read_text())
    witness_replays = []
    d13_replays = []
    cover = [json.loads(line) for line in (HERE/'prefixes/complete13.jsonl').read_text().splitlines()]
    d13 = json.loads((HERE/'results/merge-component13-round4-three.json').read_text())
    for i, row in enumerate(d13['rows']):
        assert row['case_id'] == cover[i]['case_id']
        if not row['example']:
            continue
        saved = HERE/f'results/profile-frontier13/n13-r{i:04d}.json'
        layers = cover[i]['layers']+json.loads(saved.read_text())['next_layers']
        w = row['example'][0]
        assert len(w['components']) >= 3
        replayed = value_check(13, layers, w)
        d13_replays.append(dict(case_id=row['case_id'], binary_functional_replays=replayed,
                               saved_witness_sha256=digest(saved)))
    assert len(d13_replays) == d13['witnesses_rejected'] == 83
    with tempfile.TemporaryDirectory(prefix='merger-round4-') as temporary:
        temp = Path(temporary)
        binary, prefix = temp/'collector', temp/'prefix.txt'
        subprocess.run(['c++', '-O3', '-std=c++17', str(HERE/'merge_component_states.cpp'),
                        '-o', str(binary)], check=True, capture_output=True, timeout=20)
        for row in rows:
            repeated = call(binary, prefix, 18, row['layers'], 'three', False)
            for key in ('accepted_placements', 'normalized_placements', 'witnesses'):
                assert repeated[key] == row[key]
            if row['cut'] != 6 or not row['witnesses']:
                continue
            w = row['witnesses'][0]
            assert len(w['components']) >= 3
            functional = value_check(18, row['layers'], w)
            groups = [[v for v in range(18) if mask >> v & 1]
                      for mask in w['cut_component_masks']]
            chains = audit_component_chains(row['layers'],
                         dict(initial=w['initial'], components=groups))
            witness_replays.append(dict(name=row['name'], initial=w['initial'],
                cut_components=groups, component_sizes=sorted(map(len, groups), reverse=True),
                binary_functional_replays=functional, component_chain_replays=chains))
        # These are positive controls for the one-layer relaxation, not sorters.
        survivors = json.loads((HERE/'results/merge-component18-round4-next-layer.json').read_text())
        for survivor in survivors:
            row = next(r for r in rows if r['name'] == survivor['name'])
            assert survivor['status'] == 'SURVIVOR'
            checked = call(binary, prefix, 18, row['layers']+[survivor['next_layer']], 'three', False)
            assert checked['accepted_placements'] == 0
    report = dict(status='VERIFIED', certificates=certificates,
        checker_sha256=digest(CHECKER), collector_sha256=digest(HERE/'merge_component_states.cpp'),
        encoder_sha256=digest(HERE/'d13_feedback_round3_merger_bare.py'),
        encoding_helper_sha256=digest(HERE.parent/'depth-hand-proofs/verify/sentinel_cegar.py'),
        source_sha256=digest(Path(__file__)), sample_source_sha256=digest(source),
        prefix_runs_reproduced=len(rows), six_layer_witness_replays=witness_replays,
        one_layer_survivors_replayed=len(survivors), seconds=time.monotonic()-start,
        d13_rejected_witness_replays=d13_replays,
        scope='Four small merger certificates and concrete prefix exclusions; no complete D18 cover case')
    (HERE/'results/merger-partition-round4-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
