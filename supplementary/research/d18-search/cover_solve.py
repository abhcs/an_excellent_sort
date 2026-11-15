#!/usr/bin/env python3
"""Bounded, resumable exact completion tests for a COMPLETE prefix cover.

No self-duality restriction. Every SAT witness is checked on all binary inputs.
Timeouts/errors are never interpreted as UNSAT. Results are bound to the cover,
case, depth, and encoder-source digests. A complete UNSAT ledger is still a
solver-based result, not an independently proof-checked DRAT/LRAT certificate.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def atomic_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def encoding_digest():
    return hashlib.sha256((HERE / 'netsat.py').read_bytes()).hexdigest()


def relabel_prefix(n, prefix, outputs, trials):
    from relabel import untangle

    def cost(mapping):
        cut = n // 2
        tables = []
        for start, size in [(0, cut), (cut, n - cut)]:
            table = [0] * (1 << size)
            for x in range(1, len(table)):
                low = x & -x
                table[x] = table[x ^ low] | (1 << mapping[start + low.bit_length() - 1])
            tables.append(table)
        mask = (1 << n) - 1
        lower = (1 << cut) - 1
        total = 0
        for x in outputs:
            y = tables[0][x & lower] | tables[1][x >> cut]
            if y == 0 or y == mask:
                continue
            a = (y & -y).bit_length() - 1
            b = (mask ^ y).bit_length() - 1
            if a < b:
                w = b - a + 1
                total += w * (w - 1) // 2 + w
        return total

    lab = list(range(n))
    _, mapping = untangle(prefix, lab)
    initial = best = cost(mapping)
    rng = random.Random(20261115)
    # Deterministic hill climbing. Relabelling + untangling preserves existence
    # of a completion; this changes the encoding size, not the search scope.
    for _ in range(trials):
        a, b = rng.sample(range(n), 2)
        lab[a], lab[b] = lab[b], lab[a]
        _, mapping = untangle(prefix, lab)
        value = cost(mapping)
        if value <= best:
            best = value
        else:
            lab[a], lab[b] = lab[b], lab[a]
    prefix2, mapping = untangle(prefix, lab)
    return prefix2, lab, mapping, initial, best


def worker(spec_path):
    from netsat import Model, is_sorted, prefix_images, verify_all
    from relabel import relabel_vec
    task = json.loads(spec_path.read_text())
    record = task['case']
    n, depth = record['n'], task['depth']
    prefix = record['layers']
    start = time.monotonic()
    outputs = prefix_images(n, prefix)
    assert len(outputs) == record['outputs']
    prefix2, lab, mapping, before, after = relabel_prefix(n, prefix, outputs, task['relabel_trials'])
    mapped = {relabel_vec(x, mapping, n) for x in outputs}
    assert mapped == prefix_images(n, prefix2), 'relabelled output-set mismatch'
    inputs = sorted(x for x in mapped if not is_sorted(x, n))
    result = {k: task[k] for k in ('problem_id', 'cover_sha256', 'encoder_sha256', 'depth', 'solver')}
    result.update(case_id=record['case_id'], prefix=prefix2, input_permutation=lab,
                  output_permutation=mapping, inputs=len(inputs),
                  original_window_cost=before, window_cost=after,
                  restriction='none beyond documented valid normal forms',
                  proof_status='solver result; no independently checked proof trace')
    model = Model(n, depth - len(prefix2), inputs, solver=task['solver'])
    try:
        for x in inputs:
            model.add_input(x)
        result.update(variables=model.nv, clauses=model.ncl,
                      build_seconds=round(time.monotonic() - start, 3))
        print(json.dumps({k: result[k] for k in ('case_id', 'inputs', 'variables', 'clauses', 'build_seconds')}), flush=True)
        ok = model.S.solve()  # Exactly one call, also valid for Kissat.
        result['status'] = 'SAT' if ok else 'UNSAT'
        if ok:
            net = prefix2 + model.network(model.S.get_model())
            assert len(net) == depth and verify_all(n, net), 'SAT witness fails exhaustive checking'
            result.update(network=net, verified_binary_inputs=1 << n)
        result['seconds'] = round(time.monotonic() - start, 3)
        atomic_json(Path(task['result_path']), result)
        print(result['status'], result['seconds'], flush=True)
    finally:
        model.S.delete()


def make_task(case, args, cover_sha):
    identity = dict(case=case, depth=args.depth, cover_sha256=cover_sha,
                    encoder_sha256=encoding_digest())
    return dict(**identity, solver=args.solver, relabel_trials=args.relabel_trials,
                problem_id=digest(identity))


def valid_record(path, task):
    if not path.exists():
        return None
    record = json.loads(path.read_text())
    if record.get('problem_id') != task['problem_id']:
        return None
    if record.get('status') == 'SAT':
        from netsat import verify_all
        assert len(record['network']) == task['depth']
        assert verify_all(task['case']['n'], record['network'])
    return record


def audit(cases, args, sha):
    counts = Counter()
    for case in cases:
        task = make_task(case, args, sha)
        record = valid_record(args.out / case['case_id'] / 'result.json', task)
        counts[record['status'] if record else 'NOT_SOLVED'] += 1
    outcome = 'OPEN'
    if counts['SAT']:
        outcome = 'VERIFIED_SORTER_FOUND'
    elif counts['UNSAT'] == len(cases):
        outcome = 'ALL_CASES_UNSAT_SOLVER_BASED'
    report = dict(n=cases[0]['n'], depth=args.depth, cover_sha256=sha,
                  total_cases=len(cases), statuses=dict(counts), outcome=outcome,
                  independently_proof_checked=False)
    atomic_json(args.out / 'audit.json', report)
    print(json.dumps(report), flush=True)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cover', type=Path)
    ap.add_argument('--depth', type=int)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--case', action='append', help='case ID; omit to process the entire cover')
    ap.add_argument('--limit', type=int, help='maximum number of selected cases in this invocation')
    ap.add_argument('--seconds', type=float, default=600)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--relabel-trials', type=int, default=200)
    ap.add_argument('--audit', action='store_true')
    ap.add_argument('--worker', type=Path, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        worker(args.worker)
        return
    if args.cover is None or args.depth is None or args.out is None:
        ap.error('--cover, --depth, and --out are required')
    payload = args.cover.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    summary = json.loads(args.cover.with_suffix('.summary.json').read_text())
    assert sha == summary['sha256'], 'cover digest mismatch'
    cases = [json.loads(x) for x in payload.splitlines() if x]
    assert len(cases) == summary['cases']
    assert len({c['case_id'] for c in cases}) == len(cases)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.audit:
        audit(cases, args, sha)
        return
    selected = [c for c in cases if args.case is None or c['case_id'] in args.case]
    if args.case and len(selected) != len(set(args.case)):
        ap.error('unknown case ID')
    if args.limit is not None:
        selected = selected[:args.limit]
    for case in selected:
        work = args.out / case['case_id']
        work.mkdir(exist_ok=True)
        task = make_task(case, args, sha)
        result_path = work / 'result.json'
        previous = valid_record(result_path, task)
        if previous and previous['status'] in ('UNSAT', 'SAT'):
            print(case['case_id'], 'already', previous['status'], flush=True)
            continue
        # Keep completed prior attempts, including timeouts, instead of
        # silently overwriting evidence. No log file is treated as liveness.
        attempt = 1
        while (work / f'attempt-{attempt:03d}.json').exists():
            attempt += 1
        task['result_path'] = str((work / f'attempt-{attempt:03d}.json').resolve())
        spec_path = work / f'task-{attempt:03d}.json'
        atomic_json(spec_path, task)
        start = time.monotonic()
        print('starting', case['case_id'], 'attempt', attempt, flush=True)
        status = None
        with (work / f'attempt-{attempt:03d}.log').open('w') as log:
            try:
                child = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                        '--worker', str(spec_path.resolve())],
                                       stdout=log, stderr=subprocess.STDOUT, timeout=args.seconds)
                if child.returncode != 0:
                    status = 'ERROR'
            except subprocess.TimeoutExpired:
                status = 'TIME_LIMIT'
            except KeyboardInterrupt:
                status = 'INTERRUPTED'
        completed = Path(task['result_path'])
        if status is None and completed.exists():
            result = json.loads(completed.read_text())
            assert result['problem_id'] == task['problem_id']
            assert result['status'] in ('SAT', 'UNSAT')
        else:
            result = dict(problem_id=task['problem_id'], case_id=case['case_id'],
                          cover_sha256=sha, encoder_sha256=task['encoder_sha256'],
                          status=status or 'ERROR', seconds=round(time.monotonic() - start, 3))
            atomic_json(completed, result)
        atomic_json(result_path, result)
        print(case['case_id'], result['status'], result['seconds'], flush=True)
        if result['status'] in ('SAT', 'INTERRUPTED'):
            break
    audit(cases, args, sha)


if __name__ == '__main__':
    main()
