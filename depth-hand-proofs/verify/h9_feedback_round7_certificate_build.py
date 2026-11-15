#!/usr/bin/env python3
"""Package the fixed local matching and rank-threshold proof tables."""
import hashlib,itertools,json
from pathlib import Path
from h9_feedback_round4_proof import run
from h9_feedback_round5_partner_build import guards,cover,anchors
ROOT=Path(__file__).parents[1]
FIRST=((0,1),(2,3),(4,5));SECOND=((0,3),(1,6),(5,7))
def es(edges):return ' '.join(''.join(map(str,e)) for e in edges) or 'none'
def ps(p):return ' '.join(('+' if s>0 else '-')+str(i) for i,s in sorted((int(i),s) for i,s in p.items()))
def ep(r):return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"
def gs(g):return f"{chr(65+g['input'])} {'lo' if g['kind']=='low' else 'hi'}:{''.join(map(str,g['excluded']))}"
def main():
 discovery=ROOT/'results/h9-feedback-round7-fourths.json';resfile=ROOT/'results/h9-feedback-round7-residual.json';rankfile=ROOT/'results/h9-feedback-round7-rank-bank.json'
 raw=json.loads(discovery.read_text());res=json.loads(resfile.read_text());rank=json.loads(rankfile.read_text());cases=[]
 for c,rs in zip(raw['cases'],res['cases']):
  if c['case'] in (2,5):continue
  number=c['case'];assert number==rs['case'];forbid=set(map(tuple,c['forbidden']));branches=[]
  for row in (rs['records'] if number in (1,3) else []):
   base=row['base'];free=set(row['free']);allowed=set(itertools.combinations(sorted(free),2))-forbid
   selected=row['clauses'];anchor=min(selected,key=lambda x:(len(x['edges']),-x['need'],x['row']));arms=[]
   for edge in anchor['edges']:
    edge=tuple(edge);left=free-set(edge);possible=set(itertools.combinations(sorted(left),2))-forbid;pending=[];impossible=False
    for clause in selected:
     need=clause['need']-(edge in map(tuple,clause['edges']))
     if need>1:impossible=True
     if need>0:pending.append(clause['row']);possible &= set(map(tuple,clause['edges']))
    if impossible:possible=set()
    arms.append(dict(edge=edge,pending=pending,impossible_need_two=impossible,optional=not pending,seconds=sorted(possible)))
   branches.append(dict(base=base,free=sorted(free),clauses=selected,anchor=anchor['row'],arms=arms,completions=row['completions']))
  cases.append(dict(case=number,third=c['third'],forbidden=c['forbidden'],rows=c['rows'],base_real=rs['base_real'],branches=branches,
                    fourths=[r['fourth'] for r in c['fourths']]))
 records=[]
 for form in rank['cases']:
  outputs=[run((FIRST,SECOND,form['third'],form['fourth']),x) for x in rank['inputs']];options=[]
  for p in range(9):
   lo,hi,rows=guards(outputs,p)
   if hi-lo<4:continue
   # Duplicate masks never improve a cover; retain the earliest bank witness.
   unique={}
   for g in rows:unique.setdefault(tuple(g['excluded']),g)
   target=sum(1<<q for q in set().union(*(set(g['excluded']) for g in rows)))
   chosen=cover(list(unique.values()),target);assert chosen is not None
   remaining=sorted(set(range(9))-{p}-{q for g in chosen for q in g['excluded']});reciprocal=[]
   for q in remaining:
    qlo,qhi,qrows=guards(outputs,q);candidate=[g for g in qrows if p in g['excluded']]
    if not candidate:break
    g=candidate[0];a,b=anchors(outputs,q,qlo,qhi,[g]);reciprocal.append(dict(pivot=q,low=qlo,high=qhi,low_input=a,high_input=b,guard=g))
   else:
    a,b=anchors(outputs,p,lo,hi,chosen);r=dict(case=form['case'],number=form['number'],third=form['third'],fourth=form['fourth'],pivot=p,low=lo,high=hi,low_input=a,high_input=b,guards=chosen,remaining=remaining,reciprocal=reciprocal)
    options.append((len(chosen)+len(reciprocal),len(reciprocal),p,r))
  assert options;records.append(min(options,key=lambda x:x[:3])[-1])
 triangles=[dict(case=c,e=e,t=t,first_row=a,forced=f,second_row=b) for c,e,t,a,f,b in [(4,[4,5],8,4,[0,1],6),(4,[4,8],5,2,[0,1],5),(4,[5,8],4,2,[0,1],5),(6,[4,5],8,2,[1,2],5),(6,[4,8],5,3,[1,2],6),(6,[5,8],4,2,[1,2],5)]]
 sinks=[dict(case=1,number=2,placement={0:-1,7:-1},old_sink=[3,6]),dict(case=3,number=2,placement={0:-1,4:1},old_sink=[1,2])]
 data=dict(status='FIXED_HAND_CERTIFICATE',third_forms=[c['third'] for c in raw['cases']],triangles=triangles,sinks=sinks,transfer_certificate_sha256='c258d102a019b789a5a01edfae1b410629d1e61f8a2ba3f1976e09c6eabf05ae',first=FIRST,second=SECOND,cases=cases,rank_inputs=rank['inputs'],rank_records=records,
           provenance={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (discovery,resfile,rankfile)})
 out=ROOT/'results/h9-feedback-round7-certificate.json';out.write_text(json.dumps(data,indent=2)+'\n')
 lines=['# Fixed tables for H9 `03 16 57`','','These tables supply the finite premises of the [hand proof](h9_feedback_round7_031657.md).','Comparator names have two digits; longer strings denote sets of positions.','',
 '## 1. Third layers and propagated order','','| Case | M=L3 | Forbidden N=L4 pairs |','|---:|---|---|']
 for c in cases:lines.append(f"| {c['case']} | `{es(c['third'])}` | `{es(c['forbidden'])}` |")
 lines+=['','## 2. Five-real demands','','Every row retains exactly `3-demand` RR gates through L3. Signed inputs are original input positions.','','| Case | Row | Original sentinels | Real positions after M | Demand on N |','|---:|---:|---|---|---:|']
 for c in cases:
  for i,r in enumerate(c['rows'],1):lines.append(f"| {c['case']} | {i} | `{ps(r['placement'])}` | {''.join(map(str,r['real']))} | {r['demand']} |")
 lines+=['','## 3. Local fourth-layer classifications','','For cases1 and3, a displayed demand-two real set supplies two base edges.','There are exactly twelve permitted bases. The residual clauses are written `row:need(edges)`; only those rows are used.','At most two edges fit on the five unused vertices. Branch on one edge of the indicated anchor clause.','A branch `e→F` requires the other edge to belong to F; `e→∅` is impossible.','The notation `e→optional F` also permits no second edge.','The intersection rule in the main proof verifies each branch directly.','Optional unused edges are included, so no maximality assumption is made.','']
 for c in cases:
  if c['case'] not in (1,3):continue
  lines += [f"### Case {c['case']}: base set {''.join(map(str,c['base_real']))}",'', '| Base | Residual clauses | Anchor | Edge branches | Completions on unused wires |','|---|---|---:|---|---|']
  for r in c['branches']:
   clauses='; '.join(f"{x['row']}:{x['need']}({es(x['edges'])})" for x in r['clauses'])
   arms='; '.join(es([x['edge']])+'→'+('optional ' if x['optional'] else '')+('{'+es(x['seconds'])+'}' if x['seconds'] else ('none' if x['optional'] else '∅')) for x in r['arms']) or 'empty anchor'
   comp=' / '.join(es(x) for x in r['completions']) or 'impossible'
   lines.append(f"| `{es(r['base'])}` | {clauses} | {r['anchor']} | {arms} | `{comp}` |")
  lines.append('')
 lines += ['## 4. N forms and isolated mandatory pivots','','Sixteen rows have an isolated mandatory Q=L5 pivot by the threshold certificate in §6.','Two rows have sink restrictions in the main proof. Cases2 and5 transfer to the previous class.','','| Label | N | Pivot |','|---|---|---:|']
 for c in cases:
  for i,n in enumerate(c['fourths'],1):
   pivot=next((r['pivot'] for r in records if (r['case'],r['number'])==(c['case'],i)),'sink')
   lines.append(f"| {c['case']}.{i} | `{es(n)}` | {pivot} |")
 lines += ['','## 5. Nineteen concrete rank inputs','','The entries are ranks on original wires0 through8. Only these permutations are evaluated by the rank checker.','','| Input | Ranks |','|---|---|']
 for i,x in enumerate(rank['inputs']):lines.append(f"| {chr(65+i)} | `{''.join(map(str,x))}` |")
 lines += ['','## 6. Threshold partner intersections','','At the L4 cut, each pivot has the displayed endpoint ranks.','A `lo` guard excludes the listed partners because pivot and partner are both at most `high−4` on that input;','a `hi` guard uses values at least `low+4`. Any remaining directed partners fail reciprocity in the following table.','All pivot spans are at least four, forbidding an idle pivot.','','| Label | Pivot | Endpoints | Guards | Remaining |','|---|---:|---|---|---|']
 for r in records:lines.append(f"| {r['case']}.{r['number']} | {r['pivot']} | {ep(r)} | {'; '.join(gs(g) for g in r['guards'])} | {''.join(map(str,r['remaining'])) or 'empty'} |")
 lines += ['','| Label | Pivot | Candidate | Candidate endpoints | Reciprocal guard |','|---|---:|---:|---|---|']
 for r in records:
  for q in r['reciprocal']:lines.append(f"| {r['case']}.{r['number']} | {r['pivot']} | {q['pivot']} | {ep(q)} | {gs(q['guard'])} |")
 lines += ['','The [independent fixed checker](verify/h9_feedback_round7_proof.py) reads back these printed tables,','checks local clause intersections and signed restrictions, and evaluates the nineteen fixed rank inputs.','It does not enumerate nine-wire matchings or consult any discovery result.','Its [audit](results/h9-feedback-round7-proof.json) records counts and hashes.','']
 (ROOT/'h9_feedback_round7_tables.md').write_text('\n'.join(lines))
 print('certificate sha256',hashlib.sha256(out.read_bytes()).hexdigest(),'local branches',sum(len(r['arms']) for c in cases for r in c['branches']),'own guards',sum(len(r['guards']) for r in records),'reciprocal guards',sum(len(r['reciprocal']) for r in records))
if __name__=='__main__':main()
