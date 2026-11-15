#!/usr/bin/env python3
"""Independent replay of partial-layer rank supports. No generator imports."""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT=Path(__file__).parent
EXPECTED={
 'beam00':('beam00',[(1,4),(5,6),(12,13)],[12]),
 'beam16':('beam16',[(4,6),(5,15),(7,14),(16,17)],[6]),
 'beam32a':('beam32',[(0,1),(2,8),(4,5),(6,9),(10,14),(12,13)],[5,12]),
 'beam32b':('beam32',[(2,8),(3,7),(4,5),(6,9),(10,14),(12,13)],[5,12]),
}


def run(prefix,values):
    x=list(values)
    for layer in prefix:
        used=set()
        for a,b in layer:
            assert 0<=a<b<len(x) and not {a,b}&used
            used.update((a,b))
            x[a],x[b]=min(x[a],x[b]),max(x[a],x[b])
    return x


def overlap(a,b):return max(0,min(a['high'],b['high'])-max(a['low'],b['low'])+1)


def same_edge_parity(a,b,c):
    return a['high']-a['low']==b['high']-b['low']==c-1 and overlap(a,b)%2==1


def observed(values):return dict(low=min(values),high=max(values))


def matching_count(n):
    a,b=1,1
    for k in range(2,n+1):a,b=b,b+(k-1)*a
    return 1 if n==0 else b


def table_rows(text):
    result=set();family=None
    for line in text.splitlines():
        head=re.fullmatch(r'## (beam\w+) \(bank beam\d+\)',line)
        if head:family=head[1]
        row=re.fullmatch(r'\| (\d+) \| (\d+) \| ([\d,idle]+) \| (min|max) \| (\d+):(\d+) \| (\d+):(\d+) \|',line)
        if row:
            p,v,mates,op,lo,l,hi,h=row.groups();assert family in EXPECTED
            for mate in mates.split(','):
                result.add((family,int(p),int(v),None if mate=='idle' else int(mate),op,int(lo),int(l),int(hi),int(h)))
    return result


def positive_controls():
    # The depth-three four-wire sorter is checked directly. Every nonempty
    # submatching of its first layer must retain each actual next-edge support.
    m=((0,1),(2,3));q=((0,2),(1,3));suffix=(((1,2),),);bank=list(itertools.permutations(range(4)))
    assert all(run((m,q)+suffix,x)==list(range(4)) for x in bank)
    tests=0
    for fixed in (((0,1),),((2,3),),m):
        used={v for e in fixed for v in e};free=set(range(4))-used
        partners={a:b for a,b in fixed}|{b:a for a,b in fixed}
        m_partner={a:b for a,b in m}|{b:a for a,b in m}
        for a,b in q:
            for p,v in ((a,b),(b,a)):
                if p not in used:continue
                mate=m_partner[v]
                assert mate==partners[v] if v in used else mate in free-{v}
                activity=[] if v in used else [(min(v,mate),max(v,mate))]
                output=[run((tuple(fixed)+tuple(activity),),x) for x in bank]
                low=observed([min(x[p],x[v]) for x in output]);high=observed([max(x[p],x[v]) for x in output])
                assert low['high']-low['low']<2 and high['high']-high['low']<2 and not same_edge_parity(low,high,2)
                tests+=1
    return dict(sorters=1,partial_layers=3,bank_inputs=24,support_checks=tests)


