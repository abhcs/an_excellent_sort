"""The bundle's T3 ("adding comparators to the layers of a sorting network keeps it sorting") is false,
and the monotonicity used in its proof fails.  Only the first layer (prepending) and the end (appending)
are safe places to add comparators."""
import itertools
from netlib import run, sorts


def failing_inputs(layers, n):
    return [v for v in itertools.product((0, 1), repeat=n) if run(layers, v) != sorted(v)]


small = [[(1, 2)], [], [(0, 2)], [(0, 1)]]
small_plus = [[(1, 2)], [(0, 1)], [(0, 2)], [(0, 1)]]
assert sorts(small, 3) and not sorts(small_plus, 3)
v = failing_inputs(small_plus, 3)[0]
print(f'n=3: {small} sorts; with (0,1) in layer 2 it maps {v} to {run(small_plus, v)}')

opt = [[(0, 2), (1, 3)], [(1, 4)], [(0, 1), (3, 4)], [(1, 4), (2, 3)], [(1, 2), (3, 4)]]
opt_plus = [list(L) for L in opt]
opt_plus[1] = [(1, 4), (2, 3)]
assert sorts(opt, 5) and not sorts(opt_plus, 5)
v = failing_inputs(opt_plus, 5)[0]
print(f'n=5, depth 5 (optimal): {opt} sorts; with (2,3) in layer 2 it maps {v} to {run(opt_plus, v)}')


def prefix(x):
    return list(itertools.accumulate(x))


x, y = [0, 1, 0], [1, 0, 0]
cx, cy = run([[(0, 2)]], x), run([[(0, 2)]], y)
assert all(a <= b for a, b in zip(prefix(x), prefix(y)))
assert not all(a <= b for a, b in zip(prefix(cx), prefix(cy)))
print(f'monotonicity fails: prefix sums {prefix(x)} <= {prefix(y)}, but after (0,2) {prefix(cx)} vs {prefix(cy)}')

# How often does a random insertion into a middle layer break a sorting network? (fixed seed)
import random
from mechanism import batcher, relabel_untangle
rng = random.Random(7)
tried = broke = 0
for n in range(3, 11):
    for _ in range(300):
        net = relabel_untangle(batcher(n), n, rng)
        if len(net) < 3:
            continue
        t = rng.randrange(1, len(net) - 1)              # a middle layer: not the first, not the last
        used = {c for e in net[t] for c in e}
        idle = [c for c in range(n) if c not in used]
        if len(idle) < 2:
            continue
        a, b = sorted(rng.sample(idle, 2))
        new = [list(L) for L in net]
        new[t].append((a, b))
        tried += 1
        broke += not sorts(new, n)
print(f'random insertions into a middle layer of relabelled Batcher networks (n=3..10): '
      f'{broke} of {tried} broke the network')
