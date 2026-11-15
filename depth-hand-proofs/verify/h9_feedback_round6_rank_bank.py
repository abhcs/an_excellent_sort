#!/usr/bin/env python3
"""Discover explicit endpoint witnesses for the 51 fixed fourth-layer forms."""
import itertools
import json
import random
import time
from pathlib import Path
from netlib import run
from h9_feedback_round6_probe import FIRST, SECOND
from h9_feedback_round4_rank_witnesses import lift


def main():
    start=time.monotonic();root=Path(__file__).parents[1]
    cases=json.loads((root/'results/h9-feedback-round6-fourths.json').read_text())['cases']
    seeds=sorted({lift(x) for x in itertools.product((0,1),repeat=9)})
    actions=[];records=[];pool=set()
    for case in cases:
        for number,ending in enumerate(case['fourths'],1):
            fourth=ending['fourth']
            prefix=(FIRST,SECOND,case['third'],fourth)
            values=[run(prefix,x) for x in seeds]
            isolated=[]
            for pivot in range(9):
                requirements=[]
                for partner in [None]+[v for v in range(9) if v!=pivot]:
                    choices=[]
                    for operation in (['idle'] if partner is None else ['min','max']):
                        v=[y[pivot] if operation=='idle' else min(y[pivot],y[partner]) if operation=='min' else max(y[pivot],y[partner]) for y in values]
                        lo,hi=min(v),max(v)
                        if hi-lo>=4:choices.append((operation,seeds[v.index(lo)],seeds[v.index(hi)]))
                    if not choices:break
                    requirements.append((partner,choices))
                if len(requirements)==9:isolated.append((pivot,requirements))
            assert isolated,(case['case'],number)
            pivot,requirements=isolated[0]
            for partner,choices in requirements:
                for _,low,high in choices:pool.update((low,high))
                actions.append(dict(case=case['case'],number=number,pivot=pivot,partner=partner,
                                    operations=[op for op,_,_ in choices],prefix=prefix))
            records.append(dict(case=case['case'],number=number,third=case['third'],fourth=fourth,pivot=pivot))
    pool=sorted(pool);measure=[]
    prefix_values={}
    for action in actions:
        key=(action['case'],action['number'])
        if key not in prefix_values:prefix_values[key]=[run(action['prefix'],x) for x in pool]
        out=prefix_values[key];p,q=action['pivot'],action['partner']
        measure.append([[y[p] if op=='idle' else min(y[p],y[q]) if op=='min' else max(y[p],y[q]) for y in out] for op in action['operations']])
    def covered(selected):
        return {i for i,choices in enumerate(measure) if any(max(v[j] for j in selected)-min(v[j] for j in selected)>=4 for v in choices)}
    rng=random.Random(31647);best=list(range(len(pool)))
    for attempt in range(4):
        selected=[rng.randrange(len(pool))]
        while len(covered(selected))<len(actions):
            old=covered(selected);remaining=[i for i in range(len(pool)) if i not in selected];rng.shuffle(remaining)
            winner=max(remaining,key=lambda i:len(covered(selected+[i])))
            if len(covered(selected+[winner]))==len(old):
                pair=max(itertools.combinations(remaining,2),key=lambda p:len(covered(selected+list(p))))
                assert len(covered(selected+list(pair)))>len(old)
                selected.extend(pair)
            else:selected.append(winner)
            assert time.monotonic()-start<45
        for i in selected[:]:
            trial=[j for j in selected if j!=i]
            if len(covered(trial))==len(actions):selected=trial
        if len(selected)<len(best):best=selected
    rows=[]
    for action,choices in zip(actions,measure):
        options=[]
        for op,v in zip(action['operations'],choices):
            low=min(best,key=lambda j:v[j]);high=max(best,key=lambda j:v[j])
            if v[high]-v[low]>=4:options.append((v[high]-v[low],op,low,high,v[low],v[high]))
        _,op,low,high,lo,hi=max(options)
        rows.append(dict(case=action['case'],number=action['number'],pivot=action['pivot'],partner=action['partner'],
                         output=op,low_input=best.index(low),low=lo,high_input=best.index(high),high=hi))
    out=dict(status='EXPLICIT_WITNESSES_FOUND',cases=records,inputs=[pool[i] for i in best],rows=rows,
             discovery_pool=len(pool),elapsed_seconds=time.monotonic()-start)
    (root/'results/h9-feedback-round6-rank-bank.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('cases','inputs','rows')}))
    print('inputs',len(best),'prefixes',len(records),'rows',len(rows))


if __name__=='__main__':main()
