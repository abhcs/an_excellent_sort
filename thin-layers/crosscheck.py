#!/usr/bin/env python3
"""crosscheck.py n depth a capped L2JSON: re-decide one case with the independent, plain encoder
depth-hand-proofs/verify/satnet.py (every prefix image encoded, full value equivalences, no end-game
constraints except the adjacent last layer, no CEGAR).  Prefix = middle_layer(n,a) then L2; layer 3
(the first free layer) is capped at a when capped >= 3."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'depth-hand-proofs', 'verify'))
sys.path.insert(0, HERE)
from satnet import Encoding, adjacent_pairs, solve, sorts  # noqa: E402
from thinsat import middle_layer  # noqa: E402

n, depth, a, capped = map(int, sys.argv[1:5])
l2 = [tuple(p) for p in json.loads(sys.argv[5])]
prefix = [middle_layer(n, a), l2]
free = depth - 2
caps = [a if 3 + t <= capped else None for t in range(free)]
allowed = [None] * (free - 1) + [adjacent_pairs(n)]
t = time.time()
enc = Encoding(n, free, caps=caps, prefix=prefix, allowed=allowed)
ok, model = solve(enc, sys.argv[6] if len(sys.argv) > 6 else 'cadical195')
res = {'n': n, 'depth': depth, 'a': a, 'capped': capped, 'l2': l2, 'encoder': 'satnet.py',
       'vars': enc.nvars, 'clauses': len(enc.clauses), 'result': 'SAT' if ok else 'UNSAT',
       'seconds': round(time.time() - t, 1)}
if ok:
    net = prefix + enc.network(model)
    res['network'] = net
    res['verified_sorts'] = sorts(net, n)
print(json.dumps(res), flush=True)
