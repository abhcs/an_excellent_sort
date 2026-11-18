#!/usr/bin/env python3
"""Build fixed rank and saturated-cone certificates for 31 surviving N forms."""
import hashlib
import itertools
import json
import random
import time
from pathlib import Path
from netlib import run
from h9_feedback_round4_rank_witnesses import lift
from h9_feedback_round5_partner_build import guards,cover,anchors

ROOT=Path(__file__).parents[1]
FIRST=((0,1),(2,3),(4,5));SECOND=((0,2),(1,5),(3,6))
EXCEPTIONS={
    (1,4): ([(1,[3]),(4,[2,3])], (2,4)),
    (8,2): ([(8,[5])], (5,8)),
    (9,1): ([(7,[3])], (3,7)),
    (14,1): ([(7,[3])], (3,7)),
    (16,2): ([(8,[4])], (4,8)),
}

def edge_text(edges):return ' '.join(''.join(map(str,e)) for e in edges) or 'none'
def ep(r):return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"
def gs(g):return f"{chr(65+g['input'])} {'lo' if g['kind']=='low' else 'hi'}:{''.join(map(str,g['excluded'])) or 'none'}"

def write_note(data):
    introduction='''# Fixed ending certificates for H9 prefix 02 15 36

Fix the first two layers `01 23 45 | 02 15 36`. The tables below exclude
the31 specified third/fourth-layer pairs from seven-layer sorting
networks. They use sixteen explicit input permutations, threshold
partner guards, and five saturated-cone parity exclusions. No SAT
premise or enumeration of the remaining three layers is needed.

**Scope:** proving that these31 pairs cover all possible continuations
requires the separate third/fourth-layer hand classification. These
ending certificates alone are not a completed H9 class proof.

## 1. Mandatory partners after four layers

Let Q denote layer five, leaving two layers afterward. For an actual
comparator prefix, the ranks attainable at any wire form an interval:
swapping two consecutive ranks in an input changes any fixed output
rank by at most one, and adjacent rank swaps connect all permutations.
The two remaining layers give each Q output a forward cone of at most
four positions. Thus an observed rank gap of at least four is impossible
at any Q output of a sorting network.

At the cut before Q, let l and h be a wire's smallest and largest
observed ranks in the fixed bank. If h-l>=4, that wire is mandatory in Q.
For a prospective partner j, two necessary threshold rules follow:

* On every bank run with pivot value at most h-4, j must have value
  greater than h-4. Otherwise the comparison's maximum is at most h-4
  there but at least h on the high-anchor run.
* On every run with pivot value at least l+4, j must have value less
  than l+4. Otherwise the comparison's minimum is at least l+4 there
  but at most l on the low-anchor run.

The same rules applied from j's side may rule out an edge not excluded
from the pivot's side. These reciprocal guards are necessary even when
j itself is not mandatory. This is the arbitrary-width
[threshold-partner lemma](h9_feedback_round5_rank_partner.md).

An isolated mandatory pivot is impossible. Two mandatory pivots sharing
only one possible partner are also impossible because Q is a matching.

## 2. Saturated four-cone parity

Consider any wire with two layers P,S remaining. Its forward cone has
at most four positions. If it has four positions, it is the union of
two complete edges of the final matching S: its P comparison must have
two outputs, and both must be compared by S to distinct partners.
Therefore any two full four-position forward cones have an **even**
intersection, as each is a union of edges from one common matching S.

For a proposed Q edge, suppose explicit runs give a rank gap of exactly
three at each of its two outputs. The interval lemma forces four ranks
at each output. In any sorting completion, capacity forces the forward
cones to equal these four-rank intervals. An odd intersection of the
intervals therefore rules out the proposed Q edge. This argument needs
only the endpoint witnesses; it does not assume that the bank exhausts
the prefix image.

Five edges are excluded this way. After deleting edge24 in form1.4,
mandatory pivots1 and4 both have only partner3. In the other four forms,
the parity exclusion removes the sole remaining partner of a mandatory
pivot. The other26 forms already have an isolated pivot from threshold
guards alone.

## 3. The31 fixed prefixes

The case numbers refer to the eighteen third-layer representatives.
The labels here identify these explicit layer arrays; their separate
coverage proof is not an input to the endpoint calculation.

| Label | Third layer M | Fourth layer N | Mandatory pivots | Final obstruction |
|---|---|---|---|---|
'''
    lines=[introduction.rstrip()]
    for r in data['records']:
        pivots=','.join(str(p['pivot']) for p in r['pivots'])
        conclusion='isolated pivot' if r['kind']=='isolated' else ('isolated after parity '+edge_text([r['parity']['edge']]) if r['kind']=='isolated_with_parity' else 'pivots1,4 share partner3 after parity24')
        lines.append(f"| {r['case']}.{r['number']} | `{edge_text(r['third'])}` | `{edge_text(r['fourth'])}` | {pivots} | {conclusion} |")
    lines+=['','## 4. Sixteen explicit input permutations','','Ranks on original wires0 through8:','','| Input | Ranks |','|---|---|']
    for i,x in enumerate(data['rank_inputs']):lines.append(f"| {chr(65+i)} | `{''.join(map(str,x))}` |")
    lines+=['','## 5. Mandatory-pivot guards','','An endpoint entry A:0–B:5 gives observed ranks0 and5 on inputs A,B.',
            'A lo guard excludes the listed partners whose values are at most h-4 on that same run; a hi guard uses at least l+4.',
            'The directed remainder follows own guards. The remainder before parity also applies the reciprocal table below.','','| Label | Pivot | Endpoints | Guards | Directed remainder | Remainder before parity |','|---|---:|---|---|---|---|']
    for r in data['records']:
        for p in r['pivots']:
            lines.append(f"| {r['case']}.{r['number']} | {p['pivot']} | {ep(p)} | {'; '.join(gs(g) for g in p['guards'])} | {''.join(map(str,p['remaining'])) or 'empty'} | {''.join(map(str,p['allowed_before_parity'])) or 'empty'} |")
    lines+=['','| Label | Pivot | Candidate partner | Partner endpoints | Reciprocal guard |','|---|---:|---:|---|---|']
    for r in data['records']:
        for p in r['pivots']:
            for q in p['reciprocal']:
                lines.append(f"| {r['case']}.{r['number']} | {p['pivot']} | {q['pivot']} | {ep(q)} | {gs(q['guard'])} |")
    lines+=['','## 6. Five parity exclusions','','Each output interval contains four ranks. The displayed intersection has odd cardinality.','','| Label | Forbidden Q edge | Minimum-output endpoints | Maximum-output endpoints | Intersection |','|---|---|---|---|---|']
    for r in data['records']:
        p=r['parity']
        if p:
            a,b=p['edge'];lines.append(f"| {r['case']}.{r['number']} | `{a}{b}` | {ep(p['ranges'][0])} | {ep(p['ranges'][1])} | {''.join(map(str,p['odd_intersection']))} |")
    lines+=['','## 7. Fixed replay','','The [checker](verify/h9_recovery_021536_endings_check.py) reads the fixed sixteen inputs, evaluates all31 displayed prefixes, and checks every endpoint, threshold guard, reciprocal guard, parity interval, and final matching contradiction. It also reads back the printed tables.',
            'It uses no SAT solver, discovery import, search for inputs, or enumeration of nine-wire matchings. Its [result](results/h9-recovery-021536-endings-check.json) binds the certificate, note, and checker by hashes.','']
    (ROOT/'h9_recovery_021536_endings.md').write_text('\n'.join(lines))

