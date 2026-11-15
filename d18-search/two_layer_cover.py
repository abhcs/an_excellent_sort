#!/usr/bin/env python3
"""Complete two-layer covers and the exact family of half-blind restrictions.

Coverage: Bundala et al., arXiv:1412.5302, Theorem 6 / Corollary 5.
Components are alternating paths/cycles; 1 and 2 mark the min/max ends
of first-layer pairs, and 0 marks the optional free first-layer channel.
We quotient by component reversal/rotation and by global reflection.
We do NOT impose reflection symmetry on a network's completion.

The half-blind family calculation itself does not assume saturation and
does not use the paper's coverage theorem. See structural-frontier.md.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path


def canonical_component(kind, word):
    if kind == 'H':
        return kind, word
    if kind == 'S':
        return kind, min(word, word[::-1])
    assert kind == 'C' and len(word) % 2 == 0
    return kind, min(s[i:] + s[:i] for s in (word, word[::-1])
                     for i in range(0, len(word), 2))


def reflection(sentence):
    swap = str.maketrans('12', '21')
    return tuple(sorted(canonical_component(k, w.translate(swap)) for k, w in sentence))


@lru_cache(None)
def components(limit):
    out = {('H', '0')}
    for m in range(1, limit // 2 + 1):
        for blocks in itertools.product(('12', '21'), repeat=m):
            word = ''.join(blocks)
            out.add(canonical_component('S', word))
            out.add(canonical_component('C', word))
            if len(word) + 1 <= limit:
                out.add(('H', '0' + word))
    return tuple(sorted(out))


def saturated(sentence):
    """The syntactic saturation criterion (paper Corollary 3)."""
    ends = set()
    special = 0
    for kind, word in sentence:
        if kind == 'C':
            if len(word) == 2:  # immediate repetition of a first-layer edge
                return False
        elif word in ('0', '12'):
            special += 1
        else:
            if kind == 'S' and (len(word) == 4 or word[0] != word[-1]):
                return False
            ends.add(word[-1])
    if special:
        return special == 1 and sum(k != 'C' for k, _ in sentence) == 1
    return len(ends) <= 1


@lru_cache(None)
def sentences(n, saturation=True, reflect=True):
    cs = components(n)
    out = []

    def rec(start, left, head, acc):
        if left == 0:
            sentence = tuple(acc)
            if saturation and not saturated(sentence):
                return
            if reflect and sentence > reflection(sentence):
                return
            out.append(sentence)
            return
        for i in range(start, len(cs)):
            kind, word = cs[i]
            if len(word) > left or (head and kind == 'H'):
                continue
            rec(i, left - len(word), head or kind == 'H', acc + [cs[i]])

    rec(0, n, False, [])
    return tuple(out)


def network(sentence):
    first, second = [], []
    offset = 0
    for kind, word in sentence:
        # Assign one adjacent physical first-layer pair to each 12/21 block.
        m = len(word) // 2
        path = []
        body = word
        if kind == 'H':
            path.append(offset + 2 * m)
            body = word[1:]
        for i in range(m):
            a, b = offset + 2 * i, offset + 2 * i + 1
            first.append((a, b))
            path.extend([a, b] if body[2 * i:2 * i + 2] == '12' else [b, a])
        start = 0 if kind == 'H' else 1
        second.extend(tuple(sorted(path[i:i + 2])) for i in range(start, len(path) - 1, 2))
        if kind == 'C':
            second.append(tuple(sorted((path[-1], path[0]))))
        offset += len(word)
    return [sorted(first), sorted(second)]


def signature(n, first, second):
    """Independent graph-to-word conversion, also used on brute-force matchings."""
    role = [0] * n
    adj = [[] for _ in range(n)]
    for t, layer in enumerate((first, second)):
        for a, b in layer:
            if t == 0:
                role[a], role[b] = 1, 2
            adj[a].append((b, t))
            adj[b].append((a, t))
    unseen = set(range(n))
    result = []
    while unseen:
        root = min(unseen)
        todo, comp = [root], set()
        while todo:
            a = todo.pop()
            if a in comp:
                continue
            comp.add(a)
            todo.extend(b for b, _ in adj[a])
        unseen -= comp
        free = [a for a in comp if role[a] == 0]
        ends = [a for a in comp if len(adj[a]) < 2]
        kind = 'H' if free else ('S' if ends else 'C')
        a = free[0] if free else (min(ends) if ends else min(comp))
        start = a
        previous_type = 0 if kind == 'H' else 1
        word = ''
        while True:
            word += str(role[a])
            edges = [(b, t) for b, t in adj[a] if t != previous_type]
            if not edges:
                break
            b, t = edges[0]
            if b == start:
                break
            a, previous_type = b, t
        assert len(word) == len(comp)
        result.append(canonical_component(kind, word))
    return tuple(sorted(result))


def type_step(values, layer):
    values = list(values)
    for a, b in layer:
        values[a], values[b] = min(values[a], values[b]), max(values[a], values[b])
    return tuple(values)


def half_blind_family(n, prefix):
    """ALL real-position sets after two blind layers, via first-pair choices.

    Exactly floor(n/2) infinities forces one per first-layer pair; its sign
    after the first layer is determined by its endpoint. At most 2^(n/2)
    configurations are visited; arbitrary 3^n placement enumeration is avoided.
    Returns real-set bitmasks with one witness initial placement per mask.
    """
    first, second = prefix
    assert len(first) == n // 2
    out = {}
    for choices in itertools.product((0, 1), repeat=len(first)):
        values = [0] * n
        for (a, b), c in zip(first, choices):
            values[a if c == 0 else b] = -1 if c == 0 else 1
        if any(values[a] == values[b] == 0 for a, b in second):
            continue
        after = type_step(values, second)
        mask = sum(1 << i for i, v in enumerate(after) if v == 0)
        if mask in out:
            # The component theorem says coincident real sets here have the
            # same signed infinity state, not merely the same occupancy.
            assert type_step(out[mask], second) == after
        out.setdefault(mask, tuple(values))
    return out


def frozen_cycle(word):
    assert len(word) % 2 == 0
    return all(word[i] == word[(i + 1) % len(word)] for i in range(1, len(word), 2))


def family_count(sentence):
    count = 1
    for kind, word in sentence:
        if kind == 'S':
            count *= len(word) // 2 + 1
        elif kind == 'C' and not frozen_cycle(word):
            count *= 2
    return count


def local_image_count(kind, word):
    prefix = network(((kind, word),))
    n = len(word)
    outputs = set()
    # Only first-layer images: three states per pair, two per idle channel.
    for pair_states in itertools.product((0, 2, 3), repeat=n // 2):
        base = sum(x << (2 * i) for i, x in enumerate(pair_states))
        for free in range(2 if n % 2 else 1):
            x = base | (free << (n - 1) if n % 2 else 0)
            for a, b in prefix[1]:
                if (x >> a & 1) and not (x >> b & 1):
                    x ^= (1 << a) | (1 << b)
            outputs.add(x)
    return len(outputs)


def image_count(sentence, cache):
    count = 1
    for comp in sentence:
        if comp not in cache:
            cache[comp] = local_image_count(*comp)
        count *= cache[comp]
    return count


def export(n, path):
    cases = sentences(n)
    cache = {}
    records = []
    for sentence in cases:
        prefix = network(sentence)
        assert signature(n, *prefix) == sentence
        family = half_blind_family(n, prefix)
        assert len(family) == family_count(sentence)
        records.append(dict(n=n, layers=prefix, sentence=sentence,
                            outputs=image_count(sentence, cache),
                            half_blind_sets=len(family)))
    records.sort(key=lambda r: (r['outputs'], r['sentence']))
    for i, record in enumerate(records):
        record['case_id'] = f'n{n}-r{i:04d}'
    path.parent.mkdir(parents=True, exist_ok=True)
    text = ''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in records)
    path.write_text(text)
    summary = dict(n=n, cases=len(records), sha256=hashlib.sha256(text.encode()).hexdigest(),
                   half_blind_histogram=dict(sorted(Counter(r['half_blind_sets'] for r in records).items())),
                   min_outputs=min(r['outputs'] for r in records),
                   max_outputs=max(r['outputs'] for r in records),
                   coverage_source='https://arxiv.org/abs/1412.5302',
                   coverage_theorem='Theorem 6 and Corollary 5',
                   completion_symmetry_restricted=False)
    path.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('n', type=int)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if not 3 <= args.n <= 22:
        ap.error('this implementation is intended for 3 <= n <= 22')
    export(args.n, args.out)


if __name__ == '__main__':
    main()
