#!/usr/bin/env python3
"""Bounded feedback: can the three selected B columns suffice at five crosses?"""
import itertools
import json
from pathlib import Path
import time
from d17_feedback_round3_probe import STATES,matching_core,step

ROOT=Path(__file__).parent


def complete(M):
    used={v for e in M for v in e};idle=[v for v in range(14) if v not in used]
    return list(M)+[tuple(idle[i:i+2]) for i in range(0,len(idle),2)]


def main():
    started=time.monotonic();tested=0;result=None
    for targets in itertools.permutations((8,9,11,12,13)):
        M=((0,1),(7,10))+tuple(zip(range(2,7),targets));rows={}
        selected=[5*r+c for r in range(4) for c in (1,2,3)]
        for i in selected:
            state=STATES[i]
            if sum(state[a]==state[b]==0 for a,b in M)>=4:continue
            S=tuple(v for v,x in enumerate(step(state,M)) if x)
            rows.setdefault(S,[]).append(i)
        checked=matching_core(list(rows.items()));tested+=1
        if checked['sat']:
            N=complete(checked['N']);profiles=[]
            for s in STATES:
                first=sum(s[a]==s[b]==0 for a,b in M);s2=step(s,M)
                second=sum(s2[a]==s2[b]==0 for a,b in N)
                profiles.append([first,second])
            assert all(max(profiles[i])>=4 for i in selected)
            result=dict(status='THREE_COLUMN_SURVIVOR',M=M,N=N,selected=selected,profiles=profiles,
                        failing_full_family=[i for i,p in enumerate(profiles) if max(p)<4])
            break
    if result is None:result=dict(status='NO_THREE_COLUMN_SURVIVOR')
    result.update(tested=tested,seconds=round(time.monotonic()-started,4),
                  scope='Static final-matching feedback; no full case606 conclusion')
    (ROOT/'results/d17-feedback-round5-probe.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
