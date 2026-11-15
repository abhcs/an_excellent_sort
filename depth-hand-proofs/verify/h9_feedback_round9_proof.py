#!/usr/bin/env python3
"""Independently replay fixed H9 03 14 67 / 03 16 27 hand premises.

No solver, discovery imports, all-nine-wire matching scan, or rank-input
search. Fourth-layer coverage uses only explicit five-wire base cases
and one-edge clause intersections on at most three remaining vertices.
"""
import hashlib
import itertools
import json
import time
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 3), (1, 4), (6, 7))
CERTIFICATE_SHA256 = 'a2515ba6952a2e01125fa5f43eb5f12c27ad117c8f2232e822ae160b1a312a85'


def normalize(edges):
    return tuple(sorted(tuple(sorted(e)) for e in edges))


def es(edges):
    return ' '.join(''.join(map(str, e)) for e in edges) or 'none'


def ps(p):
    return ' '.join(('+' if sign > 0 else '-') + str(i)
                    for i, sign in sorted((int(i), s) for i, s in p.items()))


def run(prefix, values):
    result = list(values)
    for layer in prefix:
        for a, b in layer:
            result[a], result[b] = min(result[a], result[b]), max(result[a], result[b])
    return tuple(result)


def trace(prefix, placement):
    placement = {int(i): s for i, s in placement.items()}
    signs = [placement.get(i, 0) for i in range(9)]
    tracks = list(range(9))
    gates = []
    for layer in prefix:
        for a, b in layer:
            if signs[a] == signs[b] == 0:
                gates.append((tracks[a], tracks[b]))
            elif signs[a] > signs[b]:
                signs[a], signs[b] = signs[b], signs[a]
                tracks[a], tracks[b] = tracks[b], tracks[a]
    positions = {v: i for i, v in enumerate(tracks)}
    boundary = [(positions[a], positions[b]) for a, b in gates]
    height = [0] * 9
    for a, b in boundary:
        height[a] = height[b] = max(height[a], height[b]) + 1
    return dict(placement=placement, signs=signs, tracks=tracks, gates=gates,
                boundary=boundary, height=max(height), real=[i for i, s in enumerate(signs) if not s])


def direct_orders(prefix, row):
    p = row['placement']
    real = sorted(set(range(9)) - set(p))
    count = 0
    for ranks in itertools.permutations(range(len(real))):
        values = [100 * p.get(i, 0) for i in range(9)]
        for i, value in zip(real, ranks):
            values[i] = value
        retained = run((row['gates'],), values)
        assert run(prefix, values) == tuple(retained[i] for i in row['tracks'])
        count += 1
    return count


def propagated_order(prefix):
    # Each update is a min/max inequality implication; no input enumeration.
    relation = {(i, i) for i in range(9)}
    for layer in prefix:
        for a, b in layer:
            old = relation
            relation = {(u, v) for u, v in old if u not in (a, b) and v not in (a, b)}
            relation |= {(a, a), (b, b), (a, b)}
            for v in set(range(9)) - {a, b}:
                if (a, v) in old or (b, v) in old:
                    relation.add((a, v))
                if (a, v) in old and (b, v) in old:
                    relation.add((b, v))
                if (v, a) in old or (v, b) in old:
                    relation.add((v, b))
                if (v, a) in old and (v, b) in old:
                    relation.add((v, a))
    return {(a, b) for a, b in relation if a < b}


def two_edge_bases(real, forbidden):
    """The explicit five-vertex recipe: choose idle, then one of three pairings."""
    assert len(real) == 5
    bases = set()
    for idle in real:
        a, b, c, d = sorted(set(real) - {idle})
        for pairs in (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))):
            if not set(pairs) & forbidden:
                bases.add(normalize(pairs))
    return bases


def perfect_six(vertices):
    """Fifteen third-layer K choices, using the elementary 5*3 recipe."""
    a = min(vertices)
    for b in sorted(set(vertices) - {a}):
        c, d, e, f = sorted(set(vertices) - {a, b})
        for rest in (((c, d), (e, f)), ((c, e), (d, f)), ((c, f), (d, e))):
            yield normalize(((a, b),) + rest)


