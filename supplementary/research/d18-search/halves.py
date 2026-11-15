#!/usr/bin/env python3
"""halves.py -- self-dual 18-channel prefixes made of a 9-channel prefix Q on channels 0..8 and its
mirror image on 9..17.  Q is found by a beam search (one comparator at a time, fewest outputs)."""
import json, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from netsat import apply_layers, prefix_images, is_self_dual, mirror

def beam9(m, depth, B):
    full = frozenset(range(1 << m))
    states = [([], full)]
    for _ in range(depth):
        cur = [(L + [[]], S) for L, S in states]
        for step in range(m // 2):
            cand = {}
            for L, S in cur:
                cand.setdefault((frozenset(S),), (L, S))
                used = {k for c in L[-1] for k in c}
                for i in range(m):
                    for j in range(i + 1, m):
                        if i in used or j in used: continue
                        T = frozenset(apply_layers([[(i, j)]], x) for x in S)
                        if T == S: continue
                        key = (T,)
                        if key not in cand:
                            cand[key] = (L[:-1] + [sorted(L[-1] + [(i, j)])], T)
            cur = sorted(cand.values(), key=lambda t: len(t[1]))[:B]
        states = cur
    return states

if __name__ == '__main__':
    depth, B, keep = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    st = beam9(9, depth, B)
    print('9-channel', depth, 'layer prefixes, output sizes:', [len(S) for _, S in st[:20]])
    with open(f'prefixes/halves_d{depth}.jsonl', 'w') as f:
        for L, S in st[:keep]:
            L = [l for l in L if l]
            P = [sorted([tuple(c) for c in l] + [mirror(18, c) for c in l]) for l in L]
            assert is_self_dual(18, P)
            out = len(prefix_images(18, P))
            f.write(json.dumps({'n': 18, 'outputs': out, 'q_outputs': len(S), 'layers': P}) + '\n')
            print(len(S), out, L)
