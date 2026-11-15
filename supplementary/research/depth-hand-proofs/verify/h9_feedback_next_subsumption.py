#!/usr/bin/env python3
"""Look for two-layer output-set containments from hand-closed H9 classes."""
import itertools
from h9_feedback_commute import FIRST, classes
from h9_feedback_commute_proof import OLD_HAND, CASES
from netlib import run


def image(second):
    return {sum(value << i for i, value in enumerate(run((FIRST, second), x)))
            for x in itertools.product((0, 1), repeat=9)}


def profile(states):
    levels = [sum(x.bit_count() == k for x in states) for k in range(10)]
    columns = [[sum(x.bit_count() == k and x >> i & 1 for x in states) for k in range(10)]
               for i in range(9)]
    return levels, columns


def containment(small, large):
    lp, cp = profile(small)
    lq, cq = profile(large)
    if any(a > b for a, b in zip(lp, lq)):
        return None, 0
    candidates = [[j for j in range(9) if all(cp[i][k] <= cq[j][k] and lp[k] - cp[i][k] <= lq[k] - cq[j][k]
                                            for k in range(10))] for i in range(9)]
    order = sorted(range(9), key=lambda i: len(candidates[i]))
    current = [-1] * 9
    tried = 0

    def rec(index, used):
        nonlocal tried
        if index == 9:
            tried += 1
            if all(sum((x >> i & 1) << current[i] for i in range(9)) in large for x in small):
                return tuple(current)
            return None
        i = order[index]
        for j in candidates[i]:
            if j not in used:
                current[i] = j
                found = rec(index + 1, used | {j})
                if found is not None:
                    return found
        return None
    return rec(0, set()), tried


if __name__ == '__main__':
    known = OLD_HAND | {s for s, _ in CASES} | {((0, 2), (1, 4), (3, b)) for b in (5, 6)}
    entries = [(label, second, image(second)) for label, second in classes()]
    for label, second, target in entries:
        if second in known:
            continue
        for source_label, source, states in entries:
            if source not in known:
                continue
            for dual in (False, True):
                candidate = {511 ^ x for x in states} if dual else states
                mapping, tried = containment(candidate, target)
                if mapping is not None:
                    print('FOUND', label, '<-', source_label, 'dual', dual, 'mapping', mapping, 'tried', tried, flush=True)