def main():
    start=time.monotonic()
    source=ROOT/'results/h9-recovery-021536-endings-discovery.json'
    raw=json.loads(source.read_text()); seeds=sorted({lift(x) for x in itertools.product((0,1),repeat=9)})
    measurements=[];forms=[];pool=set()
    for c in raw['cases']:
        for number,r in enumerate(c['fourths'],1):
            key=(c['case'],number);prefix=(FIRST,SECOND,c['third'],r['fourth'])
            outputs=[run(prefix,x) for x in seeds]
            plan,parity=([(r['isolated'][0],[])],None) if r['isolated'] else EXCEPTIONS[key]
            forms.append(dict(case=key[0],number=number,third=c['third'],fourth=r['fourth'],plan=plan,parity=parity))
            for p,allowed in plan:
                for q in [None]+[v for v in range(9) if v!=p and v not in allowed]:
                    alternatives=[]
                    for op in (['idle'] if q is None else ['min','max']):
                        vals=[y[p] if op=='idle' else min(y[p],y[q]) if op=='min' else max(y[p],y[q]) for y in outputs]
                        lo,hi=min(vals),max(vals)
                        if hi-lo>=4:
                            alternatives.append((op,vals))
                            pool.update((seeds[vals.index(lo)],seeds[vals.index(hi)]))
                    assert alternatives,(key,p,q)
                    measurements.append(dict(key=key,pivot=p,partner=q,gap=4,alternatives=alternatives))
            if parity:
                for op,func in [('min',min),('max',max)]:
                    vals=[func(y[parity[0]],y[parity[1]]) for y in outputs]
                    lo,hi=min(vals),max(vals);assert hi-lo==3
                    pool.update((seeds[vals.index(lo)],seeds[vals.index(hi)]))
                    measurements.append(dict(key=key,parity=parity,output=op,gap=3,alternatives=[(op,vals)]))
    pool=sorted(pool);indices=[seeds.index(x) for x in pool]
    for r in measurements:
        r['alternatives']=[(op,[vals[i] for i in indices]) for op,vals in r['alternatives']]
    def satisfied(selected):
        return all(any(max(v[i] for i in selected)-min(v[i] for i in selected)>=r['gap'] for op,v in r['alternatives']) for r in measurements)
    rng=random.Random(21536);best=list(range(len(pool)))
    for attempt in range(12):
        selected=list(range(len(pool)));rng.shuffle(selected)
        for v in selected[:]:
            candidate=[i for i in selected if i!=v]
            if satisfied(candidate):selected=candidate
        if len(selected)<len(best):best=selected
        assert time.monotonic()-start<28
    inputs=[pool[i] for i in sorted(best)];records=[]
    for form in forms:
        outputs=[run((FIRST,SECOND,form['third'],form['fourth']),x) for x in inputs]
        pivots=[]
        for p,allowed in form['plan']:
            lo,hi,rows=guards(outputs,p);assert hi-lo>=4
            unique={}
            for g in rows:unique.setdefault(tuple(g['excluded']),g)
            excluded=set().union(*(set(g['excluded']) for g in rows))
            selected=cover(list(unique.values()),sum(1<<q for q in excluded));assert selected is not None
            remaining=sorted(set(range(9))-{p}-excluded)
            assert set(allowed)<=set(remaining),(form,p,allowed,remaining)
            reciprocal=[]
            for q in sorted(set(remaining)-set(allowed)):
                qlo,qhi,qrows=guards(outputs,q);g=next(g for g in qrows if p in g['excluded']);a,b=anchors(outputs,q,qlo,qhi,[g])
                reciprocal.append(dict(pivot=q,low=qlo,high=qhi,low_input=a,high_input=b,guard=g))
            a,b=anchors(outputs,p,lo,hi,selected)
            pivots.append(dict(pivot=p,low=lo,high=hi,low_input=a,high_input=b,guards=selected,remaining=remaining,reciprocal=reciprocal,allowed_before_parity=allowed))
        parity=None
        if form['parity']:
            edge=form['parity'];ranges=[]
            for op,func in [('min',min),('max',max)]:
                vals=[func(y[edge[0]],y[edge[1]]) for y in outputs];lo,hi=min(vals),max(vals);assert hi-lo==3
                ranges.append(dict(output=op,low=lo,high=hi,low_input=vals.index(lo),high_input=vals.index(hi)))
            overlap=set(range(ranges[0]['low'],ranges[0]['high']+1))&set(range(ranges[1]['low'],ranges[1]['high']+1))
            assert len(overlap)%2==1
            parity=dict(edge=edge,ranges=ranges,odd_intersection=sorted(overlap))
        for r in pivots:
            p=r['pivot'];forbiddenpartner=set(parity['edge'])-{p} if parity and p in parity['edge'] else set()
            r['allowed_after_parity']=sorted(set(r['allowed_before_parity'])-forbiddenpartner)
        if len(pivots)==1:
            assert not pivots[0]['allowed_after_parity'];kind='isolated_with_parity' if parity else 'isolated'
        else:
            neighbors=set().union(*(set(r['allowed_after_parity']) for r in pivots))
            assert len(neighbors)<len(pivots) and not neighbors&{r['pivot'] for r in pivots};kind='hall_with_parity'
        records.append(dict(case=form['case'],number=form['number'],third=form['third'],fourth=form['fourth'],kind=kind,pivots=pivots,parity=parity))
    data=dict(status='FIXED_ENDPOINT_CERTIFICATE',first=FIRST,second=SECOND,rank_inputs=inputs,records=records,
              discovery_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              scope='These certificates exclude the31 listed four-layer prefixes; separate hand arguments must prove their coverage.',
              no_sat_premise=True)
    dest=ROOT/'results/h9-recovery-021536-endings-certificate.json';dest.write_text(json.dumps(data,indent=2)+'\n')
    write_note(data)
    print(json.dumps(dict(inputs=len(inputs),records=len(records),pivots=sum(len(r['pivots']) for r in records),own_guards=sum(len(p['guards']) for r in records for p in r['pivots']),reciprocal_guards=sum(len(p['reciprocal']) for r in records for p in r['pivots']),parity=sum(bool(r['parity']) for r in records),seconds=time.monotonic()-start,certificate_sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2))

if __name__=='__main__':main()
