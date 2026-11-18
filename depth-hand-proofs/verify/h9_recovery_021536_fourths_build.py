#!/usr/bin/env python3
"""Freeze small local hand tables from the recovered signed-demand witnesses."""
import itertools
import json
from pathlib import Path
from h9_recovery_021536_fourths_check import ROOT, cores, es, local_proof, pending, table_line


def tiny_completions(free, allowed, clauses):
    # Discovery only, at most five free vertices (26 matchings).
    poss = [()] + [(e,) for e in sorted(allowed)]
    poss += [(e, f) for e, f in itertools.combinations(sorted(allowed), 2) if not set(e) & set(f)]
    return {x for x in poss if all(sum(e in set(map(tuple, r['edges'])) for e in x) >= r['need'] for r in clauses)}


def main():
    source = json.loads((ROOT / 'results/h9-recovery-021536-endings-discovery.json').read_text())
    out = {'status': 'FIXED_LOCAL_HAND_CERTIFICATE', 'cases': []}
    lines = ['# Fixed fourth-layer tables for `02 15 36`', '',
             'These tables accompany [the hand classification](h9_recovery_021536_fourths.md).',
             'Case 2 has a separate idle-wire certificate. Rows number signed five-real demands.',
             'A local clause `r:k(edges)` requires k of the listed additional edges.',
             'Each core leaves at most five unused wires; the local table rule is proved in the note.', '']
    for saved in source['cases']:
        if saved['case'] == 2: continue
        c = {key: saved[key] for key in ('case', 'third', 'forbidden', 'rows')}
        c['core_tables'] = []; c['fourths'] = [r['fourth'] for r in saved['fourths']]
        lines += [f"## Case {c['case']}: M=`{es(c['third'])}`", '',
                  f"Forbidden N edges: `{es(c['forbidden'])}`.", '',
                  '| Row | Original sentinels | Real set | Demand |', '|---:|---|---|---:|']
        for i, r in enumerate(c['rows'], 1):
            p = {int(v): s for v, s in r['placement'].items()}
            ps = ' '.join(('+' if p[v] > 0 else '-') + str(v) for v in sorted(p))
            lines.append(f"| {i} | `{ps}` | {''.join(map(str, r['real']))} | {r['demand']} |")
        for core in cores(c):
            free, allowed, clauses = pending(c, core)
            target = tiny_completions(free, allowed, clauses)
            selected = list(clauses)
            for r in clauses:
                trial = [x for x in selected if x is not r]
                if tiny_completions(free, allowed, trial) == target: selected = trial
            finishes, arms = local_proof(free, allowed, selected)
            assert finishes == target
            c['core_tables'].append(dict(core=core, clauses=selected, completions=sorted(finishes)))
        lines += ['', '| Forced core | Unmet clauses | Additional edges |', '|---|---|---|']
        if c['core_tables']: lines += [table_line(r) for r in c['core_tables']]
        else:
            label = {6: 'Common-pair contact contradiction', 17: 'Weighted demand17 exceeds capacity16'}.get(c['case'], 'Odd-core deletion obstruction')
            lines += [f'| none | {label} | `impossible` |']
        lines += ['', 'Surviving N: ' + ('; '.join('`' + es(M) + '`' for M in c['fourths']) or 'none') + '.', '']
        out['cases'].append(c)
    (ROOT / 'results/h9-recovery-021536-fourths-certificate.json').write_text(json.dumps(out, indent=2) + '\n')
    (ROOT / 'h9_recovery_021536_fourths_tables.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'cases': len(out['cases']), 'cores': sum(len(c['core_tables']) for c in out['cases'])}))


if __name__ == '__main__': main()
