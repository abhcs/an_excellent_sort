#!/usr/bin/env python3
"""Concrete real-input endpoint certificates for three fixed D18 six-prefixes.

No SAT: this constructs lifts of oracle witnesses, then verifies their real
comparison runs. The printed endpoint tables are sufficient hand premises.
"""
import hashlib
import itertools
import json
from pathlib import Path

from netsat import apply_layers

HERE=Path(__file__).resolve().parent


def run(prefix,values):
    values=list(values)
    for layer in prefix:
        for a,b in layer:values[a],values[b]=min(values[a],values[b]),max(values[a],values[b])
    return values


def preimages(n,prefix):
    image={x:x for x in range(1<<n)}
    for layer in prefix:
        following={}
        for state,original in image.items():following.setdefault(apply_layers([layer],state),original)
        image=following
    return image


def lift(bits,n):
    result=[None]*n
    for rank,v in enumerate([v for v in range(n) if not(bits>>v&1)]+[v for v in range(n) if bits>>v&1]):result[v]=rank
    return result


def main():
    records=[]
    for name,pivots in (('beam00',[12]),('beam16',[6]),('beam32',[5,12])):
        source=HERE/f'results/rank-layer-round6-{name}.json'
        data=json.loads(source.read_text());prefix=data['prefix'];n=data['n'];original=preimages(n,prefix)
        actions={tuple(a['edge']) if a['edge'] else ('idle',a['idle']):a for a in data['actions']}
        bank=[];rows=[]
        def witness(row,kind):
            bits=row['zero_witness' if kind=='low' else 'one_witness']
            values=lift(original[bits],n)
            if values not in bank:bank.append(values)
            return bank.index(values),values
        for pivot in pivots:
            for partner in [None]+[v for v in range(n) if v!=pivot]:
                key=('idle',pivot) if partner is None else tuple(sorted((pivot,partner)))
                action=actions[key]
                bad=next((r for r in action['intervals'] if r['width']>8),None)
                if bad is None:continue
                low,lv=witness(bad,'low');high,hv=witness(bad,'high')
                suffix=[] if partner is None else [[list(key)]]
                lo=run(prefix+suffix,lv)[bad['wire']];hi=run(prefix+suffix,hv)[bad['wire']]
                assert hi-lo>=8
                rows.append(dict(pivot=pivot,partner=partner,output_wire=bad['wire'],low_input=low,low=lo,high_input=high,high=hi))
        parity=[]
        if name=='beam32':
            # The only width-feasible partners are {2,8} for both pivots.
            for pivot in pivots:
                allowed=[v for v in range(n) if v!=pivot and all(r['width']<=8 for r in actions[tuple(sorted((pivot,v)))]['intervals'])]
                assert allowed==[2,8]
            for first,second in (((2,12),(2,12)),((8,12),(2,5))):
                left=actions[tuple(sorted(first))]['intervals'];right=actions[tuple(sorted(second))]['intervals']
                pair=next((x,y) for x in left for y in right if x['wire']!=y['wire'] and x['width']==y['width']==8 and max(0,min(x['hi'],y['hi'])-max(x['lo'],y['lo'])+1)%2)
                endpoints=[]
                for edge,row in zip((first,second),pair):
                    lo,lv=witness(row,'low');hi,hv=witness(row,'high')
                    low=run(prefix+[[list(sorted(edge))]],lv)[row['wire']]
                    high=run(prefix+[[list(sorted(edge))]],hv)[row['wire']]
                    assert (low,high)==(row['lo'],row['hi'])
                    endpoints.append(dict(edge=edge,wire=row['wire'],low_input=lo,low=low,high_input=hi,high=high))
                overlap=max(0,min(x['hi'] for x in pair)-max(x['lo'] for x in pair)+1)
                parity.append(dict(endpoints=endpoints,odd_intersection=overlap))
        else:
            assert len(rows)==18
        record=dict(name=name,prefix=prefix,rank_inputs=bank,width_exclusions=rows,parity=parity,
                    source_result_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        records.append(record)
    report=dict(status='VERIFIED',sat_used=False,records=records,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Three concrete six-layer prefixes; explicit real-input endpoints, no SAT premise')
    (HERE/'results/rank-layer-round6-hand-certificate.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Hand endpoint tables for three D18 six-layer prefixes','',
      'Each input lists the eighteen distinct ranks at original input positions. All ranks are zero-based.',
      'A gap of at least eight after the proposed seventh layer is impossible with only three layers left.','']
    for r in records:
        lines += [f'## {r["name"]}','', 'The exact six-layer prefix is recorded with the certificate.','', '| Input | Ranks |','|---:|---|']
        lines += [f'| {i} | `{",".join(map(str,values))}` |' for i,values in enumerate(r['rank_inputs'])]
        lines += ['', '| Pivot | Excluded partner | Output wire | Low input:rank | High input:rank |', '|---:|---|---:|---|---|']
        lines += [f'| {x["pivot"]} | {x["partner"] if x["partner"] is not None else "idle"} | {x["output_wire"]} | {x["low_input"]}:{x["low"]} | {x["high_input"]}:{x["high"]} |' for x in r['width_exclusions']]
        for p in r['parity']:
            lines += ['',f'The following exact eight-position cones have odd intersection size {p["odd_intersection"]}:','', '| Edge | Output wire | Low input:rank | High input:rank |','|---|---:|---|---|']
            lines += [f'| {tuple(x["edge"])} | {x["wire"]} | {x["low_input"]}:{x["low"]} | {x["high_input"]}:{x["high"]} |' for x in p['endpoints']]
        lines += ['']
    (HERE/'rank-layer-round6-hand-tables.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(status='VERIFIED',input_bank_sizes=[len(r['rank_inputs']) for r in records],endpoint_exclusions=[len(r['width_exclusions']) for r in records],parity_pairs=sum(len(r['parity']) for r in records))))


if __name__=='__main__':main()
