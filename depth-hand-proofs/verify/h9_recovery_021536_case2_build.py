#!/usr/bin/env python3
"""Bounded local-mode discovery for case2; no matching enumeration or SAT."""
import hashlib
import itertools
import json
import random
import time
from pathlib import Path
from netlib import run
from h9_feedback_round4_rank_witnesses import lift

ROOT=Path(__file__).parents[1]
PREFIX=(((0,1),(2,3),(4,5)),((0,2),(1,5),(3,6)),((1,2),(3,4),(7,8)))

def local_outputs(y,p,q,r):
    if q is None:return {'idle':y[p]}
    z=y[q] if r is None else min(y[q],y[r]) if q<r else max(y[q],y[r])
    return {'min':min(y[p],z),'max':max(y[p],z)}

def compress(inputs):
    out=[run(PREFIX,x) for x in inputs];records=[]
    for p in range(9):
        for q in [None]+[v for v in range(9) if v!=p]:
            modes=[None] if q is None else [None]+[v for v in range(9) if v not in (p,q)]
            target=(1<<len(modes))-1;unique={}
            for a,b in itertools.combinations(range(len(inputs)),2):
                for op in (['idle'] if q is None else ['min','max']):
                    covered=[i for i,r in enumerate(modes) if abs(local_outputs(out[a],p,q,r)[op]-local_outputs(out[b],p,q,r)[op])>=4]
                    mask=sum(1<<i for i in covered)
                    if mask:unique.setdefault(mask,dict(inputs=[a,b],output=op,modes=[modes[i] for i in covered]))
            dp={0:[]}
            for mask,g in unique.items():
                for old,chosen in list(dp.items()):
                    new=old|mask
                    if new not in dp or len(chosen)+1<len(dp[new]):dp[new]=chosen+[g]
            assert target in dp
            records.append(dict(idle_N=p,Q_partner=q,guards=dp[target]))
    return records

def guard_text(g):
    a,b=g['inputs'];modes=','.join('I' if r is None else str(r) for r in g['modes'])
    return f"{chr(65+a)}–{chr(65+b)}/{g['output']} {{{modes}}}"

def write_note(data):
    intro='''# An odd-idle obstruction closes third-layer form2

The three fixed layers are

    C = 01 23 45 | 02 15 36 | 12 34 78.

**Claim.** C cannot be followed by four sorting layers on nine wires.
This excludes third-layer form2 in the H9 class `02 15 36`, independently
of any restrictions already imposed on the fourth layer.

## 1. A local obstruction for an arbitrary next matching

Name the four remaining layers N,Q,P,S. Since N is a matching on nine
wires, it leaves some wire p idle. Fix that p. Write y for the output
of C on an input permutation of ranks0 through8. At the cut after N,
wire p still holds y_p. If another wire q is idle in N, it holds y_q;
if it is compared with r, it holds min(y_q,y_r) when q<r and
max(y_q,y_r) when q>r. Because p is idle, r cannot equal p.

If Q leaves p idle, the observed range of y_p has gap at least four,
as witnessed in the table below. If Q pairs p with q, exactly eight
local N modes at q are possible: idle, or pairing with any r outside
{p,q}. The table supplies a rank gap of at least four at the minimum
or maximum output of that Q comparison in every such mode.

For any actual comparator prefix, attainable ranks at a wire form an
interval. (Interchanging consecutive input ranks changes each output
rank by at most one; such swaps connect all input permutations.) Thus
each witnessed gap forces at least five attainable ranks at the chosen
Q output. Two remaining layers P,S can route that value to at most
four positions, a contradiction. Both the Q-idle and every Q-partner
option are impossible, so no such N,Q,P,S can exist.

Only the local N mode at q matters. Other N gates leave p and q's
comparator inputs untouched, and other Q gates leave the selected
Q output untouched. Consequently this proof covers all N and Q
matchings without enumerating either layer.

The argument generalizes to any odd width: a fixed finite input bank
that gives these local rank gaps at least as large as the remaining
forward-cone capacity excludes every pair of next matchings. Here the
capacity is four.

## 2. Eleven explicit input runs

The second column is on the original wires; the third is its output
after the three displayed layers C.

| Input | Original ranks | After C |
|---|---|---|
'''
    lines=[intro.rstrip()]
    for i,x in enumerate(data['rank_inputs']):
        y=run(PREFIX,x);lines.append(f"| {chr(65+i)} | `{''.join(map(str,x))}` | `{''.join(map(str,y))}` |")
    lines+=['','## 3. Guards covering every local N mode','',
            'In each row N leaves p idle. The Q entry is either idle or its partner q.',
            'A guard `A–B/min {I,2,5}` says that the minimum Q output differs by at least4 between inputs A and B when q is idle in N (`I`) or has N partner2 or5. A max guard uses the maximum Q output. The N comparison itself always sends its minimum to the smaller-numbered wire.',
            'For a Q-idle row, the guard directly compares y_p on the two inputs. For every other row the listed mode sets together contain I and all seven possible partners r outside {p,q}. There are9 idle cases and9*8*8=576 paired local cases.','','| Idle N wire p | Q mode at p | Covering guards |','|---:|---|---|']
    for r in data['compressed_guards']:
        q='idle' if r['Q_partner'] is None else str(r['Q_partner'])
        lines.append(f"| {r['idle_N']} | {q} | {'; '.join(guard_text(g) for g in r['guards'])} |")
    lines+=['','## 4. Fixed verification','',
            'The [checker](verify/h9_recovery_021536_case2_check.py) evaluates only the eleven printed runs, validates all585 individual local witnesses and the140 covering guards, and checks complete local-mode coverage. It uses no SAT solver, input search, or matching enumeration.',
            'The [certificate](results/h9-recovery-021536-case2-certificate.json) fixes the runs and guards; the [audit](results/h9-recovery-021536-case2-check.json) binds the checker and proof note.','']
    (ROOT/'h9_recovery_021536_case2.md').write_text('\n'.join(lines))

