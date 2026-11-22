#!/usr/bin/env python3
"""exc_cert.py n d a OUT.json: hand certificates for the EXCEPTIONAL prefixes at level (n, a).

In the descent, a network whose first layer has exactly a comparators and whose layers 2, 3 have at
most a either has a good sentinel track (then the descent moves to (n-1, a-1)) or is exceptional.
This enumerates every three-layer prefix (layer 2 over the symmetry classes, layer 3 over all
matchings with at most a comparators), keeps the exceptional ones, and asks prefix_cert.certify for
a certificate that no completion to depth d sorts."""
import itertools, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prefix_cert import certify
from static_cert import static_certify
from l2classes import classes
from descent import track
from prefix_cert_all import matchings  # noqa: E402  (module runs nothing on import? guard below)


def exceptional(n, a, layers, m=3):
    full = [len(layers[t]) == a for t in range(m)]
    for lo, hi in layers[0]:
        for start, sign in ((hi, 1), (lo, -1)):
            _, meets = track(layers, start, sign, upto=m)
            if all(meets[t] or not full[t] for t in range(1, m)):
                return False
    return True


if __name__ == '__main__':
    n, d, a = map(int, sys.argv[1:4])
    out = sys.argv[4]
    L1, reps = classes(n, a)
    L1 = [tuple(p) for p in L1]
    later = matchings(n, a)
    t0 = time.time()
    total = exc = 0
    stats, uncert = {}, []
    for l2, _ in reps:
        l2 = [tuple(p) for p in l2]
        for l3 in later:
            layers = [L1, l2, list(l3)]
            total += 1
            if not exceptional(n, a, layers):
                continue
            exc += 1
            c = certify(n, d, a, 3, layers)
            key = 'none' if c is None else f'{c[0]}/k={c[1]}'
            if c is None:
                sc = static_certify(n, layers, d - 3)
                if sc is not None:
                    c = ('static', sc)
                    key = 'static chains ' + ','.join(map(str, sc['chains']))
            stats[key] = stats.get(key, 0) + 1
            if c is None:
                uncert.append(layers)
    res = {'level': [n, a], 'depth': d, 'prefixes': total, 'exceptional': exc, 'by_rule': stats,
           'uncertified': len(uncert), 'uncertified_examples': uncert[:20], 'uncertified_all': uncert,
           'seconds': round(time.time() - t0, 1)}
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ('uncertified_examples', 'uncertified_all')}))
