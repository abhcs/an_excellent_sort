"""Window sums of token sets after 3-layer prefixes on 14 channels (tokpot.c): S14 exceptional prefixes
against feasible prefixes (two-infinity restrictions of the depth-9 16-sorter, hand/g16_d9_network.json).
usage: tokpot_run.py WMASK [more masks]"""
import json, os, subprocess, sys, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..')]
from phi import residual_network


def run(n, D, prefixes, W):
    lines = [f'{n} {D} {len(prefixes)}']
    for pre in prefixes:
        lines.append(str(len(pre)))
        for L in pre:
            lines.append(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]))
    out = subprocess.run([os.path.join(HERE, 'tokpot'), W], input='\n'.join(lines) + '\n', capture_output=True, text=True).stdout
    return [list(map(int, l.split())) for l in out.split('\n') if l.strip()]


def feasible14():
    g16 = json.load(open(os.path.join(HERE, 'g16_d9_network.json')))
    out, seen = [], set()
    for a, b in itertools.combinations(range(16), 2):
        for sa, sb in itertools.product('+-', repeat=2):
            r, R = residual_network(16, g16, {a: sa, b: sb})
            if r != 14:
                continue
            pre = tuple(tuple(map(tuple, L)) for L in R[:3])
            if pre not in seen:
                seen.add(pre)
                out.append([list(L) for L in pre])
    return out


if __name__ == "__main__":
    c0 = json.load(open(os.path.join(HERE, 'case0_exceptional.json')))
    sparse = [[c0['L1'], c0['L2'], L3] for L3 in c0['L3s']]
    feas = feasible14()
    print(f'{len(sparse)} S14 case-0 exceptional prefixes; {len(feas)} feasible 14-channel prefixes, layer sizes',
          sorted(collections.Counter(tuple(len(L) for L in p) for p in feas).items()))
    for W in sys.argv[1:]:
        m = int(W, 16)
        ks = [k for k in range(14) if m >> k & 1]
        for name, P in (('sparse', sparse), ('feasible', feas)):
            rows = run(14, 9, P, W)
            S = sorted(r[1] for r in rows)
            M = sorted(r[2] for r in rows)
            drop = sorted(r[1] - r[2] for r in rows)
            print(f'W={ks}: {name:8s} window sum after layer 3: {S[0]}..{S[-1]}; least after one more layer: {M[0]}..{M[-1]}; '
                  f'largest one-layer drop {drop[0]}..{drop[-1]}')
        rows = run(14, 9, sparse[:1], W)
        print('   e.g. sparse |T_3(k)| per output:', rows[0][3:])
        rows = run(14, 9, feas[:1], W)
        print('   e.g. feasible |T_3(k)| per output:', rows[0][3:])
