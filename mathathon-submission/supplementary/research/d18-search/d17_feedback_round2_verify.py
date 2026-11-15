#!/usr/bin/env python3
"""Local hand-lemma audits and a bounded, incomplete row-core screen.

No SAT, solver imports, or second-matching search.  The optional feedback
is not a premise of the accompanying hand proofs.
"""
import collections
import hashlib
import itertools
import json
from pathlib import Path
import signal
import time

ROOT = Path(__file__).parent
INPUT = ROOT / 'results/d17-feedback-fourteen-hand606-states.json'
G = ((3, 4), (4, 5), (5, 6), (2, 4))
ASIGN = {2: 1, 3: -1, 4: -1, 5: 1, 6: 1}
CRITICAL = (7, 10)


def matchings(xs, perfect=False):
    if not xs:
        yield ()
        return
    a, *rest = xs
    if not perfect:
        yield from matchings(rest)
    for j, b in enumerate(rest):
        for tail in matchings(rest[:j] + rest[j+1:], perfect):
            yield ((a, b),) + tail


def edge(a, b):
    return tuple(sorted((a, b)))


def compatible(edges):
    partner = {}
    for a, b in edges:
        if a in partner and partner[a] != b or b in partner and partner[b] != a:
            return False
        partner[a], partner[b] = b, a
    return True


def step(state, matching):
    result = list(state)
    for a, b in matching:
        result[a], result[b] = sorted((result[a], result[b]))
    return result


def singleton(v, sign, matching):
    for a, b in matching:
        if v in (a, b):
            return min(a, b) if sign < 0 else max(a, b)
    return v


def folded(matching):
    image = {v: singleton(v, sign, matching) for v, sign in ASIGN.items()}
    return {edge(image[a], image[b]) for a, b in G if edge(a, b) not in matching}


def cores(u, v):
    result = [((u, v), (11, 9), (10, 12))]
    result += [((8, 9), (12, 13)) + p
               for p in matchings([u, v, 11, 10], perfect=True)]
    return result


def critical_feedback(states):
    counts = collections.Counter()
    examples = {}
    for tail in matchings([v for v in range(14) if v not in CRITICAL], perfect=True):
        matching = (CRITICAL,) + tail
        cross = sum((a in ASIGN) != (b in ASIGN) and a >= 2 and b >= 2
                    and (a >= 7 or b >= 7) for a, b in matching)
        requirements, full = [], []
        for row, (u, v) in enumerate(G):
            family = states[5*row:5*row+5]
            if any(sum(s[a] == s[b] == 0 for a, b in matching) >= 4 for s in family):
                continue
            full.append(row)
            permutation = list(range(14))
            for a, b in tail:
                if not all(s[a] <= s[b] for s in family):
                    assert all(s[a] >= s[b] for s in family)
                    permutation[a], permutation[b] = permutation[b], permutation[a]
            # Audit the exact row routing, including equal-sign collision correction.
            for state in family:
                canonical = step(state, [CRITICAL])
                predicted = [None] * 14
                for a, value in enumerate(canonical):
                    predicted[permutation[a]] = value
                assert predicted == step(state, matching)
            requirements.append([
                frozenset(edge(permutation[a], permutation[b]) for a, b in core)
                for core in cores(u, v)])
        possible = {frozenset()}
        for options in requirements:
            possible = {left | right for left in possible for right in options
                        if compatible(left | right)}
            if not possible:
                break
        key = (cross, len(full), bool(possible))
        counts[key] += 1
        if possible:
            examples.setdefault(str(key), dict(first=matching, full_rows=full,
                                compatible_row_core=sorted(next(iter(possible)))))
    assert sum(counts.values()) == 10395
    assert not any(c == 0 and possible for c, full, possible in counts)
    assert not any(full >= 3 and possible for c, full, possible in counts)
    return dict(scope='Incomplete full-row-core screen; no second-matching search',
                first_matchings=10395,
                excluded=sum(v for (c, f, p), v in counts.items() if not p),
                undecided=sum(v for (c, f, p), v in counts.items() if p),
                counts=[dict(cross=c, full_rows=f, compatible_core=p, count=v)
                        for (c, f, p), v in sorted(counts.items())],
                undecided_examples=examples)


