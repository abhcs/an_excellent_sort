"""Time full SAT certificates (CNF generation, CaDiCaL with DRAT proof, drat-trim) on random
exceptional root children of the descent levels, one process per child.
usage: N_PER_LEVEL POOL [SEED]"""
import json, multiprocessing, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..')]
import ss_cases
import sentinel_prover as sp
import satcert

LEVELS = [(12, 3), (13, 4), (14, 5)]


def task(item):
    n, a, case, k = item
    L1, cs = ss_cases.cases(n, a)
    L2, X = cs[case]
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, a, auts)
    rec = satcert.certify(n, (L1, L2, allL[k]), 6, ())
    rec.update(n=n, a=a, case=case, k=k)
    return rec


def main():
    per, pool = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    items = []
    for n, a in LEVELS:
        rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', f'exceptional_census_{n}_{a}.jsonl'))]
        pairs = [(r['case'], k) for r in rows for k in r['exceptional']]
        items += [(n, a, c, k) for c, k in rng.sample(pairs, per)]
    t0 = time.time()
    with multiprocessing.get_context('fork').Pool(pool) as P:
        for rec in P.imap_unordered(task, items):
            print(json.dumps({k: rec.get(k) for k in ('n', 'case', 'k', 'result', 'drat', 'vars', 'clauses', 'gen_s',
                                                      'solve_s', 'check_s', 'proof_bytes', 'tool_maxrss_mb')}), flush=True)
    print(f'done in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
