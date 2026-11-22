#!/usr/bin/env python3
"""prefix_cert_all.py n d a m OUT.json: certify EVERY prefix of SS(n,d,a,m) with prefix_cert.certify.
Layer 1 = middle_layer(n,a); layer 2 runs over the class representatives of l2classes.py (the
symmetry argument of README section 6); layers 3..m over all matchings with at most a comparators.
Records how many prefixes each rule settles and lists every prefix left uncertified."""
import itertools, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prefix_cert import certify
from l2classes import classes


def matchings(n, cap):
    edges = list(itertools.combinations(range(n), 2))
    out = []

    def go(start, used, cur):
        out.append(list(cur))
        if len(cur) == cap:
            return
        for k in range(start, len(edges)):
            u, v = edges[k]
            if u in used or v in used:
                continue
            cur.append((u, v)); used |= {u, v}
            go(k + 1, used, cur)
            cur.pop(); used -= {u, v}
    go(0, set(), [])
    return out


if __name__ == '__main__':
    n, d, a, m = map(int, sys.argv[1:5])
    out_path = sys.argv[5]
    only = None
    if len(sys.argv) > 6:                      # optional comma-separated layer-2 class indices
        only = {int(x) for x in sys.argv[6].split(',')}
    L1, reps = classes(n, a)
    L1 = [tuple(p) for p in L1]
    later = matchings(n, a)
    t0 = time.time()
    stats, uncert, total = {}, [], 0
    for ci, (l2, orb) in enumerate(reps):
        if only is not None and ci not in only:
            continue
        l2 = [tuple(p) for p in l2]
        for rest in itertools.product(later, repeat=m - 2):
            layers = [L1, l2] + [list(L) for L in rest]
            total += 1
            c = certify(n, d, a, m, layers)
            key = 'none' if c is None else f'{c[0]}/k={c[1]}'
            stats[key] = stats.get(key, 0) + 1
            if c is None:
                uncert.append(layers)
        print(f'class {ci}/{len(reps)} done: {total} prefixes, {len(uncert)} uncertified, {time.time() - t0:.0f}s', flush=True)
    res = {'statement': f'SS({n},{d},{a},{m})', 'L1': L1, 'second_layer_classes': len(reps),
           'prefixes_checked': total, 'by_rule': stats, 'uncertified': len(uncert),
           'uncertified_examples': uncert[:20], 'uncertified_all': uncert, 'seconds': round(time.time() - t0, 1)}
    json.dump(res, open(out_path, 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ('uncertified_examples', 'uncertified_all')}))