def structural_checks(data):
    A={(0,3),(0,4),(1,4),(1,5),(2,3)}
    B={(0,3),(0,6),(1,6),(2,3),(2,7)}
    pi=data['image_map'];dual=data['duality']
    assert pi==[0,2,1,6,3,7,4,5,8]
    assert {(pi[a],pi[b]) for a,b in A|{(6,7)}} == B|{(4,5)}
    assert {(dual[b],dual[a]) for a,b in A|{(6,7)}} == A|{(6,7)}
    order_counts=[]
    for second,coordinates,relation in ((SECOND,(0,1,2,3,4,5),A),
                                        (data['other_second'],(0,1,2,3,6,7),B)):
        images=set();expected=set()
        for order in itertools.permutations(range(6)):
            values=[0]*9
            for i,v in zip(coordinates,order):values[i]=v
            images.add(tuple(run((FIRST,second),values)[i] for i in coordinates))
            if all(values[a]<values[b] for a,b in relation):expected.add(order)
        assert images==expected
        order_counts.append(len(images))
    assert order_counts==[61,61]
    specs=[({0:1,2:1},(3,4),((1,5),(6,7))),
           ({0:-1,4:-1},(0,1),((2,3),(6,7))),
           ({2:1,4:-1},(1,3),((0,4),(6,7)))]
    runs=0
    for placement,sentinels,gates in specs:
        row=trace((FIRST,SECOND),placement)
        assert tuple(i for i,s in enumerate(row['signs']) if s)==sentinels
        assert tuple(row['boundary'])==gates and row['height']==1
        runs+=direct_orders((FIRST,SECOND),row)
    thirds=sorted({normalize(((0,1),)+k) for k in perfect_six((2,4,5,6,7,8)) if (6,7) not in k})
    assert thirds==[normalize(c['third']) for c in data['cases']] and len(thirds)==12
    dual_forms={normalize((dual[a],dual[b]) for a,b in m) for m in thirds}
    assert all((3,4) in m and 1 not in {v for e in m for v in e} for m in dual_forms)
    assert not set(thirds)&dual_forms
    return dict(core_order_replays=1440,core_images=order_counts,
                image_isomorphism=True,image_duality=True,
                named_restriction_order_runs=runs,third_layer_forms=12)


def local_classification(c, table):
    number = c['case']
    forbidden = set(map(tuple, c['forbidden']))
    assert forbidden == propagated_order((FIRST, SECOND, c['third']))
    assert f"| {number} | `{es(c['third'])}` | `{es(c['forbidden'])}` |" in table
    real = c['base_real']
    assert any(r['real'] == real and r['demand'] == 2 for r in c['rows'])
    bases = two_edge_bases(real, forbidden)
    assert len(bases) == 12
    assert {normalize(r['base']) for r in c['branches']} == bases
    assert len(c['branches']) == 12
    assert number == 10 and real == [1,2,4,5,6]
    all_completions = set()
    arms_checked = 0
    for branch in c['branches']:
        base = normalize(branch['base'])
        free = set(range(9)) - {v for e in base for v in e}
        assert sorted(free) == branch['free'] and len(free) == 5
        allowed = set(itertools.combinations(sorted(free), 2)) - forbidden
        clauses = {}
        for item in branch['clauses']:
            r = c['rows'][item['row'] - 1]
            remaining = r['demand'] - sum(set(e) <= set(r['real']) for e in base)
            edges = {e for e in allowed if set(e) <= set(r['real'])}
            assert remaining == item['need'] and remaining in (1, 2)
            assert edges == set(map(tuple, item['edges']))
            assert item['row'] not in clauses
            clauses[item['row']] = (remaining, edges)
        anchor = clauses[branch['anchor']]
        assert {tuple(a['edge']) for a in branch['arms']} == anchor[1]
        assert len(branch['arms']) == len(anchor[1])
        obtained = set()
        for arm in branch['arms']:
            e = tuple(arm['edge'])
            remaining_vertices = free - set(e)
            available = set(itertools.combinations(sorted(remaining_vertices), 2)) - forbidden
            residual = [(i, need - (e in edges), edges) for i, (need, edges) in clauses.items()]
            pending = [(i, need, edges) for i, need, edges in residual if need > 0]
            need_two = any(need > 1 for _, need, _ in pending)
            assert arm['pending'] == [i for i, _, _ in pending]
            assert arm['impossible_need_two'] == need_two
            assert arm['optional'] == (not pending)
            second = available.copy()
            for _, _, edges in pending:
                second &= edges
            if need_two:
                second.clear()
            assert second == set(map(tuple, arm['seconds']))
            if not pending:
                obtained.add((e,))
            for f in second:
                obtained.add(normalize((e, f)))
            arms_checked += 1
        assert obtained == {normalize(x) for x in branch['completions']}
        for completion in obtained:
            whole = normalize(base + completion)
            assert len({v for e in whole for v in e}) == 2 * len(whole)
            assert all(sum(set(e) <= set(r['real']) for e in whole) >= r['demand'] for r in c['rows'])
            all_completions.add(whole)
        clause_text = '; '.join(f"{x['row']}:{x['need']}({es(x['edges'])})" for x in branch['clauses'])
        arm_text = '; '.join(es([x['edge']]) + '→' + ('optional ' if x['optional'] else '') +
                             ('{' + es(x['seconds']) + '}' if x['seconds'] else ('none' if x['optional'] else '∅'))
                             for x in branch['arms']) or 'empty anchor'
        completions = ' / '.join(es(x) for x in branch['completions']) or 'impossible'
        assert f"| `{es(branch['base'])}` | {clause_text} | {branch['anchor']} | {arm_text} | `{completions}` |" in table
    assert all_completions == {normalize(m) for m in c['fourths']}
    return arms_checked