def main():
    original=ROOT/'results/rank-layer-round6-hand-certificate.json'
    cert=ROOT/'results/d18-rank-partner-round7-partial-certificate.json'
    tables=ROOT/'d18_rank_partner_round7_tables.md';note=ROOT/'d18_rank_partner_round7_partial.md'
    fixed=json.loads(original.read_text());data=json.loads(cert.read_text());text=tables.read_text()
    source_hash=hashlib.sha256(original.read_bytes()).hexdigest()
    assert source_hash==data['source_certificate_sha256']=='3d662a0b4ee885426c51ae7109cb5fc57f9818f4d9e684e1dc0612afaf8ff787'
    sources={r['name']:r for r in fixed['records']};printed=table_rows(text);expected_printed=set()
    direct=0;width=0;parity=0;crosses=0;activities=0;reports=[]
    for family in data['families']:
        name=family['name'];source_name,edges,pivots=EXPECTED[name];record=sources[source_name]
        assert family['source']==source_name and family['prefix']==record['prefix'][:5]
        assert list(map(tuple,family['fixed_sixth']))==edges
        assert set(edges)<=set(map(tuple,record['prefix'][5]))
        used={v for e in edges for v in e};assert len(used)==2*len(edges)
        free=set(range(18))-used;assert family['free']==sorted(free)
        paired={a:b for a,b in edges}|{b:a for a,b in edges}
        bank=record['rank_inputs'];assert all(sorted(x)==list(range(18)) for x in bank)
        prefix=family['prefix'];partial=family['fixed_sixth']
        assert [r['pivot'] for r in family['mandatory']]==pivots and set(pivots)<=used
        for row in family['mandatory']:
            for side in ('low','high'):
                value=run(prefix+[partial],bank[row[f'{side}_input']])[row['pivot']];direct+=1
                assert value==row[side]
            assert row['high']-row['low']>=8
            assert f"| {row['pivot']} | {row['low_input']}:{row['low']} | {row['high_input']}:{row['high']} |" in text
        domains={(p,v,mate) for p in pivots for v in range(18) if v!=p
                 for mate in ([paired[v]] if v in used else [None]+sorted(free-{v}))}
        seen=set()
        def local_layer(v,mate):
            if v in used:
                assert mate==paired[v];return partial
            assert mate is None or mate in free-{v}
            return partial+([] if mate is None else [[min(v,mate),max(v,mate)]])
        def endpoint(row,op,p,v,mate):
            nonlocal direct
            layer=local_layer(v,mate);wire=min(p,v) if op=='min' else max(p,v)
            for side in ('low','high'):
                value=run(prefix+[layer,[[min(p,v),max(p,v)]]],bank[row[f'{side}_input']])[wire];direct+=1
                assert value==row[side]
        for row in family['exclusions']:
            p,v,mate=row['pivot'],row['partner'],row['mate'];key=(p,v,mate)
            assert key in domains and key not in seen;seen.add(key)
            if row['kind']=='width':
                endpoint(row,row['output'],p,v,mate);assert row['high']-row['low']>=8;width+=1
                expected_printed.add((name,p,v,mate,row['output'],row['low_input'],row['low'],row['high_input'],row['high']))
            else:
                assert row['kind']=='parity';a,b=row['minimum'],row['maximum']
                endpoint(a,'min',p,v,mate);endpoint(b,'max',p,v,mate)
                assert same_edge_parity(a,b,8) and overlap(a,b)==row['odd_intersection'];parity+=1
                mate_text='idle' if mate is None else str(mate)
                line=f"| {p} | {v} | {mate_text} | {a['low_input']}:{a['low']} / {a['high_input']}:{a['high']} | {b['low_input']}:{b['low']} / {b['high_input']}:{b['high']} | {row['odd_intersection']} |"
                assert line in text
        remaining={}
        for p in pivots:
            support=family['supports'][str(p)];remaining[p]=sorted({r['partner'] for r in support})
            for item in support:
                v,mate=item['partner'],item['mate'];key=(p,v,mate);assert key in domains and key not in seen;seen.add(key)
                layer=local_layer(v,mate);values=[run(prefix+[layer],x) for x in bank];direct+=len(bank)
                a=observed([min(x[p],x[v]) for x in values]);b=observed([max(x[p],x[v]) for x in values])
                assert a['high']-a['low']<8 and b['high']-b['low']<8 and not same_edge_parity(a,b,8)
            choices='; '.join(f"({r['partner']},{'idle' if r['mate'] is None else r['mate']})" for r in support) or 'none'
            assert f'| {p} | {choices} |' in text
        assert seen==domains;activities+=len(domains)
        if source_name in ('beam00','beam16'):
            assert remaining[pivots[0]]==[] and not family['cross_parity']
        else:
            assert remaining=={5:[2,8],12:[8]}
            rows=family['cross_parity'];assert [(tuple(r['edge']),r['output']) for r in rows]==[((8,12),'min'),((2,5),'max')]
            assert {2,5,8,12}<=used
            for row in rows:
                a,b=row['edge'];wire=min(a,b) if row['output']=='min' else max(a,b)
                for side in ('low','high'):
                    value=run(prefix+[partial,[sorted((a,b))]],bank[row[f'{side}_input']])[wire];direct+=1
                    assert value==row[side]
                assert row['high']-row['low']==7
                assert f"| {tuple(row['edge'])} | {row['output']} | {row['low_input']}:{row['low']} | {row['high_input']}:{row['high']} |" in text
            assert overlap(*rows)==7;crosses+=1
        reports.append(dict(name=name,free_wires=len(free),local_activities=len(domains),remaining_supports=remaining,
                            labelled_layer_completions=matching_count(len(free))))
    assert {f['name'] for f in data['families']}==set(EXPECTED) and printed==expected_printed
    assert (activities,width,parity,crosses)==(444,436,2,2)
    assert matching_count(12)==140152 and matching_count(10)==9496 and matching_count(6)==76 and matching_count(4)==10
    positives=positive_controls()
    report=dict(status='VERIFIED',sat_used=False,full_layer_enumeration=False,families=reports,
                bank_entries=sum(len(r['rank_inputs']) for r in fixed['records']),
                distinct_input_permutations=len({tuple(x) for r in fixed['records'] for x in r['rank_inputs']}),local_activities=activities,
                width_exclusions=width,self_parity_exclusions=parity,forced_pair_parity_contradictions=crosses,
                direct_endpoint_and_support_runs=direct,beam32_union_labelled_completions=2*matching_count(6)-matching_count(4),
                positive_controls=positives,source_certificate_sha256=source_hash,
                certificate_sha256=hashlib.sha256(cert.read_bytes()).hexdigest(),tables_sha256=hashlib.sha256(tables.read_bytes()).hexdigest(),
                theorem_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/d18-rank-partner-round7-partial-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
