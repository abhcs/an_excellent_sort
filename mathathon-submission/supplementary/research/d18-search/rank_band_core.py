#!/usr/bin/env python3
"""Shrink the weight levels required for a fixed-prefix UNSAT result.

This is an experiment about necessary ordering conditions, not a hand proof.
All input simulation clauses are guarded by their weight-level selector. Shared
gate definitions are created first and remain unguarded. End normal forms and
redundancy restrictions refer to the FULL prefix image throughout.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from netsat import Model, is_sorted, prefix_images, apply_layers


class GuardedModel(Model):
    def __init__(self, *args, **kwargs):
        self.guard = None
        super().__init__(*args, **kwargs)
        # These definitions are cached across inputs: never guard them.
        for t in range(self.r):
            for k in range(self.n):
                for e in range(k, self.n):
                    self.Down(t, k, e)
                for a in range(k + 1):
                    self.Up(t, a, k)

    def add(self, clause):
        if self.guard is not None:
            clause = [-self.guard, *clause]
        super().add(clause)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--result', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds-per-call', type=float, default=15)
    args = ap.parse_args()
    original = json.loads(args.result.read_text())
    prefix, n = original['prefix'], len(original['output_permutation'])
    universe = sorted(x for x in prefix_images(n, prefix) if not is_sorted(x, n))
    m = GuardedModel(n, original['depth'] - len(prefix), universe)
    selectors = {w: m.new_var() for w in range(1, n)}
    for x in universe:
        m.guard = selectors[x.bit_count()]
        m.add_input(x)
    m.guard = None
    records = []
    # A conflict budget, rather than threads, keeps every solve interruptible.
    # The wrapper process imposes the separate wall-clock limit.
    def solve(weights, name):
        start = time.monotonic()
        m.S.conf_budget(100000)
        ok = m.S.solve_limited(assumptions=[selectors[w] for w in weights])
        record = dict(name=name, weights=weights, status={True:'SAT',False:'UNSAT',None:'LIMIT'}[ok],
                      seconds=round(time.monotonic()-start,3))
        if ok is False:
            core = set(m.S.get_core())
            record['core_weights'] = [w for w in weights if selectors[w] in core]
        elif ok is True:
            suffix = m.network(m.S.get_model())
            assert all(is_sorted(apply_layers(suffix,x),n) for x in universe if x.bit_count() in weights)
            record['suffix'] = suffix
        records.append(record)
        print(json.dumps({k:v for k,v in record.items() if k!='suffix'}),flush=True)
        args.out.write_text(json.dumps(dict(case_id=original['case_id'],n=n,depth=original['depth'],
            prefix=prefix,records=records,normal_forms='full-image redundancy and phi1..4',
            independently_proof_checked=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
        return record
    try:
        # Ask first whether a compact symmetric band already suffices.
        record = solve(list(range(4,10)), 'central-six-levels')
        if record['status'] != 'UNSAT':
            record = solve(list(range(1,n)), 'all-levels')
        if record['status'] != 'UNSAT':
            return
        keep = record['core_weights']
        for w in sorted(keep, key=lambda w:(-abs(w-n/2),w)):
            if w not in keep:
                continue
            result = solve([k for k in keep if k!=w], f'delete-{w}')
            if result['status']=='UNSAT':
                keep = result['core_weights']
        print('FINAL_CORE',keep,flush=True)
    finally:
        m.S.delete()


if __name__ == '__main__':
    main()
