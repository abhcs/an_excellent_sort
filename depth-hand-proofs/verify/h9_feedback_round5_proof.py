#!/usr/bin/env python3
"""Audit the fixed 02 14 56 hand proof; no solver or discovery imports.

The moving-track trace and direct replay routines are shared with the
independently reviewed round4 checker. Matching scans corroborate the
displayed structural reductions, rather than replacing them as premises.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path
import h9_feedback_round4_proof as traces
from h9_feedback_round4_proof import trace, direct_orders, propagated_order, run, normalized, matchings

ROOT=Path(__file__).parents[1]
FIRST=((0,1),(2,3),(4,5))
SECOND=((0,2),(1,4),(5,6))
NAMED={'P':{0:1,2:-1,4:1},'B':{0:1,2:-1,6:-1},'C':{0:1,1:1,4:1},
       'D':{0:1,4:1},'E':{0:1,1:1,2:1,4:1},'F':{0:1,2:-1}}


def edge_text(edges):return ' '.join(''.join(map(str,e)) for e in edges)
def ptext(p):return ' '.join(('+' if s>0 else '-')+str(i) for i,s in sorted((int(i),s) for i,s in p.items()))
def parse(s):return normalized(tuple(map(int,e)) for e in s.split())
def perfect(vertices):return [m for m in matchings(sorted(vertices)) if len(m)*2==len(vertices)]
def rr(m,real):return [e for e in m if set(e)<=set(real)]


def expected_fourths():
    out={i:set() for i in range(1,10)}
    for u,v in ((7,8),(8,7)):
        for j in perfect({2,4,5,v}):out[1].add(normalized(((0,1),(3,u))+j))
        for a,b in itertools.combinations(range(3),2):
            c=({0,1,2}-{a,b}).pop()
            for j in perfect({3,4,5,v}):out[3].add(normalized(((a,b),(c,u))+j))
        out[5].update((normalized(((4,u),(5,v),(1,2))),normalized(((4,u),(5,v),(1,2),(3,6))),
                       normalized(((3,4),(5,u),(2,v))),normalized(((3,4),(5,u),(2,v),(0,1))),
                       normalized(((3,5),(4,u),(0,1),(2,v))),normalized(((3,u),(5,v),(0,1),(2,4))),
                       normalized(((3,u),(4,5),(0,1),(2,v))),normalized(((3,u),(4,v),(0,1),(2,5)))))
    out[2]={parse('01 24 38 57')};out[4]={parse('02 15 37 48')}
    out[6]={normalized(((0,1),(7,8))+j) for j in perfect({2,3,4,5})}|{parse('02 18 35 47')}
    out[8]={parse('02 18 37 45')}
    assert [len(out[i]) for i in range(1,10)]==[6,1,18,1,16,4,0,1,0]
    return out


def printed(data,text):
    for c in data['cases']:
        assert f"| {c['case']} | `{edge_text(c['third'])}` | `{edge_text(c['forbidden'])}` |" in text
        for i,r in enumerate(c['rows'],1):
            assert f"| {c['case']} | {i} | `{ptext(r['placement'])}` | {''.join(map(str,r['real']))} | {r['demand']} |" in text
    for r in data['rank_cases']:
        assert f"| {r['case']}.{r['number']} | `{edge_text(r['fourth'])}` | {r['pivot']} |" in text
    input_rows=re.findall(r'^\| ([A-Z]) \| `([0-8]{9})` \|$',text,re.M)
    assert [tuple(map(int,x)) for _,x in input_rows]==list(map(tuple,data['rank_inputs']))
    actual=set();key=None
    for line in text.splitlines():
        heading=re.fullmatch(r'### (\d+)\.(\d+)',line)
        if heading:key=tuple(map(int,heading.groups()))
        row=re.fullmatch(r'\| (\d) \| ([\d,idle]+) \| (idle|min|max) \| ([A-Z]):(\d) \| ([A-Z]):(\d) \|',line)
        if row:
            p,partners,op,lo,l,hi,h=row.groups();assert key is not None
            for q in partners.split(','):actual.add((*key,int(p),None if q=='idle' else int(q),op,ord(lo)-65,int(l),ord(hi)-65,int(h)))
    expected={(r['case'],r['number'],r['pivot'],r['partner'],r['output'],r['low_input'],r['low'],r['high_input'],r['high']) for r in data['rank_rows']}
    assert actual==expected


def residuals(case,base):
    used={v for e in base for v in e};free=set(range(9))-used;forbid=set(map(tuple,case['forbidden']))
    result=set()
    for row in case['rows']:
        need=row['demand']-len(rr(base,row['real']))
        if need==1:
            result.add(frozenset(e for e in itertools.combinations(sorted(free),2) if set(e)<=set(row['real']) and e not in forbid))
    return result


def clause(case,base,edges):
    assert frozenset(normalized(edges)) in residuals(case,base),(case['case'],base,edges)


def audit_hand_clauses(cases):
    count=0
    # Case3: three triangle clauses in each of its six positive branches.
    for u,v in ((7,8),(8,7)):
        for edge,triangles in (((0,1),[(3,4,v),(3,5,v),(3,4,5)]),
                               ((0,2),[(3,5,v),(4,5,v),(3,4,5)]),
                               ((1,2),[(3,4,v),(4,5,v),(3,4,5)])):
            a=({0,1,2}-set(edge)).pop();base=(edge,(a,u))
            for tri in triangles:clause(cases[3],base,itertools.combinations(sorted(tri),2));count+=1
        for base,clauses in (
            (((0,u),(1,v)),[[(3,4),(3,6)],[(2,3),(3,5)]]),
            (((0,u),(2,v)),[[(4,5),(5,6)],[(1,5),(3,5)]]),
            (((1,u),(2,v)),[[(0,4),(3,4)],[(3,4),(3,6)],[(3,4),(3,5),(4,5)],[(0,4),(4,5)]])):
            for edges in clauses:clause(cases[3],base,edges);count+=1
        # The six parameterized rows of the case5 table.
        patterns=[(((4,u),(5,v)),[[(0,1),(1,2)],[(1,2),(1,3)]]),
                  (((3,4),(5,u)),[[(0,v),(2,v)],[(1,2),(1,v),(2,v)],[(2,6),(2,v),(6,v)]]),
                  (((3,5),(4,u)),[[(0,1),(1,2)],[(0,v),(2,v)],[(2,6),(2,v),(6,v)]]),
                  (((3,u),(5,v)),[[(0,1),(1,2)],[(0,4),(2,4)],[(2,4),(2,6)]]),
                  (((3,u),(4,5)),[[(0,v),(2,v)],[(0,1),(1,2)],[(2,6),(2,v),(6,v)]]),
                  (((3,u),(4,v)),[[(0,1),(1,2)],[(1,2),(2,5)],[(2,5),(2,6)]])]
        for base,clauses in patterns:
            for edges in clauses:clause(cases[5],base,edges);count+=1
    for base,clauses in (
        (parse('02 35'),['17 18 78','47 48 78','47 67']),
        (parse('03 25'),['67 68 78','17 18 78','47 48 78','47 67']),
        (parse('05 23'),['67 68 78','17 18 78','17 47','47 67'])):
        for s in clauses:clause(cases[6],base,parse(s));count+=1
    for base in map(parse,['12 04 35','13 04 25','12 34 05','13 24 05','12 45 03','13 45 02']):
        clause(cases[6],base,[(6,7)]);clause(cases[6],base,[(7,8)]);count+=2
    for s in ('45 56','15 18 58','45 48 58'):clause(cases[8],parse('02 37'),parse(s));count+=1
    return count


def main():
    cert=ROOT/'results/h9-feedback-round5-certificate.json';table=ROOT/'h9_feedback_round5_tables.md'
    data=json.loads(cert.read_text());printed(data,table.read_text())
    layers=list(matchings(list(range(9))));prefix2=(FIRST,SECOND);order2=propagated_order(prefix2)
    assert order2==set(parse('02 03 04 14 16 56'))
    direct=0;initial=[]
    for p,s,g in (({0:-1,4:-1},{0,1},parse('23 56')),({0:-1,4:1},{0,6},parse('14 23'))):
        r=trace(prefix2,p);assert set(range(9))-set(r['real'])==s and normalized(r['boundary'])==g and r['height']==1
        direct+=direct_orders(prefix2,r);initial.append(r)
    initial_matchings={m for m in layers if not set(m)&order2 and all(len(rr(m,set(range(9))-s))>=3 for s in ({0,1},{0,6}))}
    type_a={normalized(k+extra) for k in perfect({2,3,4,5,7,8}) for extra in ((),((0,1),),((0,6),))}
    type_b={m for m in perfect(set(range(1,9))) if not set(m)&order2}
    assert initial_matchings==type_a|type_b and len(initial_matchings)==108
    third_audit=[]
    def checked(m,name):
        nonlocal direct
        prefix=prefix2+(m,);r=trace(prefix,NAMED[name]);direct+=direct_orders(prefix,r);return r
    def odd(m,a,b):
        x,y=checked(m,a),checked(m,b)
        assert len(x['gates'])==len(y['gates'])==2 and x['height']==y['height']==1
        assert len(set(x['real'])&set(y['real']))==5
        return [x,y]
    for m in sorted(type_a):
        if (4,5) not in m:kind='A_without45';rows=odd(m,'P','B')
        elif (0,1) in m:
            kind='A_with01';rows=[checked(m,'F')];assert len(rows[0]['gates'])==4 and rows[0]['height']==2
        elif (2,3) not in m:
            kind='A_blind';rows=[checked(m,'E')];assert not rows[0]['gates']
        else:kind='A_last';rows=odd(m,'P','C')
        third_audit.append(dict(third=m,kind=kind,traces=rows))
    survivors=set()
    for m in sorted(type_b):
        if (4,6) in m:survivors.add(m);continue
        partner={a:b for a,b in m}|{b:a for a,b in m}
        if partner[2] in (4,6):
            kind='B_deep2';rows=[checked(m,'D')];assert len(rows[0]['gates'])==4 and rows[0]['height']==2
        elif partner[3] in (2,4,6):kind='B_odd';rows=odd(m,'P','C')
        else:kind='B_blind';rows=[checked(m,'E')];assert not rows[0]['gates']
        third_audit.append(dict(third=m,kind=kind,traces=rows))
    expected_m={normalized(((4,6),)+k) for k in perfect({1,2,3,5,7,8})}
    assert survivors==expected_m and len(survivors)==15
    swap=lambda i:8 if i==7 else 7 if i==8 else i
    canonical=lambda m:min(m,normalized((swap(a),swap(b)) for a,b in m))
    assert {canonical(m) for m in survivors}=={normalized(c['third']) for c in data['cases']}
    assert len(data['cases'])==9
    expected_n=expected_fourths();cases={c['case']:c for c in data['cases']};demand_audit=[]
    for case in cases.values():
        prefix=prefix2+(normalized(case['third']),);forbidden=propagated_order(prefix)
        assert forbidden==set(map(tuple,case['forbidden']))
        assert all(x[a]<=x[b] for x in (run(prefix,bits) for bits in itertools.product((0,1),repeat=9)) for a,b in forbidden)
        rows=[]
        for item in case['rows']:
            r=trace(prefix,item['placement']);assert r['real']==item['real'] and len(r['gates'])==3-item['demand']
            direct+=direct_orders(prefix,r);rows.append(r)
        passing={n for n in layers if not set(n)&forbidden and all(len(rr(n,r['real']))>=r['demand'] for r in case['rows'])}
        assert passing==expected_n[case['case']]==set(map(normalized,case['fourths']))
        demand_audit.append(dict(case=case['case'],traces=rows,fourths=len(passing)))
    hand_clauses=audit_hand_clauses(cases)
    bank=list(map(tuple,data['rank_inputs']));assert len(bank)==15 and all(sorted(x)==list(range(9)) for x in bank)
    cache={};expected_actions=set();rank_cases={}
    for r in data['rank_cases']:
        key=(r['case'],r['number']);assert key not in rank_cases;rank_cases[key]=r
        c=cases[r['case']];assert normalized(r['third'])==normalized(c['third'])
        assert normalized(r['fourth'])==normalized(c['fourths'][r['number']-1])
        cache[key]=[run(prefix2+(r['third'],r['fourth']),x) for x in bank]
        expected_actions.update((*key,r['pivot'],q) for q in [None]+[j for j in range(9) if j!=r['pivot']])
    assert len(rank_cases)==47 and {key for key in rank_cases}=={(c['case'],j) for c in data['cases'] for j in range(1,len(c['fourths'])+1)}
    actions=set()
    for r in data['rank_rows']:
        key=(r['case'],r['number']);p,q,op=r['pivot'],r['partner'],r['output'];assert p==rank_cases[key]['pivot']
        assert (q is None)==(op=='idle');actions.add((*key,p,q))
        for side in ('low','high'):
            x=cache[key][r[f'{side}_input']]
            value=x[p] if op=='idle' else min(x[p],x[q]) if op=='min' else max(x[p],x[q])
            assert value==r[side]
        assert r['high']-r['low']>=4
    assert actions==expected_actions and len(actions)==len(data['rank_rows'])==423
    report=dict(status='VERIFIED',solver_free=True,second=SECOND,third_initial_forms=108,third_final_forms=15,
                canonical_thirds=9,fourth_forms=47,demand_rows=76,hand_clause_checks=hand_clauses,
                rank_inputs=15,rank_prefix_runs=15*47,rank_endpoint_exclusions=423,direct_real_order_runs=direct,
                first_two_traces=initial,third_audit=third_audit,demand_audit=demand_audit,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                trace_helper_sha256=hashlib.sha256(Path(traces.__file__).read_bytes()).hexdigest(),
                certificate_sha256=hashlib.sha256(cert.read_bytes()).hexdigest(),
                tables_sha256=hashlib.sha256(table.read_bytes()).hexdigest(),
                proof_sha256=hashlib.sha256((ROOT/'h9_feedback_round5_021456.md').read_bytes()).hexdigest())
    (ROOT/'results/h9-feedback-round5-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('first_two_traces','third_audit','demand_audit')},indent=2))


if __name__=='__main__':main()
