"""d17_tokrate.py EXCONLY.json IDX K SEED: the cost of the exact token search (tokcore2.c, TOK_MATCH=1) on one
exceptional-only class of the D(17) descent (efficient-prefixes.md section 10).
  1. Count the class representative's fourth layers: matchings of the comparators that swap some reachable
     state after layer 3, the empty layer included. tokcore2 tries every one of them, because on 12 channels
     the cone bound 2^(D-t) cannot cut before layer 6 at depth 9.
  2. Run tokcore2 on the class with a cap of 2,000,000 nodes (the probe first quoted in section 10). Those are
     the first fourth layers in search order, which are cheap, so this run alone underestimates the cost.
  3. Search K uniformly random fourth layers (seed SEED) to the end, each appended to the prefix. The mean CPU
     time per fourth layer times their number estimates the complete search of the class.
Runs JOBS (env, default 3) searches at a time; each one's CPU time is measured by /usr/bin/time. Keep JOBS within
the idle performance cores: on an M4 (4 performance, 6 efficiency cores) eight at once inflate each run's CPU time,
the capped search's from 66 s to 109 s. That run does the same work every time, so it calibrates the others."""
import json, os, random, re, statistics, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

d = json.load(open(sys.argv[1])); idx = int(sys.argv[2]); K = int(sys.argv[3]); random.seed(int(sys.argv[4]))
n, D = d['n'], d['depth']; pre = [[tuple(p) for p in L] for L in d['reps'][idx]]
TOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tokcore2')

S = set()
for x in range(1 << n):
    for L in pre:
        for a, b in L:
            if (x >> a) & 1 and not (x >> b) & 1:
                x ^= (1 << a) | (1 << b)
    S.add(x)
E = [(i, j) for i in range(n) for j in range(i + 1, n) if any((u >> i) & 1 and not (u >> j) & 1 for u in S)]
nbr = {c: [j for i, j in E if i == c] for c in range(n)}


@lru_cache(None)
def count(free):                     # matchings of E on the channel set 'free', the empty one included
    if not free:
        return 1
    c = (free & -free).bit_length() - 1; rest = free & ~(1 << c)
    return count(rest) + sum(count(rest & ~(1 << j)) for j in nbr[c] if (rest >> j) & 1)


def sample(free):                    # a uniformly random matching of E on 'free'
    L = []
    while free:
        c = (free & -free).bit_length() - 1; rest = free & ~(1 << c)
        opts = [(count(rest), None)] + [(count(rest & ~(1 << j)), j) for j in nbr[c] if (rest >> j) & 1]
        r = random.randrange(sum(w for w, _ in opts))
        for w, j in opts:
            if r < w:
                break
            r -= w
        if j is None:
            free = rest
        else:
            L.append((c, j)); free = rest & ~(1 << j)
    return L


def tok(job):                        # one tokcore2 run (layers, cap): its output line and its CPU seconds
    layers, cap = job
    inp = f'{n} {D} 1\n{len(layers)}\n' + '\n'.join(' '.join([str(len(L))] + [f'{a} {b}' for a, b in L])
                                                     for L in layers) + '\n'
    p = subprocess.run(['/usr/bin/time', '-p', TOK, str(cap)], input=inp, capture_output=True, text=True,
                       check=True, env=dict(os.environ, TOK_MATCH='1'))
    cpu = sum(float(v) for v in re.findall(r'^(?:user|sys)\s+([\d.]+)', p.stderr, re.M))
    return p.stdout.strip(), cpu


F = count((1 << n) - 1)
L4s = [sample((1 << n) - 1) for _ in range(K)]
with ThreadPoolExecutor(int(os.environ.get('JOBS', '3'))) as ex:
    res = list(ex.map(tok, [(pre, 2000000)] + [(pre + [L4], 0) for L4 in L4s]))
print(f'class {idx} of {sys.argv[1]} (n = {n}, depth {D}): {pre}')
print(f'{len(S)} reachable states after layer 3, {len(E)} non-redundant comparators, {F} fourth layers')
out, t = res[0]
f = out.split()
print(f'capped search, 2,000,000 nodes: "{out}" in {t:.1f} s CPU')
print(f'  {f[1]} fourth layers reached (the first in search order), {int(f[2]) / int(f[1]):,.0f} fifth layers each')
times, outcomes = [], {}
for k, (L4, (out, t)) in enumerate(zip(L4s, res[1:])):
    r = out.split()[1 + D - 4]
    times.append(t); outcomes[r] = outcomes.get(r, 0) + 1
    print(f'fourth layer {k}: {L4}: "{out}" {t:.2f} s')
m, se = statistics.mean(times), statistics.stdev(times) / len(times) ** 0.5
print(f'{K} random fourth layers searched to the end: outcomes {outcomes}; CPU s per fourth layer: mean {m:.2f}, '
      f'median {statistics.median(times):.2f}, min {min(times):.2f}, max {max(times):.2f} (standard error {se:.2f})')
print(f'estimated complete search of the class: {F} x {m:.2f} s = {F * m / 3600:.0f} CPU-hours '
      f'(mean +- 2 standard errors: {F * (m - 2 * se) / 3600:.0f}-{F * (m + 2 * se) / 3600:.0f})')
