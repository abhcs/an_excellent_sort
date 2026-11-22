#!/usr/bin/env python3
"""close_fixed.py n d HANDCERT.json OUT.jsonl: decide every left-over prefix of a hand-certificate
run by SAT with the WHOLE prefix fixed (only the free layers searched), using netsat's model and
CEGAR.  Writes one line per prefix; a FOUND line would refute the sparse-start statement."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'd18-search'))
from netsat import search

n, d = int(sys.argv[1]), int(sys.argv[2])
data = json.load(open(sys.argv[3]))
out = open(sys.argv[4], 'a')
for k, P in enumerate(data['uncertified_all']):
    prefix = [[tuple(c) for c in L] for L in P]
    t = time.time()
    res = search(n, prefix, d - len(prefix), log=lambda s: None)
    status = 'UNSAT' if res is None else ('FOUND' if isinstance(res, list) else str(res))
    out.write(json.dumps({'prefix': P, 'status': status, 'seconds': round(time.time() - t, 2)}) + '\n')
    out.flush()
    if status != 'UNSAT':
        print('NOT UNSAT', P, status, flush=True)
print('done', len(data['uncertified_all']), flush=True)
