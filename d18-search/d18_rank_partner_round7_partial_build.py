#!/usr/bin/env python3
"""Package universal partial-layer activity certificates from fixed banks."""
import hashlib
import json
from pathlib import Path
from d18_rank_partner_round7_probe import run, interval, parity_bad

ROOT=Path(__file__).parent
SPECS=[('beam00','beam00',[(1,4),(5,6),(12,13)],[12]),
       ('beam16','beam16',[(4,6),(5,15),(7,14),(16,17)],[6]),
       ('beam32a','beam32',[(0,1),(2,8),(4,5),(6,9),(10,14),(12,13)],[5,12]),
       ('beam32b','beam32',[(2,8),(3,7),(4,5),(6,9),(10,14),(12,13)],[5,12])]


def endpoint(values):
    lo,hi=interval(values)
    return dict(low=lo,high=hi,low_input=values.index(lo),high_input=values.index(hi))


def main():
    source=ROOT/'results/rank-layer-round6-hand-certificate.json';fixed=json.loads(source.read_text())
    sources={r['name']:r for r in fixed['records']};families=[]
    for name,source_name,partial,pivots in SPECS:
        record=sources[source_name];prefix=record['prefix'][:5];bank=record['rank_inputs'];n=len(bank[0])
        before=[run(prefix,x) for x in bank];after=[run([partial],x) for x in before]
        paired={a:b for a,b in partial}|{b:a for a,b in partial};free=set(range(n))-set(paired)
        mandatory=[dict(pivot=p,**endpoint([x[p] for x in after])) for p in pivots]
        exclusions=[];supports={p:[] for p in pivots}
        for p in pivots:
            pv=[x[p] for x in after]
            for v in range(n):
                if v==p:continue
                mates=[paired[v]] if v in paired else [None]+sorted(free-{v})
                for mate in mates:
                    vv=[x[v] if mate is None else (min if v<mate else max)(x[v],x[mate]) for x in before]
                    minimum=[min(a,b) for a,b in zip(pv,vv)];maximum=[max(a,b) for a,b in zip(pv,vv)]
                    a,b=endpoint(minimum),endpoint(maximum)
                    choices=[(ep['high']-ep['low'],op,ep) for op,ep in (('min',a),('max',b)) if ep['high']-ep['low']>=8]
                    base=dict(pivot=p,partner=v,mate=mate)
                    if choices:
                        _,op,ep=max(choices,key=lambda x:x[0]);exclusions.append(dict(**base,kind='width',output=op,**ep))
                    elif parity_bad((a['low'],a['high']),(b['low'],b['high'])):
                        overlap=max(0,min(a['high'],b['high'])-max(a['low'],b['low'])+1)
                        exclusions.append(dict(**base,kind='parity',minimum=a,maximum=b,odd_intersection=overlap))
                    else:supports[p].append(dict(partner=v,mate=mate))
        cross=[]
        if source_name=='beam32':
            for edge,op in (((8,12),'min'),((2,5),'max')):
                vals=[(min if op=='min' else max)(x[edge[0]],x[edge[1]]) for x in after]
                cross.append(dict(edge=edge,output=op,**endpoint(vals)))
        families.append(dict(name=name,source=source_name,prefix=prefix,fixed_sixth=partial,free=sorted(free),
                             mandatory=mandatory,exclusions=exclusions,supports=supports,cross_parity=cross))
    data=dict(status='FIXED_PARTIAL_LAYER_CERTIFICATE',source_certificate_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),families=families)
    target=ROOT/'results/d18-rank-partner-round7-partial-certificate.json';target.write_text(json.dumps(data,indent=2)+'\n')
    lines=['# Local activity tables for partial D18 sixth layers','',
           'These finite witnesses support the [partial-layer theorem](d18_rank_partner_round7_partial.md).',
           'Input indices refer to the unchanged bank of the source beam in [the original tables](rank-layer-round6-hand-tables.md).',
           'For each family, keep its fixed sixth-layer gates. A proposed seventh-layer partner v may be idle in layer6 (`idle`) or have the sixth-layer mate listed. All unlisted sixth-layer gates are disjoint and cannot affect the values tested.',
           'A width row evaluates min or max at the proposed seventh-layer edge and shows a rank gap at least8. Partner/mate groups combine identical witnesses.','']
    groups_total=0
    for f in families:
        lines += [f"## {f['name']} (bank {f['source']})",'',
                  f"Fixed L6 gates: `{f['fixed_sixth']}`. Free wires: `{f['free']}`.",'',
                  '| Mandatory pivot | Low input:rank | High input:rank |','|---:|---|---|']
        for r in f['mandatory']:lines.append(f"| {r['pivot']} | {r['low_input']}:{r['low']} | {r['high_input']}:{r['high']} |")
        lines += ['','| Pivot | Proposed L7 partner | L6 mate(s) of partner | Output | Low input:rank | High input:rank |','|---:|---:|---|---|---|---|']
        groups={}
        for r in f['exclusions']:
            if r['kind']!='width':continue
            key=tuple(r[k] for k in ('pivot','partner','output','low_input','low','high_input','high'))
            groups.setdefault(key,[]).append(r['mate'])
        for (p,v,op,a,lo,b,hi),mates in groups.items():
            names=','.join('idle' if m is None else str(m) for m in mates)
            lines.append(f'| {p} | {v} | {names} | {op} | {a}:{lo} | {b}:{hi} |')
        groups_total+=len(groups)
        parity=[r for r in f['exclusions'] if r['kind']=='parity']
        if parity:
            lines += ['','Both outputs in each following row have witnessed span7. Their full cones would have the stated odd intersection.','',
                      '| Pivot | L7 partner | L6 mate | Minimum low/high input:rank | Maximum low/high input:rank | Odd overlap |','|---:|---:|---:|---|---|---:|']
            for r in parity:
                a,b=r['minimum'],r['maximum'];mate='idle' if r['mate'] is None else str(r['mate'])
                lines.append(f"| {r['pivot']} | {r['partner']} | {mate} | {a['low_input']}:{a['low']} / {a['high_input']}:{a['high']} | {b['low_input']}:{b['low']} / {b['high_input']}:{b['high']} | {r['odd_intersection']} |")
        lines+=['','After all local activities are considered, only these supports remain:','',
                '| Pivot | Remaining (L7 partner,L6 mate) choices |','|---:|---|']
        for p,support in f['supports'].items():
            choices='; '.join(f"({r['partner']},{'idle' if r['mate'] is None else r['mate']})" for r in support) or 'none'
            lines.append(f'| {p} | {choices} |')
        if f['cross_parity']:
            lines+=['','The two forced L7 edges have incompatible full cones:','',
                    '| L7 edge | Output | Low input:rank | High input:rank |','|---|---|---|---|']
            for r in f['cross_parity']:lines.append(f"| {tuple(r['edge'])} | {r['output']} | {r['low_input']}:{r['low']} | {r['high_input']}:{r['high']} |")
        lines.append('')
    lines+=['The [independent checker](d18_rank_partner_round7_partial_check.py) checks every allowed local activity, every displayed witness, and the exact fixed-source hash. No sixth-layer matching is enumerated.','']
    (ROOT/'d18_rank_partner_round7_tables.md').write_text('\n'.join(lines))
    print('families',len(families),'local width',sum(r['kind']=='width' for f in families for r in f['exclusions']),
          'local parity',sum(r['kind']=='parity' for f in families for r in f['exclusions']),'width groups',groups_total,'table lines',len(lines))


if __name__=='__main__':main()
