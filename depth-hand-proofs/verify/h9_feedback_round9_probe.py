#!/usr/bin/env python3
"""Small signed-prefix feedback for H9 03 14 67."""
import json,time
from pathlib import Path
from netlib import placements,matchings
from h9_feedback_reschedule_extend import prefix_state
from h9_feedback_round4_proof import propagated_order
FIRST=((0,1),(2,3),(4,5));SECOND=((0,3),(1,4),(6,7))
def main():
 start=time.monotonic();prefix=(FIRST,SECOND);rows={}
 for k in (2,3,4):
  for p in placements(9,k):
   r=prefix_state(prefix,p);count=len(r['gates']);h=max(r['depths'])
   if (k==2 and count<=2 and h<=1)or(k in(3,4)and count==0):
    sent=tuple(i for i,s in enumerate(r['state'])if s)
    rows.setdefault((k,sent),dict(placement=p,sentinels=sent,retained=r['gates'],demand=5-k))
 print('rows',len(rows))
 for key,r in rows.items():print(key,r)
 forbidden=propagated_order(prefix);layers=[m for m in matchings(9)if not set(m)&forbidden]
 survivors=[m for m in layers if all(sum(a not in r['sentinels']and b not in r['sentinels']for a,b in m)>=r['demand']for r in rows.values())]
 print('survivors',len(survivors));print(survivors)
 report=dict(status='DISCOVERY_ONLY',rows=list(rows.values()),survivors=survivors,elapsed_seconds=time.monotonic()-start)
 (Path(__file__).parents[1]/'results/h9-feedback-round9-probe.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
