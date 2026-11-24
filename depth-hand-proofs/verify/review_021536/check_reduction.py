"""Mechanize the reduction note's case split over ALL matchings M on 9 wires."""
import itertools
from collections import Counter
from common import *

nf2, sw2 = order_info((L1, L2))
print('never-fire after L2:', sorted(nf2))
print('always-swap after L2:', sorted(sw2))
claimed = {(0, 2), (0, 5), (0, 6), (1, 5), (3, 6), (4, 5)}
assert claimed <= nf2, claimed - nf2
print('extra never-fire not listed in note:', sorted(nf2 - claimed))

# H7 restrictions of section 1
for pl, exp_sent in (({0: 1, 2: 1}, {5, 6}), ({0: 1, 2: -1}, {0, 5})):
    tr = trace((L1, L2), pl)
    numeric_check((L1, L2), pl, tr)
    sent = {w for w in range(9) if tr['sign'][w]}
    ev = tr['events']
    slots = [set(e[1:]) for e in ev]
    print('restriction', pl, 'sentinels after L2', sent, 'events', ev)
    assert sent == exp_sent and len(ev) == 2 and not (slots[0] & slots[1])

FORMS = ['12 34 56 78', '12 34 78', '12 37 48', '12 37 48 56', '13 24 56 78', '13 24 78',
         '13 27 48', '13 27 48 56', '14 23 56 78', '14 23 78', '14 27 38', '14 27 38 56',
         '17 23 48', '17 23 48 56', '17 24 38', '17 24 38 56', '17 28 34', '17 28 34 56']
F = {edges(s) for s in FORMS}
assert len(F) == 18

A = {0: -1, 2: 1, 4: 1}
B = {0: -1, 2: 1, 4: -1}
Cc = {0: -1, 1: -1, 2: 1}
CROSS = {0: -1, 1: -1, 2: 1, 4: -1}
PAIR = {0: -1, 2: 1}


def exchange_ok(M, R1, R2):
    """Valid six-real exchange contradiction for restrictions R1,R2 with L3=M."""
    res = []
    for R in (R1, R2):
        tr = trace((L1, L2, M), R)
        ev = tr['events']
        if len(ev) < 2:
            res.append(('lt2', tr))  # already a contradiction by itself
            continue
        if len(ev) > 2:
            return False
        if set(ev[0][1:]) & set(ev[1][1:]):
            return False
        res.append(('two', tr))
    if any(k == 'lt2' for k, _ in res):
        return True
    s1, s2 = set(res[0][1]['real']), set(res[1][1]['real'])
    return len(s1) == 6 and len(s2) == 6 and len(s1 & s2) == 5


def d5_ok(M, R):
    tr = trace((L1, L2, M), R)
    return len(tr['real']) == 5 and len(tr['events']) == 0


def h7_ok(M, R):
    tr = trace((L1, L2, M), R)
    return len(tr['real']) == 7 and schedulable(tr['events'], 2, 2)


stat = Counter()
survivors = set()
for M in matchings(9):
    Ms = tuple(e for e in M if e not in nf2)
    a56 = sum(1 for e in Ms if not set(e) & {5, 6})
    a05 = sum(1 for e in Ms if not set(e) & {0, 5})
    if a56 < 3 or a05 < 3:
        stat['H7 pair condition'] += 1
        continue
    if Ms in F or swap78(Ms) in F:
        stat['listed (up to 7<->8)'] += 1
        survivors.add(min(Ms, swap78(Ms)))
        continue
    used = {v for e in Ms for v in e}
    assert len(Ms) == 4 and set(range(9)) - used == {5}, Ms
    # try each argument from section 2/3 and require at least one to be valid
    ways = []
    if exchange_ok(Ms, A, B):
        ways.append('AB')
    if exchange_ok(Ms, A, Cc):
        ways.append('AC')
    if d5_ok(Ms, CROSS):
        ways.append('cross')
    if h7_ok(Ms, PAIR):
        ways.append('pair')
    assert ways, Ms
    stat['idle5:' + '+'.join(ways)] += 1

print(stat)
print('distinct surviving representatives:', len(survivors))
assert {min(f, swap78(f)) for f in F} == survivors
# also: representatives listed are each the 7<->8 class reps, no class listed twice
assert len({min(f, swap78(f)) for f in F}) == 18
print('REDUCTION OK')
