#!/usr/bin/env python3
"""Independent fixed-certificate replay. No oracle, SAT, or generator imports."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def run(prefix,values):
    state=list(values)
    for layer in prefix:
        used=set()
        for a,b in layer:
            assert 0<=a<b<len(state) and a not in used and b not in used
            used.update((a,b))
            lo,hi=sorted((state[a],state[b]));state[a],state[b]=lo,hi
    return state


def main():
    source=HERE/'results/rank-layer-round6-hand-certificate.json'
    data=json.loads(source.read_text());text=(HERE/'rank-layer-round6-hand-tables.md').read_text()
    assert [r['name'] for r in data['records']]==['beam00','beam16','beam32']
    count=0;parity_pairs=0;inputs=0
    for record in data['records']:
        prefix=record['prefix'];assert len(prefix)==6
        bank=record['rank_inputs'];assert all(sorted(v)==list(range(18)) for v in bank)
        inputs+=len(bank)
        for i,v in enumerate(bank):assert f'| {i} | `{",".join(map(str,v))}` |' in text
        actual={}
        for row in record['width_exclusions']:
            p,q=row['pivot'],row['partner'];key=(p,q);assert key not in actual
            actual[key]=row
            extra=[] if q is None else [[sorted((p,q))]]
            low=run(prefix+extra,bank[row['low_input']])[row['output_wire']]
            high=run(prefix+extra,bank[row['high_input']])[row['output_wire']]
            assert (low,high)==(row['low'],row['high']) and high-low>=8
            assert row['output_wire']==p if q is None else row['output_wire'] in (p,q)
            line=f'| {p} | {q if q is not None else "idle"} | {row["output_wire"]} | {row["low_input"]}:{low} | {row["high_input"]}:{high} |'
            assert line in text;count+=1
        if record['name'] in ('beam00','beam16'):
            pivot=12 if record['name']=='beam00' else 6
            assert set(actual)=={(pivot,q) for q in [None]+list(range(18)) if q!=pivot}
            assert not record['parity']
        else:
            expected={(p,q) for p in (5,12) for q in [None]+list(range(18)) if q not in (p,2,8)}
            assert set(actual)==expected and len(record['parity'])==2
            expected_edges=[[(2,12),(2,12)],[(8,12),(2,5)]]
            for i,pair in enumerate(record['parity']):
                endpoints=pair['endpoints'];assert [tuple(e['edge']) for e in endpoints]==expected_edges[i]
                assert endpoints[0]['wire']!=endpoints[1]['wire']
                for row in endpoints:
                    edge=sorted(row['edge']);assert row['wire'] in edge
                    low=run(prefix+[[edge]],bank[row['low_input']])[row['wire']]
                    high=run(prefix+[[edge]],bank[row['high_input']])[row['wire']]
                    assert (low,high)==(row['low'],row['high']) and high-low==7
                    assert f'| {tuple(row["edge"])} | {row["wire"]} | {row["low_input"]}:{low} | {row["high_input"]}:{high} |' in text
                overlap=max(0,min(r['high'] for r in endpoints)-max(r['low'] for r in endpoints)+1)
                assert overlap==pair['odd_intersection'] and overlap%2
                parity_pairs+=1
    report=dict(status='VERIFIED',sat_used=False,explicit_input_permutations=inputs,
        width_exclusions=count,odd_cone_pairs=parity_pairs,direct_prefix_runs=2*count+4*parity_pairs,
        certificate_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        tables_sha256=hashlib.sha256((HERE/'rank-layer-round6-hand-tables.md').read_bytes()).hexdigest(),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Concrete six-prefix hand certificates; no search over continuations')
    (HERE/'results/rank-layer-round6-hand-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