def endpoints(row, outputs):
    p = row['pivot']
    assert row['low'] == min(x[p] for x in outputs)
    assert row['high'] == max(x[p] for x in outputs)
    assert outputs[row['low_input']][p] == row['low']
    assert outputs[row['high_input']][p] == row['high']


def guard(g, p, low, high, outputs):
    x = outputs[g['input']]
    if g['kind'] == 'low':
        assert x[p] <= high - 4
        excluded = {q for q in range(9) if q != p and x[q] <= high - 4}
    else:
        assert g['kind'] == 'high' and x[p] >= low + 4
        excluded = {q for q in range(9) if q != p and x[q] >= low + 4}
    assert excluded == set(g['excluded'])
    return excluded


def ep(r):
    return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"


def gs(g):
    return f"{chr(65+g['input'])} {'lo' if g['kind']=='low' else 'hi'}:{''.join(map(str,g['excluded']))}"


def rank_checks(data, table):
    inputs=data['rank_inputs']
    assert len(inputs)==17 and len({tuple(x) for x in inputs})==17
    for i,x in enumerate(inputs):
        assert sorted(x)==list(range(9))
        assert f"| {chr(65+i)} | `{''.join(map(str,x))}` |" in table
    expected={(c['case'],i):(c['third'],n) for c in data['cases'] for i,n in enumerate(c['fourths'],1)}
    grouped={};seen=set();own=reciprocal=0
    for r in data['rank_records']:
        key=(r['case'],r['number']);p=r['pivot'];identity=key+(p,)
        assert key in expected and identity not in seen;seen.add(identity)
        m,n=expected[key]
        assert r['third']==m and r['fourth']==n
        outputs=[run((FIRST,SECOND,m,n),x) for x in inputs]
        endpoints(r,outputs);assert r['high']-r['low']>=4
        excluded=set()
        for g in r['guards']:
            excluded|=guard(g,p,r['low'],r['high'],outputs);own+=1
        remaining=set(range(9))-{p}-excluded
        assert remaining==set(r['remaining'])
        assert remaining-set(r['allowed'])=={q['pivot'] for q in r['reciprocal']}
        for q in r['reciprocal']:
            endpoints(q,outputs)
            assert p in guard(q['guard'],q['pivot'],q['low'],q['high'],outputs)
            reciprocal+=1
            assert f"| {key[0]}.{key[1]} | {p} | {q['pivot']} | {ep(q)} | {gs(q['guard'])} |" in table
        assert f"| {key[0]}.{key[1]} | {p} | {ep(r)} | {'; '.join(gs(g) for g in r['guards'])} | {''.join(map(str,r['remaining'])) or 'empty'} | {''.join(map(str,r['allowed'])) or 'empty'} |" in table
        grouped.setdefault(key,[]).append(r)
    assert set(grouped)==set(expected) and len(grouped)==33
    hall=[]
    for key,rows in grouped.items():
        if len(rows)==1:
            assert rows[0]['allowed']==[]
            obstruction='isolated '+str(rows[0]['pivot'])
        else:
            assert len(rows)==2 and all(r['allowed']==[2] for r in rows)
            assert len({r['pivot'] for r in rows})==2 and all(r['pivot']!=2 for r in rows)
            obstruction='Hall '+','.join(str(r['pivot']) for r in rows)+'→2'
            hall.append(key)
        assert f"| {key[0]}.{key[1]} | `{es(expected[key][1])}` | {obstruction} |" in table
    assert sorted(hall)==[(3,1),(4,1),(4,2)]
    return dict(rank_inputs=17,distinct_prefix_runs=17*33,guard_records=36,
                isolated_forms=30,hall_forms=hall,own_threshold_guards=own,reciprocal_guards=reciprocal)


