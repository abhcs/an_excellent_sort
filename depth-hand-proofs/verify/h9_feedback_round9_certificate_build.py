#!/usr/bin/env python3
"""Package fixed premises for the two fence-image H9 cases."""
import hashlib,itertools,json
from pathlib import Path
from h9_feedback_round4_proof import run
from h9_feedback_round5_partner_build import guards,cover,anchors
ROOT=Path(__file__).parents[1]
FIRST=((0,1),(2,3),(4,5));SECOND=((0,3),(1,4),(6,7))
def es(edges):return ' '.join(''.join(map(str,e))for e in edges)or'none'
def ps(p):return ' '.join(('+'if s>0 else'-')+str(i)for i,s in sorted((int(i),s)for i,s in p.items()))
def ep(r):return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"
def gs(g):return f"{chr(65+g['input'])} {'lo'if g['kind']=='low'else'hi'}:{''.join(map(str,g['excluded']))}"
RECIPES={1:dict(kind='extensions',T=[3,4,5,7],outside=[1,6]),
2:dict(kind='three_extensions',T=[3,4,5,8],outside=[1,6,7]),
3:dict(kind='extensions',T=[3,4,5,7],outside=[1,6]),
4:dict(kind='three_extensions',T=[3,4,5,8],outside=[1,6,7]),
5:dict(kind='three_extensions',T=[1,4,6,7],outside=[3,2,8]),
6:dict(kind='triangle',T=[4,5,6],outside_pairs=[[0,1],[3,8]]),
7:dict(kind='extensions',T=[1,4,5,6],outside=[2,7]),
8:dict(kind='extensions',T=[1,4,7,8],outside=[3,2]),
9:dict(kind='shared_pair',T=[1,2,4,5],outside=[0,8],pair=[1,5],S=[3,6,7],perfect=[3,6,7,8]),
10:dict(kind='local_table'),11:dict(kind='three_extensions',T=[3,5,6,8],outside=[1,4,7]),
12:dict(kind='triangle_contradiction',T=[3,4,8])}
def main():
 files=[ROOT/f'results/h9-feedback-round9-{x}.json'for x in('fourths','residual','rank-bank')]
 raw,res,rank=[json.loads(p.read_text())for p in files];cases=[]
 for c,rs in zip(raw['cases'],res['cases']):
  number=c['case'];forbid=set(map(tuple,c['forbidden']));branches=[]
  for row in(rs['records']if number==10 else[]):
   free=set(row['free']);selected=row['clauses'];anchor=min(selected,key=lambda x:(len(x['edges']),-x['need'],x['row']));arms=[]
   for e in anchor['edges']:
    e=tuple(e);left=free-set(e);second=set(itertools.combinations(sorted(left),2))-forbid;pending=[];bad=False
    for x in selected:
     need=x['need']-(e in map(tuple,x['edges']))
     if need>1:bad=True
     if need>0:pending.append(x['row']);second &= set(map(tuple,x['edges']))
    if bad:second=set()
    arms.append(dict(edge=e,pending=pending,impossible_need_two=bad,optional=not pending,seconds=sorted(second)))
   branches.append(dict(base=row['base'],free=row['free'],clauses=selected,anchor=anchor['row'],arms=arms,completions=row['completions']))
  cases.append(dict(case=number,third=c['third'],forbidden=c['forbidden'],rows=c['rows'],recipe=RECIPES[number],base_real=rs['base_real'],branches=branches,fourths=[n['fourth']for n in c['fourths']]))
 records=[]
 for form in rank['cases']:
  out=[run((FIRST,SECOND,form['third'],form['fourth']),x)for x in rank['inputs']];p=form['pivot'];lo,hi,rows=guards(out,p);unique={}
  for g in rows:unique.setdefault(tuple(g['excluded']),g)
  target=sum(1<<q for q in set().union(*(set(g['excluded'])for g in rows)));chosen=cover(list(unique.values()),target);assert chosen is not None
  remaining=sorted(set(range(9))-{p}-{q for g in chosen for q in g['excluded']});assert set(form['allowed'])<=set(remaining)
  reciprocal=[]
  for q in sorted(set(remaining)-set(form['allowed'])):
   qlo,qhi,qrows=guards(out,q);g=next(g for g in qrows if p in g['excluded']);a,b=anchors(out,q,qlo,qhi,[g])
   reciprocal.append(dict(pivot=q,low=qlo,high=qhi,low_input=a,high_input=b,guard=g))
  a,b=anchors(out,p,lo,hi,chosen)
  records.append(dict(case=form['case'],number=form['number'],third=form['third'],fourth=form['fourth'],pivot=p,allowed=form['allowed'],low=lo,high=hi,low_input=a,high_input=b,guards=chosen,remaining=remaining,reciprocal=reciprocal))
 data=dict(status='FIXED_HAND_CERTIFICATE',first=FIRST,second=SECOND,other_second=[[0,3],[1,6],[2,7]],image_map=[0,2,1,6,3,7,4,5,8],duality=[4,3,5,1,0,2,7,6,8],cases=cases,rank_inputs=rank['inputs'],rank_records=records,
           provenance={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files})
 dest=ROOT/'results/h9-feedback-round9-certificate.json';dest.write_text(json.dumps(data,indent=2)+'\n')
 lines=['# Fixed tables for the two fence-image H9 cases','','Finite premises of the [hand proof](h9_feedback_round9_fence6.md).','Cases refer to L2=03 14 67; its image transfers to03 16 27.','','## 1. Third layers and ordered pairs','','| Case | M | Forbidden N pairs |','|---:|---|---|']
 for c in cases:lines.append(f"| {c['case']} | `{es(c['third'])}` | `{es(c['forbidden'])}` |")
 lines+=['','## 2. Five-real demands','','Each row retains exactly3−d RR gates through L3 and therefore requires d N edges inside its real set.','','| Case | Row | Original sentinels | Real set after M | Demand |','|---:|---:|---|---|---:|']
 for c in cases:
  for i,r in enumerate(c['rows'],1):lines.append(f"| {c['case']} | {i} | `{ps(r['placement'])}` | {''.join(map(str,r['real']))} | {r['demand']} |")
 lines+=['','## 3. The twelve local bases for case10','','The base real set is12456. A residual clause `row:k(edges)` requires k listed edges.','Choose an anchor edge e. Only one additional edge can fit, so it must belong to every unmet clause.','An empty intersection or a residual demand2 makes the branch impossible.','','| Base | Residual clauses | Anchor | Edge branches | Completions on unused wires |','|---|---|---:|---|---|']
 for r in cases[9]['branches']:
  cs='; '.join(f"{x['row']}:{x['need']}({es(x['edges'])})"for x in r['clauses'])
  arms='; '.join(es([x['edge']])+'→'+('optional 'if x['optional']else'')+('{'+es(x['seconds'])+'}'if x['seconds']else('none'if x['optional']else'∅'))for x in r['arms'])or'empty anchor'
  comp=' / '.join(es(x)for x in r['completions'])or'impossible';lines.append(f"| `{es(r['base'])}` | {cs} | {r['anchor']} | {arms} | `{comp}` |")
 lines+=['','## 4. All33 N forms','','An isolated pivot has no partner. A Hall pair has two mandatory pivots sharing only partner2.','','| Label | N | Rank obstruction |','|---|---|---|']
 for c in cases:
  for i,n in enumerate(c['fourths'],1):
   rs=[r for r in records if(r['case'],r['number'])==(c['case'],i)];kind=('isolated '+str(rs[0]['pivot']))if len(rs)==1 else('Hall '+','.join(str(r['pivot'])for r in rs)+'→2')
   lines.append(f"| {c['case']}.{i} | `{es(n)}` | {kind} |")
 lines+=['','## 5. Seventeen concrete rank inputs','','Ranks are listed on original wires0 through8.','','| Input | Ranks |','|---|---|']
 for i,x in enumerate(rank['inputs']):lines.append(f"| {chr(65+i)} | `{''.join(map(str,x))}` |")
 lines+=['','## 6. Fixed threshold guards','','A lo guard excludes partners at most high−4, and a hi guard excludes partners at least low+4,','on an input where the pivot is on that same side of the threshold. All pivot spans are at least four.','Directed remainders are checked reciprocally below; the final remainder is empty or the singleton2.','','| Label | Pivot | Endpoints | Guards | Directed remainder | Final remainder |','|---|---:|---|---|---|---|']
 for r in records:lines.append(f"| {r['case']}.{r['number']} | {r['pivot']} | {ep(r)} | {'; '.join(gs(g)for g in r['guards'])} | {''.join(map(str,r['remaining']))or'empty'} | {''.join(map(str,r['allowed']))or'empty'} |")
 lines+=['','| Label | Pivot | Candidate | Candidate endpoints | Reciprocal guard |','|---|---:|---:|---|---|']
 for r in records:
  for q in r['reciprocal']:lines.append(f"| {r['case']}.{r['number']} | {r['pivot']} | {q['pivot']} | {ep(q)} | {gs(q['guard'])} |")
 lines+=['','The [fixed checker](verify/h9_feedback_round9_proof.py) validates these premises and the structural matching recipes.','Its [audit](results/h9-feedback-round9-proof.json) records counts and hashes.','']
 (ROOT/'h9_feedback_round9_tables.md').write_text('\n'.join(lines))
 print('certificate',hashlib.sha256(dest.read_bytes()).hexdigest(),'demands',sum(len(c['rows'])for c in cases),'guard rows',len(records),'own',sum(len(r['guards'])for r in records),'reciprocal',sum(len(r['reciprocal'])for r in records))
if __name__=='__main__':main()
