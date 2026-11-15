#!/usr/bin/env python3
"""Package fixed premises, independently checked by round5_proof.py."""
import json
from pathlib import Path


def edge_text(edges):
    return ' '.join(''.join(map(str,e)) for e in edges)


def ptext(p):
    return ' '.join(('+' if s>0 else '-')+str(i) for i,s in sorted((int(i),s) for i,s in p.items()))


def main():
    root=Path(__file__).parents[1]
    discovery=json.loads((root/'results/h9-feedback-round5-fourths.json').read_text())
    ranks=json.loads((root/'results/h9-feedback-round5-rank-bank.json').read_text())
    cases=[{key:c[key] for key in ('case','third','forbidden','rows','fourths')} for c in discovery['cases']]
    data=dict(second=[[0,2],[1,4],[5,6]],cases=cases,rank_cases=ranks['cases'],rank_inputs=ranks['inputs'],rank_rows=ranks['rows'])
    (root/'results/h9-feedback-round5-certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    lines=['# Fixed tables for the H9 case `02 14 56`','',
           'These are the finite premises of the [hand proof](h9_feedback_round5_021456.md).',
           'Comparators use two digits; longer strings denote position sets. Signed placements refer to original inputs.',
           'Every demand row retains exactly `3-demand` RR gates through L3.','',
           '## 1. Ordered pairs after L3','',
           '| Case | L3 | Forbidden L4 pairs |','|---:|---|---|']
    for c in cases:lines.append(f"| {c['case']} | `{edge_text(c['third'])}` | `{edge_text(c['forbidden'])}` |")
    lines+=['','## 2. Five-real demands','',
            '| Case | Row | Input sentinels | Reals after L3 | Required L4 edges |','|---:|---:|---|---|---:|']
    for c in cases:
        for i,r in enumerate(c['rows'],1):lines.append(f"| {c['case']} | {i} | `{ptext(r['placement'])}` | {''.join(map(str,r['real']))} | {r['demand']} |")
    lines+=['','## 3. Fourth-layer forms and isolated pivots','',
            'Each listed pivot must be used by L5, but every possible partner is excluded by its endpoint rows below.',
            'Cases7 and9 already fail the matching arguments.','',
            '| Label | L4 | Pivot |','|---|---|---:|']
    for r in ranks['cases']:lines.append(f"| {r['case']}.{r['number']} | `{edge_text(r['fourth'])}` | {r['pivot']} |")
    lines+=['','## 4. Fifteen concrete inputs','',
            'Each row is a permutation of ranks0 through8 on the original wires. Only these inputs need evaluation.','',
            '| Input | Ranks on wires0,...,8 |','|---|---|']
    for i,x in enumerate(ranks['inputs']):lines.append(f"| {chr(65+i)} | `{''.join(map(str,x))}` |")
    lines+=['','## 5. Endpoint exclusions','',
            '`idle` means the pivot value itself. Otherwise the output is the minimum or maximum of the pivot and proposed partner after L4.',
            'Every displayed low/high gap is at least four. The rank-interval lemma supplies at least five attainable ranks on that L5 output; its last two layers can reach at most four final positions.',
            'Grouped partner lists use identical witnesses.','']
    for case in ranks['cases']:
        key=(case['case'],case['number']);lines += [f'### {key[0]}.{key[1]}','',
            '| Pivot | Excluded partner(s) | Output | Low witness | High witness |','|---:|---|---|---|---|']
        groups={}
        for r in ranks['rows']:
            if (r['case'],r['number'])!=key:continue
            group=(r['pivot'],r['output'],r['low_input'],r['low'],r['high_input'],r['high'])
            groups.setdefault(group,[]).append(r['partner'])
        for (p,op,low,lo,high,hi),partners in groups.items():
            names=','.join('idle' if q is None else str(q) for q in partners)
            lines.append(f"| {p} | {names} | {op} | {chr(65+low)}:{lo} | {chr(65+high)}:{hi} |")
        lines.append('')
    lines+=['The [solver-free checker](verify/h9_feedback_round5_proof.py) reads back the printed premises and checks every rank exclusion. Its [audit](results/h9-feedback-round5-proof.json) records counts and hashes.','']
    (root/'h9_feedback_round5_tables.md').write_text('\n'.join(lines))
    print('cases',len(cases),'demands',sum(len(c['rows']) for c in cases),'fourths',len(ranks['cases']),'endpoint rows',len(ranks['rows']),'table lines',len(lines))


if __name__=='__main__':main()
