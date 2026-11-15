#!/usr/bin/env python3
"""Combine all stored R7/R8 rescheduling demands with all R9 three-block cuts.

Every SAT worker and DRAT checker is externally capped at30seconds.
Only new round5 artifacts are written. A survivor is not a sorting network.
"""
import argparse
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time

from pysat.solvers import Solver
from d18_hand_next_reschedule import (PAIRS, G, CHECKER, build, check_values,
                                      digest, passes, replay, save)

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
COLLECTOR = Path('/private/tmp/d18_hand_round5_component_states')


def components(prefix, initial):
    """Independent adjacency-graph trace on original real register labels."""
    types = list(initial)
    labels = [v if x == 0 else -1 for v, x in enumerate(types)]
    graph = {v: set() for v, x in enumerate(types) if x == 0}
    for layer in prefix:
        for a, b in layer:
            if types[a] == types[b] == 0:
                x, y = labels[a], labels[b]
                graph[x].add(y)
                graph[y].add(x)
            elif types[a] > types[b]:
                types[a], types[b] = types[b], types[a]
                labels[a], labels[b] = labels[b], labels[a]
    unseen = set(graph)
    masks = []
    while unseen:
        stack = [unseen.pop()]
        group = set(stack)
        while stack:
            v = stack.pop()
            fresh = graph[v] & unseen
            unseen -= fresh
            group |= fresh
            stack.extend(fresh)
        masks.append(sum(1 << v for v, label in enumerate(labels) if label in group))
    return sorted(masks), labels


def three_partitions(k):
    """Each unordered partition of k components into three nonempty groups."""
    def visit(i, groups):
        if i == k:
            if len(groups) == 3:
                yield [g[:] for g in groups]
            return
        for g in groups:
            g.append(i)
            yield from visit(i + 1, groups)
            g.pop()
        if len(groups) < 3:
            groups.append([i])
            yield from visit(i + 1, groups)
            groups.pop()
    yield from visit(0, [])


def component_cuts(states):
    result = {}
    for index, state in enumerate(states):
        components = state['cut_component_masks']
        for partition in three_partitions(len(components)):
            blocks = [sum(components[i] for i in group) for group in partition]
            owner = {v: j for j, block in enumerate(blocks)
                     for v in range(18) if block >> v & 1}
            assert len(owner) == 9 and len(blocks) == 3
            clause = tuple(G[a, b] for a, b in PAIRS
                           if a in owner and b in owner and owner[a] != owner[b])
            result.setdefault(clause, dict(state_index=index, partition=partition,
                                           block_masks=blocks, clause=list(clause)))
    return list(result.values())


def replay_demands(data, layer):
    binary_runs = 0
    for item in data['rescheduling_items']:
        assert passes(item, layer)
        extended = replay(data['prefix'] + [layer], item['initial'])
        assert max(extended['depths']) >= 3 or extended['total'] >= {7: 5, 8: 7}[item['r']]
        binary_runs += check_values(data['prefix'], item)
    for state in data['component_collection']['witnesses']:
        after, _ = components(data['prefix'] + [layer], state['initial'])
        assert len(after) <= 2
    return dict(rescheduling_demands=len(data['rescheduling_items']),
                binary_normalization_replays=binary_runs,
                component_states=len(data['component_collection']['witnesses']),
                component_cuts=len(data['component_cuts']))


