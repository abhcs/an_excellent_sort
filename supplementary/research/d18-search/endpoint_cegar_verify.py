#!/usr/bin/env python3
"""Independent scalar controls for the endpoint oracle and both SAT formulations."""
import hashlib
import itertools
import json
from pathlib import Path
import random

from endpoint_cegar import IntervalOracle, wire_endpoints
from interval_frontier import add_state_bounds
from netsat import apply_layers, neg, prefix_images
from probe_frontier import ProbeModel


def random_layer(n, rng):
    p = list(range(n))
    rng.shuffle(p)
    return sorted(tuple(sorted(p[k:k+2])) for k in range(0, 2*rng.randrange(n//2+1), 2))


def main():
    rng = random.Random(84192)
    tests = 0
    verdicts = {'SAT': 0, 'UNSAT': 0}
    pair_checks = 0
    for n in range(3, 7):
        for _ in range(16):
            prefix = [random_layer(n, rng)]
            free = [random_layer(n, rng), random_layer(n, rng)]
            universe = sorted(prefix_images(n, prefix))
            images = {x:apply_layers(free, x) for x in universe}
            oracle = IntervalOracle(n, universe)
            rows = oracle.evaluate(free)
            for c, row in enumerate(rows):
                lo = min(n-x.bit_count()-1 for x,y in images.items() if not (y>>c)&1)
                hi = max(n-x.bit_count() for x,y in images.items() if (y>>c)&1)
                assert (row['lo'], row['hi']) == (lo, hi)
                assert not (images[row['zero_witness']] >> c)&1
                assert (images[row['one_witness']] >> c)&1
            for cap in (2, 4):
                expected = all(row['width'] <= cap for row in rows)
                scalar_pairs = [(x,y) for x,y in itertools.product(universe,repeat=2)
                                if x.bit_count()-y.bit_count() >= cap-1]
                scalar_ok = all(not ((images[y] >> c)&1) or (images[x] >> c)&1
                                for x,y in scalar_pairs for c in range(n))
                assert bool(scalar_ok) == expected
                pair_checks += len(scalar_pairs)*n
                for mode in ('endpoints','pairs'):
                    model = ProbeModel(n, 3, universe, phi=False, nored0=False)
                    try:
                        for t, layer in enumerate(free+[[]]):
                            chosen = set(layer)
                            for edge, var in model.g[t].items():
                                model.add([var if edge in chosen else -var])
                        states = {x:model.simulate_to_cut(x, 2) for x in universe}
                        if mode == 'endpoints':
                            L,U = wire_endpoints(model,list(range(n)),cap)
                            for x in universe:
                                add_state_bounds(model,x,states[x],L,U)
                        else:
                            for x,y in scalar_pairs:
                                for c in range(n):
                                    model.add([states[x][c],neg(states[y][c])])
                        got = model.S.solve()
                        assert got == expected, (n,prefix,free,cap,mode,expected,got)
                        verdicts['SAT' if got else 'UNSAT'] += 1
                        tests += 1
                    finally:
                        model.S.delete()
    report = dict(status='VERIFIED', fixed_network_formulation_checks=tests,
                  verdicts=verdicts, scalar_wire_pair_checks=pair_checks,
                  scope='64 random tiny prefixes/continuations, two caps, two formulations; scalar exact controls',
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  encoder_sha256=hashlib.sha256(Path(__file__).with_name('endpoint_cegar.py').read_bytes()).hexdigest())
    path = Path(__file__).parent/'results/endpoint-cegar-verification.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
