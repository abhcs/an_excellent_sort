"""End-to-end cross-check of the sentinel route (efficient-prefixes.md section 9), with no canonical forms:
for random 11-channel class representatives, build the untangled residual 10-channel prefixes of their
good-track sentinels (as sentinel_prover.residual2, but keeping empty layers so the residual keeps 3 layers),
and run the exact token search (tokcore2, depth 8) on them until one is refuted.
usage: resid_check.py reps_11_4.json COUNT SEED"""
import json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def residual_keep(n, layers, S):
    content = [None] * n
    real = [c for c in range(n) if c not in S]
    for c in range(n):
        content[c] = S[c] if c in S else real.index(c)
    gen = []
    for L in layers:
        gl = []
        for i, j in L:
            a, b = content[i], content[j]
            sa, sb = isinstance(a, str), isinstance(b, str)
            if sa and sb:
                if a == '+' and b == '-':
                    content[i], content[j] = b, a
            elif sa:
                if a == '+':
                    content[i], content[j] = b, a
            elif sb:
                if b == '-':
                    content[i], content[j] = b, a
            else:
                gl.append((a, b))
        gen.append(gl)                                   # empty layers kept
    m = list(range(len(real))); std = []
    for gl in gen:
        sl = []
        for a, b in gl:
            a2, b2 = m[a], m[b]
            if a2 < b2:
                sl.append((a2, b2))
            else:
                sl.append((b2, a2)); m[a], m[b] = b2, a2
        std.append(sl)
    return len(real), std


def good(layers, s, plus, a):
    pos = s
    for l, L in enumerate(layers):
        met = False
        for i, j in L:
            if pos in (i, j):
                met = True; pos = j if plus else i; break
        if not met and (l == 0 or len(L) == a):
            return False
    return True


def tok(n, pre):
    lines = [f'{n} 8 1', str(len(pre))] + [' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]) for L in pre]
    r = subprocess.run([os.path.join(HERE, 'tokcore2'), '0'], input='\n'.join(lines) + '\n', capture_output=True,
                       text=True, env=dict(os.environ, TOK_MATCH='1'))
    row = r.stdout.split()
    k = row.index('pruned') if 'pruned' in row else len(row)
    return row[k - 1]


d = json.load(open(sys.argv[1])); cnt, seed = int(sys.argv[2]), int(sys.argv[3])
random.seed(seed); sample = random.sample(range(len(d['reps'])), cnt)
settled = 0; searches = 0
for i in sample:
    pre = d['reps'][i]; ok = False
    for s in range(11):
        for plus in (1, 0):
            if not good(pre, s, plus, 4):
                continue
            r, std = residual_keep(11, pre, {s: '+' if plus else '-'})
            assert r == 10 and len(std) == 3 and all(len(L) <= 3 for L in std), (pre, s, plus, std)
            searches += 1
            if tok(10, std) == 'none':
                ok = True; break
        if ok:
            break
    settled += ok
    print(i, 'settled' if ok else 'NOT settled by its own residuals', flush=True)
print(f'{settled} of {cnt} sampled class representatives settled by an untangled residual ({searches} residual searches)')