def worker(path):
    started = time.monotonic()
    data = json.loads(path.read_text())
    result_path = path.with_name(path.stem + '-result.json')
    items = data['rescheduling_items']
    for item in items:
        direct = replay(data['prefix'], item['initial'])
        assert all(direct[k] == item[k] for k in direct)
    for state in data['component_collection']['witnesses']:
        masks, labels = components(data['prefix'], state['initial'])
        assert masks == state['cut_component_masks']
        assert labels == state['final_labels']
    assert component_cuts(data['component_collection']['witnesses']) == data['component_cuts']
    clauses, variables, profile_groups = build(items)
    groups = [dict(g, kind='rescheduling', index=i) for i, g in enumerate(profile_groups)]
    for i, cut in enumerate(data['component_cuts']):
        variables += 1
        clauses.append([-variables] + cut['clause'])
        groups.append(dict(activation=variables, kind='component', index=i))
    result = dict(status='BUILT', case=data['case'],
                  scope='One common L6: all stored normalized R7/R8 rescheduling demands and all R9 three-component cuts',
                  rescheduling_groups=len(items), component_groups=len(data['component_cuts']),
                  component_states=len(data['component_collection']['witnesses']),
                  variables=variables, clauses=len(clauses),
                  source_sha256=digest(Path(__file__)), input_sha256=digest(path))
    save(result_path, result)
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        acts = [g['activation'] for g in groups]
        if solver.solve(assumptions=acts):
            model = set(solver.get_model())
            layer = [list(e) for e in PAIRS if G[e] in model]
            audit = replay_demands(data, layer)
            result.update(status='SURVIVOR', layer6=layer, direct_replay=audit,
                          seconds=time.monotonic() - started)
            save(result_path, result)
            print(json.dumps(result), flush=True)
            return
        core = solver.get_core()
        result.update(status='UNSAT_UNCHECKED', initial_core_size=len(core))
        save(result_path, result)
        for activation in list(core):
            trial = [v for v in core if v != activation]
            if not solver.solve(assumptions=trial):
                core = trial
    selected = [g for g in groups if g['activation'] in core]
    profile_indices = [g['index'] for g in selected if g['kind'] == 'rescheduling']
    component_indices = [g['index'] for g in selected if g['kind'] == 'component']
    proof_clauses, proof_variables, _ = build([items[i] for i in profile_indices], assumptions=False)
    proof_clauses += [data['component_cuts'][i]['clause'] for i in component_indices]
    directory = path.with_name(path.stem + '-certificate')
    directory.mkdir(exist_ok=True)
    (directory / 'problem.cnf').write_text(f'p cnf {proof_variables} {len(proof_clauses)}\n' +
        ''.join(' '.join(map(str, c)) + ' 0\n' for c in proof_clauses))
    with Solver(name='cadical195', bootstrap_with=proof_clauses, with_proof=True) as solver:
        assert not solver.solve()
        (directory / 'proof.drat').write_text('\n'.join(solver.get_proof()) + '\n')
    runs = sum(check_values(data['prefix'], items[i]) for i in profile_indices)
    result.update(status='UNSAT_UNCHECKED', core_is_deletion_minimal=True,
                  core_size=len(selected), core_rescheduling_indices=profile_indices,
                  core_component_indices=component_indices,
                  core_binary_normalization_replays=runs,
                  certificate_directory=str(directory), seconds=time.monotonic() - started)
    save(result_path, result)
    print(json.dumps(result), flush=True)


def bounded(cmd, seconds):
    started = time.monotonic()
    try:
        call = subprocess.run(cmd, capture_output=True, text=True, timeout=seconds)
        return dict(terminal='EXITED', returncode=call.returncode, stdout=call.stdout,
                    stderr=call.stderr, wall_cap_seconds=seconds, seconds=time.monotonic() - started)
    except subprocess.TimeoutExpired as error:
        def text(x):
            return x.decode() if isinstance(x, bytes) else (x or '')
        return dict(terminal='TIMEOUT_KILLED', stdout=text(error.stdout), stderr=text(error.stderr),
                    wall_cap_seconds=seconds, seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    subprocess.run(['c++', '-O3', '-std=c++17', str(HERE / 'merge_component_states.cpp'),
                    '-o', str(COLLECTOR)], check=True, capture_output=True, timeout=20)
    records = []
    for name in ('beam00', 'beam16', 'beam32'):
        previous = OUT / f'd18_hand_next_reschedule-{name}.json'
        old = json.loads(previous.read_text())
        mates = OUT / f'd18_hand_next_reschedule-{name}.txt'
        collected = subprocess.run([str(COLLECTOR), str(mates), 'three', 'all'],
                                   check=True, capture_output=True, text=True, timeout=20)
        collection = json.loads(collected.stdout)
        assert collection['all_unique_states_stored']
        cuts = component_cuts(collection['witnesses'])
        path = OUT / f'd18_hand_round5_combined-{name}.json'
        save(path, dict(case=name, prefix=old['prefix'], rescheduling_items=old['items'],
                        rescheduling_collections=old['collections'],
                        component_collection=collection, component_cuts=cuts,
                        rescheduling_source_sha256=digest(previous),
                        component_collector_sha256=digest(HERE / 'merge_component_states.cpp')))
        record = bounded([sys.executable, str(Path(__file__)), '--worker', str(path)], 30)
        record['case'] = name
        result_path = path.with_name(path.stem + '-result.json')
        if record['terminal'] == 'EXITED' and record['returncode'] == 0:
            result = json.loads(result_path.read_text())
            if result['status'] == 'UNSAT_UNCHECKED':
                directory = Path(result['certificate_directory'])
                checked = bounded([str(CHECKER), str(directory / 'problem.cnf'),
                                   str(directory / 'proof.drat')], 30)
                log = checked['stdout'] + checked['stderr']
                checked['verified'] = checked.get('returncode') == 0 and 's VERIFIED' in log
                (directory / 'check.log').write_text(log)
                save(directory / 'check-terminal.json', checked)
                if checked['verified']:
                    result['status'] = 'UNSAT_VERIFIED'
                    result['certificate_sha256'] = {p.name: digest(p) for p in directory.iterdir() if p.is_file()}
                    save(result_path, result)
                record['proof_check'] = checked
            record['result_status'] = result['status']
        save(path.with_name(path.stem + '-terminal.json'), record)
        records.append(record)
        save(OUT / 'd18_hand_round5_combined-audit.json', records)
        print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
