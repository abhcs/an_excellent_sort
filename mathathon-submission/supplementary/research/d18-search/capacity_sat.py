#!/usr/bin/env python3
"""Exact sorting-network SAT with proved last-two-layer capacity lemmas.

This keeps the original sorting constraints and adds necessary restrictions
on the number of states at the cut before the last two layers. A parent
process enforces a hard wall limit; a timeout is never an UNSAT result.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time

from pysat.card import ITotalizer
from netsat import Model, is_sorted, neg, prefix_images, sorted_mask, verify_all
from two_layer_profiles import accepted_inputs, capacity_patterns
from two_layer_topology import adjacent_matchings, normal_last_two
from two_real_graph import matchings

HERE = Path(__file__).resolve().parent


class CapacityModel(Model):
    def __init__(self, n, r, outputs, mode='profiles', solver='cadical195'):
        assert r >= 2 and mode in ('none', 'levels', 'profiles')
        self.capacity_mode = mode
        self.groups = {}
        self.thresholds = {}
        self.profile_edges = []
        self.capacity_input_clauses = 0
        super().__init__(n, r, outputs, phi=True, sym=False, cosat=False, solver=solver)
        before = self.nv, self.ncl
        if mode != 'none':
            self._state_supports()
        if mode == 'profiles':
            self._profile_path()
        self.capacity_base_variables = self.nv - before[0]
        self.capacity_base_clauses = self.ncl - before[1]

    def _state_supports(self):
        n = self.n
        for zeros in range(1, n):
            low, high = max(0, zeros - 3), min(n, zeros + 3)
            high_ones = ((1 << (n - high)) - 1) << high
            group = {}
            for positions in itertools.combinations(range(low, high), high - zeros):
                pattern = high_ones | sum(1 << a for a in positions)
                group[pattern] = self.new_var()
            self.groups[zeros] = group
            self.add([group[sorted_mask(n, n - zeros)]])  # The sorted anchor always occurs.
            with ITotalizer(lits=list(group.values()), ubound=min(5, len(group)), top_id=self.nv) as totalizer:
                self.nv = max(self.nv, totalizer.cnf.nv)
                for clause in totalizer.cnf.clauses:
                    self.add(clause)
                self.thresholds[zeros] = list(totalizer.rhs)
            self._cap(True, zeros, 5)

    def _cap(self, guard, zeros, bound):
        rhs = self.thresholds.get(zeros, [])
        if len(rhs) > bound:
            # rhs[bound] is forced when at least bound+1 support flags are true.
            self.add([neg(guard), -rhs[bound]])

    def _profile_path(self):
        n = self.n
        boundary = [self.new_var() for _ in range(n + 1)]
        self.add([boundary[0]])
        self.add([boundary[n]])
        incoming = [[] for _ in range(n + 1)]
        outgoing = [[] for _ in range(n + 1)]
        for left in range(n):
            for right in range(left + 1, n + 1):
                for pattern in sorted(set(tuple(p) for p in capacity_patterns(right - left))):
                    edge = self.new_var()
                    outgoing[left].append(edge)
                    incoming[right].append(edge)
                    self.add([-edge, boundary[left]])
                    self.add([-edge, boundary[right]])
                    for zeros in range(left + 1, right):
                        self._cap(edge, zeros, pattern[zeros - left])
                    self.profile_edges.append((left, right, pattern, edge))
        for vertex in range(n + 1):
            for arcs in (incoming[vertex], outgoing[vertex]):
                for a, b in itertools.combinations(arcs, 2):
                    self.add([-a, -b])
            if vertex > 0:
                self.add([-boundary[vertex]] + incoming[vertex])
            if vertex < n:
                self.add([-boundary[vertex]] + outgoing[vertex])
            if 0 < vertex < n:
                self._cap(boundary[vertex], vertex, 1)

    def _pen_units(self, current, low, high, zeros):
        super()._pen_units(current, low, high, zeros)
        if self.capacity_mode == 'none':
            return
        before = self.ncl
        for pattern, present in self.groups[zeros].items():
            clause = [present]
            for channel in range(max(0, zeros - 3), min(self.n, zeros + 3)):
                value = current.get(channel, bool(channel >= zeros))
                clause.append(neg(value) if pattern >> channel & 1 else value)
            self.add(clause)  # An equal state must have its support flag true.
        self.capacity_input_clauses += self.ncl - before


def atomic_json(path, result):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(result, indent=2) + '\n')
    temp.replace(path)


def source_hashes():
    return {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ('capacity_sat.py', 'netsat.py', 'two_layer_profiles.py',
                         'shared_ending_sat.py', 'two_layer_envelope.py')}


def worker(task_path):
    from cover_solve import relabel_prefix
    task = json.loads(task_path.read_text())
    start = time.monotonic()
    n, prefix = task['case']['n'], task['case']['layers']
    outputs = prefix_images(n, prefix)
    if task['relabel_trials']:
        prefix, labels, mapping, before, after = relabel_prefix(n, prefix, outputs, task['relabel_trials'])
        outputs = prefix_images(n, prefix)
    else:
        labels, mapping, before, after = list(range(n)), list(range(n)), None, None
    inputs = sorted(x for x in outputs if not is_sorted(x, n))
    result = dict(case_id=task['case'].get('case_id'), n=n, depth=task['depth'],
                  prefix=prefix, input_permutation=labels, output_permutation=mapping,
                  original_window_cost=before, window_cost=after, inputs=len(inputs),
                  mode=task['mode'], solver=task['solver'], source_hashes=task['source_hashes'],
                  cover_sha256=task.get('cover_sha256'), restriction='none beyond valid normal forms',
                  proof_status='solver result; not an independently checked proof trace')
    model_class = CapacityModel
    if task.get('encoding') == 'shared':
        from shared_ending_sat import SharedEndingModel
        model_class = SharedEndingModel
    result['encoding'] = task.get('encoding', 'direct')
    model = model_class(n, task['depth'] - len(prefix), inputs, task['mode'], task['solver'])
    try:
        for x in inputs:
            model.add_input(x)
        result.update(variables=model.nv, clauses=model.ncl,
                      capacity_base_variables=model.capacity_base_variables,
                      capacity_base_clauses=model.capacity_base_clauses,
                      capacity_input_clauses=model.capacity_input_clauses,
                      profile_arcs=len(model.profile_edges), build_seconds=time.monotonic() - start)
        if hasattr(model, 'shared_states'):
            result.update(shared_states=model.shared_states, forbidden_states=model.forbidden_states,
                          shared_variables=model.shared_variables, shared_clauses=model.shared_clauses)
        atomic_json(Path(task['progress_path']), dict(result, status='BUILT'))
        print(json.dumps({k: result[k] for k in ('case_id', 'variables', 'clauses', 'build_seconds',
                                                'capacity_base_clauses', 'capacity_input_clauses')}), flush=True)
        solve_start = time.monotonic()
        ok = model.S.solve()  # One call, including for the non-incremental Kissat backend.
        result.update(status='SAT' if ok else 'UNSAT', solve_seconds=time.monotonic() - solve_start,
                      seconds=time.monotonic() - start)
        if ok:
            net = prefix + model.network(model.S.get_model())
            assert verify_all(n, net)
            result.update(network=net, verified_binary_inputs=1 << n)
        atomic_json(Path(task['result_path']), result)
        print(result['status'], result['seconds'], flush=True)
    finally:
        model.S.delete()


def check(model_class=CapacityModel):
    start = time.monotonic()
    positives = 0
    # Fixed known endings exercise every small normal-form capacity shape,
    # including maximal accepted sets that need not themselves be prefix images.
    for n in range(2, 8):
        for last in adjacent_matchings(n):
            for first in matchings(n):
                if not normal_last_two(n, first, last):
                    continue
                accepted = accepted_inputs(n, [first, last])
                model = model_class(n, 2, accepted, 'profiles')
                try:
                    for t, layer in enumerate((first, last)):
                        chosen = set(layer)
                        for pair, var in model.g[t].items():
                            model.add([var if pair in chosen else -var])
                    for x in accepted:
                        if not is_sorted(x, n):
                            model.add_input(x)
                    assert model.S.solve(), (n, first, last)
                    positives += 1
                finally:
                    model.S.delete()
    cases = [json.loads(line) for line in (HERE / 'prefixes/complete9.jsonl').read_text().splitlines()]
    cases_unsat = 0
    for case in cases:
        outputs = prefix_images(9, case['layers'])
        model = model_class(9, 4, outputs, 'profiles')
        try:
            for x in outputs:
                if not is_sorted(x, 9):
                    model.add_input(x)
            assert not model.S.solve(), case['case_id']
            cases_unsat += 1
        finally:
            model.S.delete()
    case = cases[0]
    outputs = prefix_images(9, case['layers'])
    model = model_class(9, 5, outputs, 'profiles')
    try:
        for x in outputs:
            if not is_sorted(x, 9):
                model.add_input(x)
        assert model.S.solve()
        network = case['layers'] + model.network(model.S.get_model())
        assert verify_all(9, network)
    finally:
        model.S.delete()
    return dict(model=model_class.__name__, normal_ending_positive_controls=positives, complete_n9_d6_unsat_cases=cases_unsat,
                n9_d7_positive_verified_inputs=512, seconds=time.monotonic() - start)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--cover', type=Path)
    parser.add_argument('--case')
    parser.add_argument('--prefix', type=Path)
    parser.add_argument('--depth', type=int)
    parser.add_argument('--mode', choices=('none', 'levels', 'profiles'), default='profiles')
    parser.add_argument('--encoding', choices=('direct', 'shared'), default='direct')
    parser.add_argument('--solver', default='kissat404')
    parser.add_argument('--seconds', type=float, default=45)
    parser.add_argument('--relabel-trials', type=int, default=500)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    if args.check:
        if args.encoding == 'shared':
            from shared_ending_sat import SharedEndingModel
            result = check(SharedEndingModel)
        else:
            result = check()
        if args.out:
            atomic_json(args.out, result)
        print(json.dumps(result), flush=True)
        return
    if args.out is None or args.depth is None or (args.cover is None and args.prefix is None):
        parser.error('provide --out, --depth, and --cover/--case or --prefix')
    if args.out.exists():
        parser.error('choose a new output filename; completed attempts are not overwritten')
    cover_sha = None
    if args.cover:
        payload = args.cover.read_bytes()
        cover_sha = hashlib.sha256(payload).hexdigest()
        cases = [json.loads(line) for line in payload.splitlines()]
        selected = [case for case in cases if case['case_id'] == args.case]
        if len(selected) != 1:
            parser.error('select exactly one valid --case')
        case = selected[0]
    else:
        case = json.loads(args.prefix.read_text())
    progress = args.out.with_suffix('.progress.json')
    task_path = args.out.with_suffix('.task.json')
    log_path = args.out.with_suffix('.log')
    task = dict(case=case, depth=args.depth, mode=args.mode, solver=args.solver, encoding=args.encoding,
                relabel_trials=args.relabel_trials, source_hashes=source_hashes(), cover_sha256=cover_sha,
                result_path=str(args.out.resolve()), progress_path=str(progress.resolve()))
    atomic_json(task_path, task)
    started = time.monotonic()
    terminal = None
    with log_path.open('w') as log:
        try:
            child = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker', str(task_path.resolve())],
                                   stdout=log, stderr=subprocess.STDOUT, timeout=args.seconds)
            if child.returncode != 0:
                terminal = 'ERROR'
        except subprocess.TimeoutExpired:
            terminal = 'TIME_LIMIT'
    if terminal is not None:
        result = json.loads(progress.read_text()) if progress.exists() else dict(case_id=case.get('case_id'))
        result.update(status=terminal, seconds=time.monotonic() - started,
                      source_hashes=task['source_hashes'], cover_sha256=cover_sha,
                      depth=args.depth, mode=args.mode, solver=args.solver)
        atomic_json(args.out, result)
    assert args.out.exists(), 'child exited without a result'
    result = json.loads(args.out.read_text())
    print(json.dumps({k: result.get(k) for k in ('case_id', 'status', 'mode', 'variables', 'clauses',
                                               'build_seconds', 'seconds')}), flush=True)


if __name__ == '__main__':
    main()
