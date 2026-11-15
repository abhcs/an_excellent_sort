#!/usr/bin/env python3
"""Exact thin-first-two-layer search, split by maximal adjacent last layers.

For a fixed last layer N, it suffices to sort input weights whose rank cut
is not an edge of N. The proof uses monotonicity, and is checked below on
small arbitrary prefixes. A timeout never closes a case. Each SAT answer
is independently checked on every binary input.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'd18-search'))
from pysat.card import CardEnc, EncType
from netsat import apply_layers, is_sorted, prefix_images, verify_all
from shared_ending_sat import SharedEndingModel
from two_layer_topology import adjacent_matchings
from two_real_graph import matchings


def reflected(n, layer):
    return tuple(sorted((n - 1 - b, n - 1 - a) for a, b in layer))


def last_layers(n):
    result = []
    for layer in adjacent_matchings(n):
        used = {v for edge in layer for v in edge}
        if any(i not in used and i + 1 not in used for i in range(n - 1)):
            continue
        layer = tuple(layer)
        if layer <= reflected(n, layer):
            result.append(layer)
    return sorted(result)


def selected_zeros(n, last):
    edges = {tuple(p) for p in last}
    return [z for z in range(1, n) if (z - 1, z) not in edges]


def first_layer(n, cap):
    # Centre the adjacent pairs so reflection fixes this first layer.
    assert n % 2 == 0 and 0 <= cap <= n // 2
    offset = (n - 2 * cap) // 2
    return [(offset + 2 * i, offset + 2 * i + 1) for i in range(cap)]


def source_hashes():
    paths = [Path(__file__), *(ROOT / 'd18-search' / name for name in
             ('netsat.py', 'capacity_sat.py', 'shared_ending_sat.py',
              'two_layer_profiles.py', 'two_layer_envelope.py', 'two_layer_topology.py'))]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def atomic_json(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(path)


def solve_case(n, depth, cap, last, solver='cadical195', progress=None):
    started = time.monotonic()
    first = first_layer(n, cap)
    outputs = prefix_images(n, [first])
    selected = set(selected_zeros(n, last))
    # Nonredundancy is computed from the FULL prefix image, not the test subset.
    model = SharedEndingModel(n, depth - 1, outputs, solver=solver)
    try:
        card = CardEnc.atmost(list(model.g[0].values()), bound=cap,
                             top_id=model.nv, encoding=EncType.seqcounter)
        model.nv = max(model.nv, card.nv)
        for clause in card.clauses:
            model.add(clause)
        chosen = set(tuple(p) for p in last)
        for edge, gate in model.g[-1].items():
            model.add([gate if edge in chosen else -gate])
        inputs = [x for x in sorted(outputs) if not is_sorted(x, n) and n - x.bit_count() in selected]
        for x in inputs:
            model.add_input(x)
        result = dict(n=n, depth=depth, first_two_caps=cap, first=first, last=last,
                      selected_zeros=sorted(selected), encoded_inputs=len(inputs),
                      full_prefix_outputs=len(outputs), variables=model.nv, clauses=model.ncl,
                      solver=solver, status='BUILT', build_seconds=time.monotonic() - started,
                      source_hashes=source_hashes(), proof_trace_checked=False)
        if progress:
            atomic_json(progress, result)
        ok = model.S.solve()
        result.update(status='SAT' if ok else 'UNSAT', seconds=time.monotonic() - started)
        if ok:
            net = [first] + model.network(model.S.get_model())
            assert all(len(layer) <= cap for layer in net[:2])
            assert net[-1] == sorted(chosen)
            assert verify_all(n, net), 'Reduced-weight model failed full verification'
            result.update(network=net, verified_binary_inputs=1 << n)
        return result
    finally:
        model.S.delete()


def check():
    checked = 0
    for n in (3, 4):
        for depth in range(4):
            for prefix in itertools.product(matchings(n), repeat=depth):
                outputs = prefix_images(n, prefix)
                for last in adjacent_matchings(n):
                    levels = set(selected_zeros(n, last))
                    reduced = all(is_sorted(apply_layers([last], x), n) for x in outputs
                                  if n - x.bit_count() in levels)
                    full = all(is_sorted(apply_layers([last], x), n) for x in outputs)
                    assert reduced == full, (n, prefix, last)
                    checked += 1
    negatives, positives = [], []
    for n, depth, cap in ((6, 5, 2), (8, 6, 3)):
        for i, last in enumerate(last_layers(n)):
            result = solve_case(n, depth, cap, last)
            assert result['status'] == 'UNSAT', result
            negatives.append(dict(n=n, depth=depth, case=i, status='UNSAT', seconds=result['seconds']))
    for i, last in enumerate(last_layers(6)):
        result = solve_case(6, 6, 2, last)
        if result['status'] == 'SAT':
            positives.append(dict(n=6, depth=6, case=i, verified_binary_inputs=64,
                                  network=result['network']))
    assert positives
    return dict(weight_omission_equivalences=checked, small_negative_cases=negatives,
                small_positive_cases=positives, source_hashes=source_hashes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--n', type=int)
    parser.add_argument('--depth', type=int)
    parser.add_argument('--cap', type=int)
    parser.add_argument('--case', type=int)
    parser.add_argument('--seconds', type=float, default=15)
    parser.add_argument('--solver', default='kissat404')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if args.check:
        result = check()
        atomic_json(args.out, result)
        print(json.dumps(result), flush=True)
        return
    cases = last_layers(args.n)
    if args.worker:
        result = solve_case(args.n, args.depth, args.cap, cases[args.case], args.solver,
                            args.out.with_suffix('.progress.json'))
        atomic_json(args.out, result)
        return
    assert args.n % 2 == 0 and args.depth >= 3
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = dict(n=args.n, depth=args.depth, first_two_caps=args.cap,
                    first=first_layer(args.n, args.cap), last_layers=cases,
                    source_hashes=source_hashes())
    manifest['case_list_sha256'] = hashlib.sha256(json.dumps(cases, separators=(',', ':')).encode()).hexdigest()
    manifest_path = args.out / 'manifest.json'
    if manifest_path.exists():
        assert json.loads(manifest_path.read_text()) == json.loads(json.dumps(manifest)), 'Manifest changed; use a new directory.'
    else:
        atomic_json(manifest_path, manifest)
    indices = range(len(cases)) if args.case is None else [args.case]
    for index in indices:
        destination = args.out / f'case-{index:03d}.json'
        assert not destination.exists(), 'Use a fresh output directory or select an unattempted case.'
        started = time.monotonic()
        cmd = [sys.executable, str(Path(__file__).resolve()), '--worker', '--n', str(args.n),
               '--depth', str(args.depth), '--cap', str(args.cap), '--case', str(index),
               '--solver', args.solver, '--out', str(destination)]
        terminal = None
        with destination.with_suffix('.log').open('w') as log:
            try:
                child = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=args.seconds)
                if child.returncode:
                    terminal = 'ERROR'
            except subprocess.TimeoutExpired:
                terminal = 'TIME_LIMIT'
        if terminal:
            progress = destination.with_suffix('.progress.json')
            result = json.loads(progress.read_text()) if progress.exists() else dict(n=args.n, depth=args.depth)
            result.update(status=terminal, seconds=time.monotonic() - started)
            atomic_json(destination, result)
        result = json.loads(destination.read_text())
        print(json.dumps({k: result.get(k) for k in ('status', 'seconds', 'encoded_inputs', 'variables', 'clauses')} | {'case': index}), flush=True)
    statuses = {}
    for index in range(len(cases)):
        path = args.out / f'case-{index:03d}.json'
        status = json.loads(path.read_text())['status'] if path.exists() else 'NOT_ATTEMPTED'
        statuses[status] = statuses.get(status, 0) + 1
    audit = dict(total_cases=len(cases), statuses=statuses,
                 outcome='UNSAT' if statuses.get('UNSAT') == len(cases) else
                         'COUNTEREXAMPLE' if statuses.get('SAT') else 'OPEN',
                 case_list_sha256=manifest['case_list_sha256'], proof_trace_checked=False)
    atomic_json(args.out / 'audit.json', audit)
    print(json.dumps(audit), flush=True)


if __name__ == '__main__':
    main()
