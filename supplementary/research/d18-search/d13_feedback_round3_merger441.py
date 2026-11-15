#!/usr/bin/env python3
"""Small positive-control search for merging sorted blocks4+4+1 in4 layers."""
import hashlib
import json
from pathlib import Path
import time

from netsat import Model, apply_layers, is_sorted, prefix_images, verify_all


def main():
    started = time.monotonic()
    prefix = [[(0,1),(2,3),(4,5),(6,7)],
              [(0,2),(1,3),(4,6),(5,7)], [(1,2),(5,6)]]
    universe = sorted(prefix_images(9,prefix))
    expected = {sum(1<<v for v in range(a,4)) + sum(1<<v for v in range(4+b,8)) + (c<<8)
                for a in range(5) for b in range(5) for c in range(2)}
    assert set(universe) == expected and len(universe) == 50
    model = Model(9,4,universe)
    for x in universe:
        if not is_sorted(x,9):
            model.add_input(x)
    out = Path(__file__).parent/'results/d13_feedback_round3-merger441.json'
    result = dict(status='BUILT', scope='Four-layer merger of three independently sorted blocks4,4,1',
                  prefix=prefix, binary_merger_inputs=len(universe), variables=model.nv, clauses=model.ncl,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2)+'\n')
    try:
        sat = model.S.solve()
        result['status'] = 'SAT' if sat else 'UNSAT_UNCHECKED'
        if sat:
            merger = model.network(model.S.get_model())
            assert verify_all(9,prefix+merger)
            result.update(merger=merger, network=prefix+merger, verified_binary_inputs=512,
                          merger_image=[apply_layers(merger,x) for x in universe])
        result['seconds'] = time.monotonic()-started
        out.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:
        model.S.delete()


if __name__ == '__main__':
    main()
