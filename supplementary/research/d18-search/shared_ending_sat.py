#!/usr/bin/env python3
"""Factor the final two layers through their common intermediate state set.

The earlier layers are encoded per input. Each possible state at the cut
is encoded through the final two layers just once, guarded by its shared
support flag. This is an exact encoding, not a restriction on the prefix.
"""
from capacity_sat import CapacityModel
from netsat import is_sorted, neg, window
from two_layer_envelope import allows


class SharedEndingModel(CapacityModel):
    def __init__(self, n, r, outputs, mode='profiles', solver='cadical195'):
        assert mode != 'none', 'Shared ending needs the support interface.'
        super().__init__(n, r, outputs, mode, solver)
        self.shared_states = 0
        self.forbidden_states = 0
        before = self.nv, self.ncl
        for zeros, group in self.groups.items():
            for pattern, present in group.items():
                if not allows(n, pattern):
                    self.add([-present])
                    self.forbidden_states += 1
                    continue
                if is_sorted(pattern, n):
                    continue
                low, high = window(pattern, n)
                current = {k: bool(pattern >> k & 1) for k in range(low, high + 1)}
                current = self._evolve(current, low, high, r - 2)
                for k in range(low, high + 1):
                    if k <= zeros - 2:
                        self.add([-present, neg(current[k])])
                    elif k >= zeros + 1:
                        self.add([-present, current[k]])
                p, q = current[zeros - 1], current[zeros]
                self.add([-present, p, q])
                self.add([-present, neg(p), neg(q)])
                self.add([-present, neg(p), self.L(zeros - 1)])
                self.shared_states += 1
        self.shared_variables = self.nv - before[0]
        self.shared_clauses = self.ncl - before[1]

    def _evolve(self, current, low, high, t):
        new = {k: self.new_var() for k in range(low, high + 1)}
        for k in range(low, high + 1):
            self.add([neg(current[k]), new[k], self.Down(t, k, high)])
            self.add([current[k], -new[k], self.Up(t, low, k)])
        for (i, j), gate in self.g[t].items():
            if not low <= i < j <= high:
                continue
            oi, oj, ni, nj = current[i], current[j], new[i], new[j]
            self.add([-gate, neg(oi), nj])
            self.add([-gate, oi, oj, -nj])
            self.add([-gate, neg(oi), neg(oj), ni])
            self.add([-gate, oj, -ni])
        return new

    def _pen_units(self, current, low, high, zeros):
        super()._pen_units(current, low, high, zeros)
        bit = lambda k: current.get(k, bool(k >= zeros))
        # At most one stray one to the left, and one stray zero to the right.
        self.add([neg(bit(zeros - 3)), neg(bit(zeros - 2))])
        self.add([bit(zeros + 1), bit(zeros + 2)])

    def add_input(self, x):
        low, high = window(x, self.n)
        assert low < high
        zeros = self.n - x.bit_count()
        current = {k: bool(x >> k & 1) for k in range(low, high + 1)}
        for t in range(self.r - 2):
            current = self._evolve(current, low, high, t)
        self._pen_units(current, low, high, zeros)
        self.ninputs += 1
