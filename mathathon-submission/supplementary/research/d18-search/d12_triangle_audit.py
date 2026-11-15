#!/usr/bin/env python3
"""Reproduce the full twelve-wire finite proof and bind its artifacts.

No SAT solver is used: enumerate M, extract four-triple cores, then
independently check their vertex prices, transport and isomorphisms.
"""
import hashlib
import json
from math import factorial
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    source = ROOT / 'd12_triangle_scan.cpp'
    states_file = ROOT / 'results/d17-feedback-twelve-states.json'
    prefix = ROOT / 'results/d12-triangle-scan-four'
    compiler_command = ['c++', '-O3', '-std=c++17', str(source)]
    with tempfile.TemporaryDirectory(prefix='d12-triangle-proof-') as temporary:
        binary = Path(temporary) / 'scan'
        subprocess.run(compiler_command + ['-o', str(binary)], check=True,
                       capture_output=True, text=True, timeout=30)
        binary_sha = digest(binary)
        subprocess.run([str(binary), str(prefix)], check=True,
                       capture_output=True, text=True, timeout=30)
    scan_file = Path(str(prefix) + '-summary.json')
    cores_file = Path(str(prefix) + '-cores.jsonl')
    scan = json.loads(scan_file.read_text())
    assert scan['status'] == 'VERIFIED'
    assert scan['signed_states'] == json.loads(states_file.read_text())['states']
    expected_counts = {
        str(m): factorial(12) // (factorial(12-2*m) * 2**m * factorial(m))
        for m in range(7)
    }
    assert scan['by_size'] == expected_counts
    assert scan['matchings'] == sum(expected_counts.values()) == 140152
    assert scan['deletion_minimal_core_sizes'] == {'4': 140152}
    assert scan['five_cores_with_no_four_subfamily'] == 0
    subprocess.run([sys.executable, str(ROOT / 'd12_triangle_lemmas_verify.py')],
                   check=True, capture_output=True, text=True, timeout=30)
    verification_file = ROOT / 'results/d12_triangle_lemmas_verification.json'
    verification = json.loads(verification_file.read_text())
    assert verification['status'] == 'VERIFIED'
    assert verification['input_core_sha256'] == digest(cores_file)
    assert verification['input_states_sha256'] == digest(states_file)
    assert verification['reported_first_matchings'] == scan['matchings']
    artifacts = [source, states_file, scan_file, cores_file, verification_file,
                 ROOT / 'd12_triangle_lemmas_verify.py',
                 ROOT / 'results/d12_triangle_lemmas_catalogue.jsonl',
                 Path(__file__).resolve()]
    report = dict(
        status='VERIFIED', sat_used=False,
        scope='Full twelve-wire pure two-matching obstruction; finite enumeration of every partial first matching and hand price proofs for all four-triple leaves',
        first_matchings=scan['matchings'],
        first_matching_counts_by_size=expected_counts,
        four_triple_templates=4,
        labelled_cores=verification['labelled_cores'],
        pure_hand_proof_of_universal_template_occurrence=False,
        exact_source_family_checked=True,
        compiler_command=compiler_command,
        binary_sha256=binary_sha,
        sha256={str(p.relative_to(ROOT)): digest(p) for p in artifacts},
        seconds=round(time.monotonic()-started, 4),
    )
    (ROOT / 'results/d12-triangle-proof-audit.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
