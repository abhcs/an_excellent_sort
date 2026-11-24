"""Link check for the H9 class 02 15 36 (review issue 1).

Ties the four parts of the proof together:
  * every third layer named by the fourth-layer certificate and by the ending certificate is one of
    the 18 reduced forms FORMS, under the case number used throughout (case k is FORMS[k-1]);
  * case 2 is absent from both (it has its own idle-wire proof), and every other case appears in the
    fourth-layer certificate;
  * the 31 (case, third, fourth) triples excluded by the ending certificate are exactly the fourth
    layers that survive the fourth-layer classification.
Solver-free; prints a JSON record and exits non-zero on any mismatch."""
import json
import sys
from pathlib import Path

from h9_recovery_021536_reduction_verify import FORMS

HERE = Path(__file__).resolve().parent
RES = HERE.parent / 'results'


def norm_layer(layer):
    if isinstance(layer, str):
        return tuple(sorted(tuple(sorted((int(p[0]), int(p[1])))) for p in layer.split()))
    return tuple(sorted(tuple(sorted(map(int, p))) for p in layer))


forms = {k + 1: norm_layer(f) for k, f in enumerate(FORMS)}
fourths = json.loads((RES / 'h9-recovery-021536-fourths-certificate.json').read_text())['cases']
endings = json.loads((RES / 'h9-recovery-021536-endings-certificate.json').read_text())['records']

problems = []
survivors = set()
seen_cases = set()
for case in fourths:
    k = case['case']
    seen_cases.add(k)
    if norm_layer(case['third']) != forms[k]:
        problems.append(f'fourths case {k}: third layer differs from FORMS[{k - 1}]')
    for n in case['fourths']:
        survivors.add((k, forms[k], norm_layer(n)))
expected_cases = set(range(1, 19)) - {2}
if seen_cases != expected_cases:
    problems.append(f'fourths certificate covers cases {sorted(seen_cases)}, expected {sorted(expected_cases)}')
ending_set = set()
for r in endings:
    k = r['case']
    if norm_layer(r['third']) != forms[k]:
        problems.append(f'ending {k}.{r["number"]}: third layer differs from FORMS[{k - 1}]')
    ending_set.add((k, forms[k], norm_layer(r['fourth'])))
if survivors != ending_set:
    problems.append(f'survivors minus endings: {sorted(survivors - ending_set)}; '
                    f'endings minus survivors: {sorted(ending_set - survivors)}')
res = {'status': 'LINKED' if not problems else 'MISMATCH', 'forms': len(forms),
       'fourths_cases': sorted(seen_cases), 'survivors': len(survivors), 'endings': len(ending_set),
       'problems': problems}
print(json.dumps(res, indent=1))
sys.exit(0 if not problems else 1)
