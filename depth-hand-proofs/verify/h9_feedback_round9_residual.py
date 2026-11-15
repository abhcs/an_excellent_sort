#!/usr/bin/env python3
"""Bounded discovery of five-unused-wire matching clauses; not final proof."""
import itertools,json
from pathlib import Path
from h9_feedback_round4_proof import matchings,normalized
ROOT=Path(__file__).parents[1]
def es(m):return ' '.join(''.join(map(str,e)) for e in m) or '-'
def main():
 data=json.loads((ROOT/'results/h9-feedback-round9-fourths.json').read_text());allrecords=[]
 for c in data['cases']:
  number=c['case'];forbid=set(map(tuple,c['forbidden']));r=next(r for r in c['rows'] if r['demand']==2);bases=[m for m in matchings(list(r['real'])) if len(m)==2 and not set(m)&forbid];records=[]
  if number==10:print('CASE',number,'BASE',r['real'])
  for base in bases:
   used=set(sum(base,()));free=sorted(set(range(9))-used);allowed=set(itertools.combinations(free,2))-forbid
   clauses=[]
   for i,row in enumerate(c['rows'],1):
    need=row['demand']-sum(a in row['real'] and b in row['real'] for a,b in base)
    if need>0:clauses.append(dict(row=i,need=need,edges=sorted(e for e in allowed if set(e)<=set(row['real']))))
   ms=[m for m in matchings(free) if set(m)<=allowed]
   def ok(m,cs):return all(len(set(m)&set(map(tuple,x['edges'])))>=x['need'] for x in cs)
   passing=[m for m in ms if ok(m,clauses)];selected=clauses[:]
   for x in sorted(clauses,key=lambda x:-len(x['edges'])):
    rest=[y for y in selected if y is not x]
    if [m for m in ms if ok(m,rest)]==passing:selected.remove(x)
   if number==10:print(es(base),' | ','; '.join(str(x['row'])+':'+str(x['need'])+'('+es(x['edges'])+')' for x in selected),' => ', '; '.join(es(x) for x in passing))
   records.append(dict(base=base,free=free,clauses=selected,completions=passing))
  allrecords.append(dict(case=number,base_real=r['real'],records=records))
 (ROOT/'results/h9-feedback-round9-residual.json').write_text(json.dumps(dict(status='DISCOVERY_ONLY',cases=allrecords),indent=2)+'\n')
if __name__=='__main__':main()
