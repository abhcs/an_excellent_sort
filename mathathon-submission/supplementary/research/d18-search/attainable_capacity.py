#!/usr/bin/env python3
"""Bounded tests of whether a whole accepted weight level is a prefix image.

This is an experiment, not a universal lower-bound proof. The suffix is fixed.
Every positive result includes a full independently checked sorting network
and actual input witnesses for every requested intermediate state.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from netsat import Model, apply_layers, is_sorted, neg, verify_all
from two_layer_profiles import accepted_inputs


class ObservedModel(Model):
    def __init__(self, n, depth, zeros):
        self.target_zeros = zeros
        self.observations = []
        self.current_input = None
        super().__init__(n, depth, range(1 << n), nored0=False)

    def add_input(self, x):
        self.current_input = x
        super().add_input(x)

    def _pen_units(self, current, low, high, zeros):
        super()._pen_units(current, low, high, zeros)
        if zeros == self.target_zeros:
            self.observations.append((self.current_input, dict(current)))

    def require_output(self, pattern):
        if is_sorted(pattern, self.n):
            return
        witnesses = []
        for _, current in self.observations:
            flag = self.new_var()
            witnesses.append(flag)
            for channel in range(self.n):
                value = current.get(channel, bool(channel >= self.target_zeros))
                self.add([-flag, value if pattern >> channel & 1 else neg(value)])
        self.add(witnesses)


def worker(args):
    n = args.n
    suffix = [[(i, i + 1) for i in range(0, n - 1, 2)],
              [(i, i + 1) for i in range(1, n - 1, 2)]]
    targets = sorted(x for x in accepted_inputs(n, suffix) if n - x.bit_count() == args.zeros)
    model = ObservedModel(n, args.depth, args.zeros)
    try:
        for offset, layer in enumerate(suffix):
            chosen = set(layer)
            for pair, gate in model.g[args.depth - 2 + offset].items():
                model.add([gate if pair in chosen else -gate])
        for x in range(1 << n):
            if not is_sorted(x, n):
                model.add_input(x)
        for pattern in targets:
            model.require_output(pattern)
        progress = dict(n=n, depth=args.depth, zeros=args.zeros, suffix=suffix,
                        target_states=targets, variables=model.nv, clauses=model.ncl,
                        status='BUILT', scope='fixed ending and specified depth only')
        print(json.dumps(progress), flush=True)
        if args.out:
            args.out.write_text(json.dumps(progress, indent=2) + '\n')
        ok = model.S.solve()
        progress['status'] = 'SAT' if ok else 'UNSAT'
        if ok:
            network = model.network(model.S.get_model())
            assert verify_all(n, network)
            observed = {}
            for x in range(1 << n):
                observed.setdefault(apply_layers(network[:-2], x), x)
            assert all(x in observed for x in targets)
            progress.update(network=network, witnesses=[dict(input=observed[x], output=x) for x in targets],
                            verified_binary_inputs=1 << n)
        if args.out:
            args.out.write_text(json.dumps(progress, indent=2) + '\n')
        print(json.dumps(progress), flush=True)
    finally:
        model.S.delete()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, required=True)
    parser.add_argument('--depth', type=int, required=True)
    parser.add_argument('--zeros', type=int, required=True)
    parser.add_argument('--seconds', type=float, default=10)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return
    assert not args.out.exists(), 'Use a fresh output path.'
    start = time.monotonic()
    with args.out.with_suffix('.log').open('w') as log:
        try:
            result = subprocess.run([sys.executable, __file__, '--worker', '--n', str(args.n),
                                     '--depth', str(args.depth), '--zeros', str(args.zeros),
                                     '--out', str(args.out)], stdout=log, stderr=subprocess.STDOUT,
                                    timeout=args.seconds)
            terminal = 'ERROR' if result.returncode else None
        except subprocess.TimeoutExpired:
            terminal = 'TIME_LIMIT'
    data = json.loads(args.out.read_text()) if args.out.exists() else dict(n=args.n, depth=args.depth)
    if terminal:
        data['status'] = terminal
    data['seconds'] = time.monotonic() - start
    args.out.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data), flush=True)


if __name__ == '__main__':
    main()
