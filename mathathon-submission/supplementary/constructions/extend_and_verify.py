"""Build 256/512 from the certified 128 network; exhaustively check each merge.

The final merge receives two sorted binary halves. Checking every pair of zero
counts is exhaustive on that domain, so composition with certified half-sorters
proves correctness. This is a new replay, not the historical random-input run.
"""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent

def odd_even_merge(wires):
    if len(wires) == 2:
        return [[tuple(wires)]]
    even = odd_even_merge(wires[::2])
    odd = odd_even_merge(wires[1::2])
    return [a + b for a, b in zip(even, odd)] + [
        [(wires[i], wires[i + 1]) for i in range(1, len(wires) - 1, 2)]
    ]

for n, expected_depth, expected_size in [(256, 34, 3775), (512, 43, 9599)]:
    half = n // 2
    small = json.loads((ROOT / f"net_{half}.json").read_text())["layers"]
    parallel = [layer + [[a + half, b + half] for a, b in layer] for layer in small]
    merger = odd_even_merge(list(range(n)))
    layers = parallel + merger
    assert len(layers) == expected_depth
    assert sum(map(len, layers)) == expected_size
    for layer in layers:
        touched = [w for pair in layer for w in pair]
        assert len(touched) == len(set(touched))
        assert all(0 <= a < b < n for a, b in layer)
    counts = np.arange(half + 1)
    left = np.repeat(counts, half + 1)
    right = np.tile(counts, half + 1)
    X = np.empty(((half + 1) ** 2, n), dtype=np.uint8)
    X[:, :half] = np.arange(half)[None, :] >= left[:, None]
    X[:, half:] = np.arange(half)[None, :] >= right[:, None]
    for layer in merger:
        for a, b in layer:
            u, v = X[:, a].copy(), X[:, b].copy()
            X[:, a], X[:, b] = u & v, u | v
    assert (X[:, :-1] <= X[:, 1:]).all()
    (ROOT / f"net_{n}.json").write_text(json.dumps({"n": n, "depth": len(layers), "layers": layers}))
    print(f"n={n} depth={len(layers)} size={expected_size}: CERTIFIED by composition; all {(half+1)**2} sorted-half inputs checked")
