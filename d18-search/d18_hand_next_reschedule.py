#!/usr/bin/env python3
"""One unknown D18 L6, constrained by normalized retained two-layer profiles.

Each subprocess solve and independent proof check has a hard 30-second cap.
SURVIVOR means this necessary condition passes, never that a sorter exists.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
PAIRS = list(itertools.combinations(range(18), 2))
G = {e: i + 1 for i, e in enumerate(PAIRS)}
CHECKER = Path('/private/tmp/d18-structural-drat-trim/drat-trim')


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(prefix, initial):
    """Independent register-level normalization, retaining the first gate."""
    values = list(initial)
    at = [v if x == 0 else None for v, x in enumerate(values)]
    last = {}
    low = {}
    heights = {v: 0 for v in at if v is not None}
    gates = []
    for layer in prefix:
        for a, b in layer:
            if values[a] == values[b] == 0:
                x, y = at[a], at[b]
                if last.get(x) == y and last.get(y) == x:
                    if not low[x]:
                        at[a], at[b] = y, x
                else:
                    level = max(heights[x], heights[y]) + 1
                    heights[x] = heights[y] = level
                    last[x], last[y] = y, x
                    low[x], low[y] = True, False
                    gates.append([x, y, level])
            elif values[a] > values[b]:
                values[a], values[b] = values[b], values[a]
                at[a], at[b] = at[b], at[a]
    mask = sum(1 << v for v, x in enumerate(values) if x == 0)
    depths = [heights[x] if x is not None else -1 for x in at]
    repeated = [18 * a + b for a, b in PAIRS if at[a] is not None and at[b] is not None
                and last.get(at[a]) == at[b] and last.get(at[b]) == at[a]]
    return dict(real_mask=mask, deep_mask=sum(1 << v for v, h in enumerate(depths) if h == 2),
                total=len(gates), labels=[-1 if x is None else x for x in at],
                depths=depths, repeat_codes=repeated, gates=gates)


def passes(item, layer):
    new = [(a, b) for a, b in layer
           if item['real_mask'] >> a & 1 and item['real_mask'] >> b & 1
           and 18 * a + b not in item['repeat_codes']]
    return (any(item['deep_mask'] & ((1 << a) | (1 << b)) for a, b in new)
            or len(new) + item['total'] >= {7: 5, 8: 7}[item['r']])


def build(items, assumptions=True):
    pool = IDPool(start_from=154)
    clauses = []
    for v in range(18):
        incident = [G[e] for e in PAIRS if v in e]
        clauses.extend([-a, -b] for a, b in itertools.combinations(incident, 2))
    groups = []
    for item in items:
        rr = [(a, b) for a, b in PAIRS
              if item['real_mask'] >> a & 1 and item['real_mask'] >> b & 1
              and 18 * a + b not in item['repeat_codes']]
        escape = [G[a, b] for a, b in rr if item['deep_mask'] & ((1 << a) | (1 << b))]
        card = CardEnc.atleast([G[e] for e in rr], {7: 5, 8: 7}[item['r']] - item['total'],
                              vpool=pool, encoding=EncType.seqcounter)
        activation = pool.id() if assumptions else None
        start = len(clauses)
        guard = ([-activation] if assumptions else []) + escape
        clauses.extend(guard + clause for clause in card.clauses)
        groups.append(dict(activation=activation, clause_start=start, clause_stop=len(clauses)))
    return clauses, pool.top, groups


def check_values(prefix, item):
    """All binary real values verify register normalization (threshold principle)."""
    initial = item['initial']
    real_inputs = [v for v, x in enumerate(initial) if x == 0]
    count = 0
    types = list(initial)
    for layer in prefix:
        for a, b in layer:
            types[a], types[b] = min(types[a], types[b]), max(types[a], types[b])
    for vals in itertools.product((0, 1), repeat=len(real_inputs)):
        actual = [-2 if x < 0 else 2 if x > 0 else 0 for x in initial]
        registers = dict(zip(real_inputs, vals))
        for v, val in registers.items():
            actual[v] = val
        for layer in prefix:
            for a, b in layer:
                actual[a], actual[b] = min(actual[a], actual[b]), max(actual[a], actual[b])
        for a, b, _ in item['gates']:
            registers[a], registers[b] = min(registers[a], registers[b]), max(registers[a], registers[b])
        predicted = [registers[label] if label >= 0 else (-2 if t < 0 else 2)
                     for label, t in zip(item['labels'], types)]
        assert actual == predicted
        count += 1
    return count


def worker(path):
    data = json.loads(path.read_text())
    result_path = path.with_name(path.stem + '-result.json')
    items = data['items']
    prefix = data['prefix']
    started = time.monotonic()
    for item in items:
        direct = replay(prefix, item['initial'])
        assert all(direct[key] == item[key] for key in direct)
    clauses, variables, groups = build(items)
    result = dict(status='BUILT', item_count=len(items), variables=variables, clauses=len(clauses),
                  scope='Necessary normalized two-layer rescheduling condition for one common L6',
                  input_sha256=digest(path), source_sha256=digest(Path(__file__)))
    save(result_path, result)
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        acts = [g['activation'] for g in groups]
        sat = solver.solve(assumptions=acts)
        if sat:
            model = set(solver.get_model())
            layer = [e for e in PAIRS if G[e] in model]
            assert all(passes(item, layer) for item in items)
            for item in items:
                extended = replay(prefix + [layer], item['initial'])
                assert max(extended['depths']) >= 3 or extended['total'] >= {7: 5, 8: 7}[item['r']]
            result.update(status='SURVIVOR', layer6=layer, replayed_restrictions=len(items),
                          seconds=time.monotonic()-started)
            save(result_path, result)
            print(json.dumps(result), flush=True)
            return
        core = solver.get_core()
        # Deletion-minimal semantic group core, bounded by the external cap.
        for a in list(core):
            trial = [x for x in core if x != a]
            if not solver.solve(assumptions=trial):
                core = trial
        core_indices = [i for i, g in enumerate(groups) if g['activation'] in core]
    selected = [items[i] for i in core_indices]
    proof_clauses, proof_variables, _ = build(selected, assumptions=False)
    cert_dir = path.with_name(path.stem + '-certificate')
    cert_dir.mkdir(exist_ok=True)
    cnf_path = cert_dir / 'problem.cnf'
    cnf_path.write_text(f'p cnf {proof_variables} {len(proof_clauses)}\n' +
                        ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in proof_clauses))
    with Solver(name='cadical195', bootstrap_with=proof_clauses, with_proof=True) as solver:
        assert not solver.solve()
        proof = solver.get_proof()
    (cert_dir / 'proof.drat').write_text('\n'.join(proof) + '\n')
    value_runs = sum(check_values(prefix, item) for item in selected)
    result.update(status='UNSAT_UNCHECKED', core_indices=core_indices, core_restrictions=selected,
                  core_size=len(selected), core_is_deletion_minimal=True,
                  direct_binary_normalization_runs=value_runs,
                  certificate_dir=str(cert_dir), seconds=time.monotonic()-started)
    save(result_path, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'core_restrictions'}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--worker', type=Path)
    args = ap.parse_args()
    if args.worker:
        worker(args.worker)
        return
    source = HERE / 'prefixes/symbeam_pb_d5.jsonl'
    beam = [json.loads(line) for line in source.read_text().splitlines()]
    combined = json.loads((OUT / 'combined-prefix-probe18.json').read_text())
    cases = [('combined', combined)] + [(f'beam{i:02d}', beam[i]) for i in (0, 16, 32)]
    audit = []
    for name, case in cases:
        stem = 'd18_hand_next_reschedule-' + name
        prefix = case['layers'][:5]
        mates = []
        for layer in prefix:
            row = [-1] * 18
            for a, b in layer:
                row[a], row[b] = b, a
            mates.append(row)
        txt = OUT / (stem + '.txt')
        txt.write_text('18 5\n' + '\n'.join(' '.join(map(str, row)) for row in mates) + '\n')
        items = []
        collections = []
        for r in (7, 8):
            begin = time.monotonic()
            call = subprocess.run(['/private/tmp/d18_hand_next_reschedule_states', str(txt), str(r), '1'],
                                  capture_output=True, text=True, timeout=10)
            assert call.returncode == 0, call.stderr
            collection = json.loads(call.stdout)
            collection['seconds'] = time.monotonic() - begin
            collections.append({k: v for k, v in collection.items() if k != 'states'})
            items.extend(dict(item, r=r) for item in collection['states'])
        path = OUT / (stem + '.json')
        save(path, dict(prefix=prefix, collections=collections, items=items,
                        collector_sha256=digest(HERE / 'd18_hand_next_reschedule_states.cpp')))
        record = dict(case=name, collections=collections, items=len(items), wall_cap_seconds=30)
        begin = time.monotonic()
        try:
            call = subprocess.run([sys.executable, str(Path(__file__)), '--worker', str(path)],
                                  capture_output=True, text=True, timeout=30)
            record.update(terminal='EXITED', returncode=call.returncode, stdout=call.stdout, stderr=call.stderr)
        except subprocess.TimeoutExpired as e:
            record.update(terminal='TIMEOUT_KILLED', stdout=str(e.stdout), stderr=str(e.stderr))
        record['seconds'] = time.monotonic() - begin
        result_path = path.with_name(path.stem + '-result.json')
        if record['terminal'] == 'EXITED' and record['returncode'] == 0:
            result = json.loads(result_path.read_text())
            if result['status'] == 'UNSAT_UNCHECKED':
                directory = Path(result['certificate_dir'])
                check_started = time.monotonic()
                try:
                    checked = subprocess.run([str(CHECKER), str(directory / 'problem.cnf'), str(directory / 'proof.drat')],
                                             capture_output=True, text=True, timeout=30)
                    log = checked.stdout + checked.stderr
                    check = dict(terminal='EXITED', returncode=checked.returncode,
                                 verified=checked.returncode == 0 and 's VERIFIED' in log,
                                 seconds=time.monotonic() - check_started, wall_cap_seconds=30)
                    (directory / 'check.log').write_text(log)
                except subprocess.TimeoutExpired:
                    check = dict(terminal='TIMEOUT_KILLED', verified=False, wall_cap_seconds=30,
                                 seconds=time.monotonic() - check_started)
                save(directory / 'check-terminal.json', check)
                if check['verified']:
                    result['status'] = 'UNSAT_VERIFIED'
                    result['certificate_sha256'] = {p.name: digest(p) for p in directory.iterdir() if p.is_file()}
                    save(result_path, result)
                record['check'] = check
            record['result_status'] = result['status']
            record['core_size'] = result.get('core_size')
        save(OUT / (stem + '-terminal.json'), record)
        audit.append(record)
        save(OUT / 'd18_hand_next_reschedule-audit.json', audit)
        print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
