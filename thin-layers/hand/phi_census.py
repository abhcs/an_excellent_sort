"""Phi_3 (hand/phi.py) over sampled S14 root children: exceptional ones from many cases, and
non-exceptional ones for contrast.  usage: CASES_SAMPLE PER_CASE POOL OUT.json"""
import json, multiprocessing, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..')]
import ss_cases
import sentinel_prover as sp
from phi import phi

n, a = 14, 5
L1, cs = ss_cases.cases(n, a)


def children(case):
    L2, X = cs[case]
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    return L2, sp._fc.canonical_layers(n, nonred, a, auts)


def task(item):
    case, k, exc = item
    L2, allL = children(case)
    return case, k, exc, phi(n, [list(L1), list(L2), list(allL[k])])[0]


def main():
    ncases, per, pool, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', 'exceptional_census_14_5.jsonl'))]
    rng = random.Random(5)
    withexc = [r for r in rows if r['exceptional']]
    items = []
    for r in rng.sample(withexc, min(ncases, len(withexc))):
        for k in rng.sample(r['exceptional'], min(per, len(r['exceptional']))):
            items.append((r['case'], k, True))
        exc = set(r['exceptional'])
        others = [k for k in range(r['children']) if k not in exc]
        for k in rng.sample(others, min(per, len(others))):
            items.append((r['case'], k, False))
    with multiprocessing.get_context('fork').Pool(pool) as P:
        res = P.map(task, items, chunksize=4)
    json.dump(res, open(out, 'w'))
    for flag in (True, False):
        v = sorted(x[3] for x in res if x[2] == flag)
        print(f'{"exceptional" if flag else "other"} children: {len(v)}; Phi_3 min {v[0]}, median {v[len(v)//2]}, max {v[-1]}')


if __name__ == '__main__':
    main()