def main():
    started = time.monotonic()
    signal.signal(signal.SIGALRM, lambda *unused: (_ for _ in ()).throw(TimeoutError('90s wall bound')))
    signal.alarm(90)
    states = json.loads(INPUT.read_text())['states']
    comparable = {(a, b) for a, b in itertools.combinations(range(14), 2)
                  if all(s[a] <= s[b] for s in states) or all(s[a] >= s[b] for s in states)}
    incomparable = set(itertools.combinations(range(14), 2)) - comparable
    assert len(incomparable) == 23
    expected4 = {tuple(sorted((2, x, 7, y))) for x in (5, 6) for y in (10, 12, 13)}
    actual4 = {I for I in itertools.combinations(range(14), 4)
               if all(p in incomparable for p in itertools.combinations(I, 2))}
    assert actual4 == expected4
    assert not any(all(p in incomparable for p in itertools.combinations(I, 2))
                   for I in itertools.combinations(range(14), 5))
    for a, b in comparable:
        swap = not all(s[a] <= s[b] for s in states)
        for state in states:
            predicted = list(state)
            if swap:
                predicted[a], predicted[b] = predicted[b], predicted[a]
            assert predicted == step(state, [(a, b)])
    for I in actual4:
        assert all(sum(s[v] != 0 for v in I) <= 2 for s in states)

    local_A = list(matchings(list(ASIGN)))
    assert len(local_A) == 26
    # External partners keep distinct images; only same-sign internal A edges merge.
    for M in local_A:
        M = tuple(edge(a, b) for a, b in M)
        assert not compatible(folded(M)), M

    incident = 0
    for first in cores(2, 3):
        for second in cores(2, 4):
            assert not compatible(set(map(lambda x: edge(*x), first)) |
                                  set(map(lambda x: edge(*x), second)))
            incident += 1
    assert incident == 16
    # Each alternative is individually valid; incompatibility comes from sharing one A vertex.
    B = [{11,8,9}, {11,9,10}, {11,10,12}, {13,10,12}, {11,9,10}]
    for core in cores(2, 3):
        assert compatible(core)
        assert all(sum(a in S | {2,3} and b in S | {2,3} for a,b in core) >= 2 for S in B)

    four_idle = 0
    for I in sorted(actual4):
        for M in matchings([v for v in range(14) if v not in I], perfect=True):
            assert len(M) == 5 and CRITICAL not in M
            assert all(sum(s[a] == s[b] == 0 for a,b in M) < 4 for s in states)
            assert not compatible(folded(M))
            for row,(u,v) in enumerate(G):
                if edge(u,v) in M:
                    continue
                images = {singleton(u,ASIGN[u],M), singleton(v,ASIGN[v],M)}
                assert len(images) == 2
                for state in states[5*row:5*row+5]:
                    transported = step(state,M)
                    assert all(transported[x] != 0 for x in images)
            four_idle += 1
    assert four_idle == 5670
    feedback = critical_feedback(states)
    result = dict(status='VERIFIED', sat_used=False, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  states_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),
                  incomparable_pairs=sorted(incomparable), four_idle_antichains=sorted(actual4),
                  local_A_matchings=26, incident_core_combinations=16,
                  four_idle_first_matchings=four_idle, critical_feedback=feedback,
                  complete_case606_hand_proof=False, elapsed_seconds=round(time.monotonic()-started,4))
    signal.alarm(0)
    target = ROOT / 'results/d17-feedback-round2-verification.json'
    target.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('critical_feedback','incomparable_pairs')},indent=2))
    print(json.dumps({k:v for k,v in feedback.items() if k not in ('counts','undecided_examples')},indent=2))


if __name__ == '__main__':
    main()