def local_positive_control():
    # Two demand-one clauses on five free vertices, sharing edge02.
    # The valid one-edge completion must not be lost to maximality.
    vertices = {0, 2, 4, 6, 7}
    clauses = ({(0, 2), (0, 4), (2, 4)}, {(0, 2), (0, 7), (2, 7)})
    allowed = set(itertools.combinations(sorted(vertices), 2)) - {(4, 7)}
    result = set()
    for e in clauses[0]:
        pending = [c for c in clauses if e not in c]
        available = {f for f in allowed if not set(e) & set(f)}
        if not pending:
            result.add((e,))
        for c in pending:
            available &= c
        result.update(normalize((e, f)) for f in available)
    expected = {((0, 2),), ((0, 2), (4, 6)), ((0, 2), (6, 7)),
                ((0, 4), (2, 7)), ((0, 7), (2, 4))}
    assert result == expected
    return dict(nonmaximal_completion_preserved=True, completions=5)


def pairings_four(vertices):
    a,b,c,d=sorted(vertices)
    return [normalize(((a,b),(c,d))),normalize(((a,c),(b,d))),normalize(((a,d),(b,c)))]


def has_two(c,vertices):
    assert any(set(r['real'])==set(vertices) and r['demand']==2 for r in c['rows'])


def finish_small_core(core,c):
    """One-edge intersections, after a structurally forced two/three-edge core."""
    core=normalize(core);forbidden=set(map(tuple,c['forbidden']))
    used={v for e in core for v in e}
    if len(used)!=2*len(core) or set(core)&forbidden:return set()
    free=set(range(9))-used
    assert len(free) in (3,5)
    allowed=set(itertools.combinations(sorted(free),2))-forbidden
    pending=[]
    for r in c['rows']:
        need=r['demand']-sum(set(e)<=set(r['real']) for e in core)
        if need>0:pending.append((need,{e for e in allowed if set(e)<=set(r['real'])}))
    if len(free)==3:
        if any(need>1 for need,_ in pending):return set()
        possible=allowed.copy()
        for _,edges in pending:possible&=edges
        answer={core} if not pending else set()
        answer|={normalize(core+(e,)) for e in possible}
        return answer
    assert pending
    _,anchor=min(pending,key=lambda r:len(r[1]))
    result=set()
    for e in anchor:result|=finish_small_core(core+(e,),c)
    return result


def case12_contradiction(c):
    has_two(c,{1,3,4,5,8});has_two(c,{3,4,6,7,8})
    has_two(c,{1,2,4,6,8});has_two(c,{1,3,4,6,8})
    assert {1,3,4,5,8}&{3,4,6,7,8}=={3,4,8}
    for e in ((3,4),(3,8)):
        remaining={1,2,4,6,8}-set(e)
        assert len(remaining)==4
        for pairing in pairings_four(remaining):
            assert not finish_small_core((e,)+pairing,c)
    triples=[{1,3,5},{1,3,6},{1,2,6},{3,6,7}]
    assert [set(r['real'])-{4,8} for r in c['rows']]==triples
    repeated={e for e in itertools.combinations((0,1,2,3,5,6,7),2)
              if sum(set(e)<=t for t in triples)>=2}
    assert repeated=={(1,3),(1,6),(3,6)}
    for e in repeated:
        unmet=[t-set(e) for t in triples if not set(e)<=t]
        assert len(unmet)==2 and all(len(t)==2 for t in unmet)
        assert unmet[0]&unmet[1]
    assert c['fourths']==[]


def recipe_classification(c):
    recipe=c['recipe'];kind=recipe['kind'];T=set(recipe.get('T',[]));cores=[]
    if kind in ('extensions','three_extensions'):
        assert len(T)==4
        outside=recipe['outside']
        assert len(set(outside))==len(outside) and not T&set(outside)
        for x in outside:has_two(c,T|{x})
        cores.extend(pairings_four(T))
        if kind=='extensions':
            assert len(outside)==2
            x,y=outside
            for e in itertools.combinations(sorted(T),2):
                u,v=sorted(T-set(e))
                cores.extend([normalize((e,(x,u),(y,v))),normalize((e,(x,v),(y,u)))])
        else:assert len(outside)==3
    elif kind=='triangle':
        assert len(T)==3
        ab,cd=map(tuple,recipe['outside_pairs'])
        assert not T&set(ab+cd) and len(set(ab+cd))==4
        has_two(c,T|set(ab));has_two(c,T|set(cd))
        assert ab in set(map(tuple,c['forbidden']))
        for e in itertools.combinations(sorted(T),2):
            t=next(iter(T-set(e)))
            cores.extend(normalize((e,cd,(t,a))) for a in ab)
    elif kind=='shared_pair':
        assert len(T)==4
        x,y=recipe['outside'];pair=tuple(recipe['pair']);S=set(recipe['S'])
        assert len(S)==3 and not S&(T|{x,y}) and set(pair)<=T
        has_two(c,T|{x});has_two(c,T|{y});has_two(c,set(pair)|S)
        perfect=set(recipe['perfect'])
        assert len(perfect)==4 and not perfect&set(pair)
        assert any(r['demand']==2 and set(r['real'])-set(pair)==perfect and len(set(r['real'])&set(pair))==1 for r in c['rows'])
        cores=[normalize((pair,)+p) for p in pairings_four(perfect)]
    else:
        assert kind=='triangle_contradiction' and c['case']==12
        case12_contradiction(c)
        return
    obtained=set()
    for core in cores:obtained|=finish_small_core(core,c)
    assert obtained=={normalize(n) for n in c['fourths']},(c['case'],obtained,c['fourths'])
    for n in obtained:
        assert all(sum(set(e)<=set(r['real']) for e in n)>=r['demand'] for r in c['rows'])


