#!/usr/bin/env python3
"""Six-run hand certificates for the 43 former H9 ending-search leaves.

Generation enumerates each prefix's binary image. Verification only checks
the six supplied runs, adds the sorted anchors, and applies the proved
heavy-neighbor lemma. The verifier does not enumerate suffixes or call SAT.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'd18-search'))
from two_real_graph import images_with_witness, run_bits, sorted_bits
from two_layer_profiles import profile


def verify(record):
    n, prefix = record['n'], record['prefix']
    assert n == 9 and len(prefix) == 5
    for layer in prefix:
        used = set()
        for a, b in layer:
            assert 0 <= a < b < n and a not in used and b not in used
            used.update((a, b))
    start, heavy = record['start'], record['heavy']
    assert 1 <= start <= n - 4 and start <= heavy < start + 3
    outputs = {sorted_bits(n, n - z) for z in range(start, start + 4)}
    for row in record['runs']:
        assert 0 <= row['input'] < 1 << n
        assert run_bits(prefix, row['input']) == row['output']
        outputs.add(row['output'])
    counts = profile(n, outputs)
    assert all(counts[z] >= 2 for z in range(start, start + 4))
    assert counts[heavy] >= 3 and counts[heavy + 1] >= 3
    return True


def generate(path):
    records = []
    for line in path.read_text().splitlines():
        if 'best L6 leaves' not in line and 'H5 cuts' not in line:
            continue
        parts = line.split('   (')[0].split('|')
        prefix = [[(0, 1), (2, 3), (4, 5)]] + [
            [tuple(map(int, pair)) for pair in re.findall(r'\((\d+),(\d+)\)', part)] for part in parts]
        assert len(prefix) == 5
        sources = images_with_witness(9, prefix)
        counts = profile(9, sources)
        start, heavy = next((a, b) for a in range(1, 6) for b in range(a, a + 3)
                            if all(counts[z] >= 2 for z in range(a, a + 4)) and
                            counts[b] >= 3 and counts[b + 1] >= 3)
        runs = []
        for z in range(start, start + 4):
            needed = 2 if z in (heavy, heavy + 1) else 1
            choices = sorted(x for x in sources if 9 - x.bit_count() == z and x != sorted_bits(9, 9 - z))
            runs.extend(dict(input=sources[x], output=x) for x in choices[:needed])
        record = dict(case_id=f'h9-ending-{len(records):02d}', n=9, prefix=prefix,
                      full_profile=counts, start=start, heavy=heavy, runs=runs)
        assert len(runs) == 6 and verify(record)
        records.append(record)
    assert len(records) == 43
    assert len({json.dumps(r['prefix']) for r in records}) == 43
    corrupted = copy.deepcopy(records[0])
    corrupted['runs'][0]['output'] ^= 1
    try:
        verify(corrupted)
    except AssertionError:
        pass
    else:
        raise AssertionError('Corrupted run accepted')
    duplicate = copy.deepcopy(records[0])
    duplicate['runs'] = [duplicate['runs'][0]] * 6
    try:
        verify(duplicate)
    except AssertionError:
        pass
    else:
        raise AssertionError('Repeated single witness accepted')
    return dict(certificates=records, profiles=dict(Counter(str(r['full_profile']) for r in records)),
                source_log_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                corrupt_run_rejected=True, duplicate_witness_rejected=True,
                verification_scope='Six runs and four fixed sorted anchors per prefix; no suffix search')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.generate:
        data = generate(args.generate)
        args.out.write_text(json.dumps(data, indent=2) + '\n')
    else:
        data = json.loads(args.verify.read_text())
    for record in data['certificates']:
        verify(record)
    print(json.dumps(dict(certificates_verified=len(data['certificates']),
                          actual_prefix_runs=sum(len(r['runs']) for r in data['certificates']),
                          profiles=data['profiles'])))


if __name__ == '__main__':
    main()