def main():
    start=time.monotonic();seeds=sorted({lift(x) for x in itertools.product((0,1),repeat=9)})
    out=[run(PREFIX,x) for x in seeds];actions=[];pool=set()
    for p in range(9):
        modes=[(None,None)]+[(q,r) for q in range(9) if q!=p for r in [None]+[v for v in range(9) if v not in (p,q)]]
        assert len(modes)==65
        for q,r in modes:
            choices=[]
            for op in (['idle'] if q is None else ['min','max']):
                vals=[local_outputs(y,p,q,r)[op] for y in out];lo,hi=min(vals),max(vals)
                if hi-lo>=4:
                    choices.append((op,vals));pool.update((seeds[vals.index(lo)],seeds[vals.index(hi)]))
            assert choices,(p,q,r)
            actions.append(dict(idle_N=p,Q_partner=q,N_partner_of_Q_partner=r,choices=choices))
    pool=sorted(pool);indices=[seeds.index(x) for x in pool]
    for action in actions:action['choices']=[(op,[vals[i] for i in indices]) for op,vals in action['choices']]
    def passes(selected):
        return all(any(max(v[i] for i in selected)-min(v[i] for i in selected)>=4 for op,v in a['choices']) for a in actions)
    rng=random.Random(2026111602);best=list(range(len(pool)))
    for attempt in range(20):
        selected=list(range(len(pool)));rng.shuffle(selected)
        for i in selected[:]:
            trial=[j for j in selected if j!=i]
            if passes(trial):selected=trial
        if len(selected)<len(best):best=selected
        assert time.monotonic()-start<28
    best=sorted(best);inputs=[pool[i] for i in best];rows=[]
    for a in actions:
        alternatives=[]
        for op,vals in a['choices']:
            lo=min(best,key=lambda i:vals[i]);hi=max(best,key=lambda i:vals[i])
            if vals[hi]-vals[lo]>=4:alternatives.append((vals[hi]-vals[lo],op,lo,hi,vals[lo],vals[hi]))
        _,op,lo,hi,low,high=max(alternatives)
        rows.append(dict(idle_N=a['idle_N'],Q_partner=a['Q_partner'],N_partner_of_Q_partner=a['N_partner_of_Q_partner'],output=op,low_input=best.index(lo),low=low,high_input=best.index(hi),high=high))
    compressed=compress(inputs)
    data=dict(status='FIXED_LOCAL_MODE_CERTIFICATE',prefix=PREFIX,rank_inputs=inputs,rows=rows,compressed_guards=compressed,
              scope='For every matching N, its idle wire has no possible Q mode leaving a two-layer sorting suffix.',
              no_sat=True,no_matching_enumeration=True)
    dest=ROOT/'results/h9-recovery-021536-case2-certificate.json';dest.write_text(json.dumps(data,indent=2)+'\n')
    write_note(data)
    print(json.dumps(dict(inputs=len(inputs),rows=len(rows),compressed_guards=sum(len(r['guards'])for r in compressed),max_guards=max(len(r['guards'])for r in compressed),pool=len(pool),seconds=time.monotonic()-start,certificate_sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2))

if __name__=='__main__':main()