def optional_controls(data):
    cases={c['case']:c for c in data['cases']}
    for number,base,optional in [(2,((1,2),(3,4),(5,8)),((0,6),)),
                                 (4,((1,2),(3,5),(4,8)),((0,6),))]:
        actual={normalize(n) for n in cases[number]['fourths']}
        assert normalize(base) in actual and normalize(base+optional) in actual
    five={normalize(n) for n in cases[5]['fourths']}
    for j in pairings_four({1,4,6,7}):
        base=normalize(j+((3,5),))
        assert all(normalize(base+extra) in five for extra in ((),((0,2),),((0,8),)))
    for number in (6,7):
        actual={normalize(n) for n in cases[number]['fourths']}
        for j in pairings_four({1,4,5,6}):
            base=normalize(j+((3,8),))
            assert base in actual and normalize(base+((0,2),)) in actual
    eight={normalize(n) for n in cases[8]['fourths']}
    assert normalize(((1,2),(3,7),(4,8),(5,6))) in eight
    assert normalize(((0,6),(1,2),(3,7),(4,8))) not in eight
    return dict(optional_idle_extensions_checked=True,case8_forced56_not06=True)


def main():
    start = time.monotonic()
    cert = ROOT / 'results/h9-feedback-round9-certificate.json'
    note = ROOT / 'h9_feedback_round9_fence6.md'
    tablefile = ROOT / 'h9_feedback_round9_tables.md'
    assert hashlib.sha256(cert.read_bytes()).hexdigest() == CERTIFICATE_SHA256
    data = json.loads(cert.read_text())
    table = tablefile.read_text()
    assert normalize(data['first']) == FIRST and normalize(data['second']) == SECOND
    structural = structural_checks(data)
    runs = clauses = branches = 0
    for c in data['cases']:
        prefix = (FIRST, SECOND, c['third'])
        for i, r in enumerate(c['rows'], 1):
            row = trace(prefix, r['placement'])
            assert row['real'] == r['real'] and len(row['real']) == 5
            assert len(row['gates']) == 3 - r['demand'] and r['demand'] in (1, 2)
            runs += direct_orders(prefix, row)
            assert f"| {c['case']} | {i} | `{ps(r['placement'])}` | {''.join(map(str,r['real']))} | {r['demand']} |" in table
        if c['case']==10:
            branches += local_classification(c,table)
        else:
            recipe_classification(c)
            assert set(map(tuple,c['forbidden']))==propagated_order(prefix)
            assert f"| {c['case']} | `{es(c['third'])}` | `{es(c['forbidden'])}` |" in table
        clauses += sum(len(b['clauses']) for b in c['branches'])
    assert [len(c['fourths']) for c in data['cases']] == [1,2,1,2,9,6,6,4,1,0,1,0]
    ranks = rank_checks(data, table)
    assert time.monotonic() - start < 30
    report = dict(status='VERIFIED',solver_free=True, global_matching_enumeration=False,
                  structural=structural, demand_rows=66,demand_order_runs=runs,
                  total_restriction_order_runs=runs+structural['named_restriction_order_runs'],
                  five_vertex_bases=12,local_clauses=clauses,local_edge_branches=branches,
                  fourth_counts=[1,2,1,2,9,6,6,4,1,0,1,0],rank=ranks,
                  positive_control=local_positive_control(),optional_controls=optional_controls(data),
                  certificate_sha256=CERTIFICATE_SHA256,
                  table_sha256=hashlib.sha256(tablefile.read_bytes()).hexdigest(),
                  note_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic()-start)
    (ROOT / 'results/h9-feedback-round9-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
