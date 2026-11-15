#!/usr/bin/env python3
"""Compress the fixed rank bank into threshold partner intersections."""
import hashlib
import json
from pathlib import Path
from h9_feedback_round4_proof import run

FIRST=((0,1),(2,3),(4,5));SECOND=((0,2),(1,4),(5,6))


def guards(outputs,p,capacity=4):
    low=min(x[p] for x in outputs);high=max(x[p] for x in outputs);rows=[]
    for i,x in enumerate(outputs):
        if x[p]<=high-capacity:
            rows.append(dict(input=i,kind='low',excluded=[q for q in range(9) if q!=p and x[q]<=high-capacity]))
        if x[p]>=low+capacity:
            rows.append(dict(input=i,kind='high',excluded=[q for q in range(9) if q!=p and x[q]>=low+capacity]))
    return low,high,rows


def cover(rows,target):
    dp={0:[]}
    for row in rows:
        mask=sum(1<<q for q in row['excluded'])
        if not mask:continue
        for old,chosen in list(dp.items()):
            new=old|mask;candidate=chosen+[row]
            if new not in dp or len(candidate)<len(dp[new]):dp[new]=candidate
    return dp.get(target)


def anchors(outputs,p,low,high,chosen):
    indices=[r['input'] for r in chosen]
    a=next((i for i in indices if outputs[i][p]==low),next(i for i,x in enumerate(outputs) if x[p]==low))
    b=next((i for i in indices if outputs[i][p]==high),next(i for i,x in enumerate(outputs) if x[p]==high))
    return a,b


def endpoint_text(r):return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"
def guard_text(r):return f"{chr(65+r['input'])} {'lo' if r['kind']=='low' else 'hi'}:{''.join(map(str,r['excluded']))}"


def main():
    root=Path(__file__).parents[1];source=root/'results/h9-feedback-round5-certificate.json'
    fixed=json.loads(source.read_text());records=[]
    for case in fixed['rank_cases']:
        outputs=[run((FIRST,SECOND,case['third'],case['fourth']),x) for x in fixed['rank_inputs']]
        options=[]
        for p in range(9):
            lo,hi,rows=guards(outputs,p)
            if hi-lo<4:continue
            selected=cover(rows,511^(1<<p))
            if selected is not None:
                a,b=anchors(outputs,p,lo,hi,selected)
                options.append((len(selected),len({a,b}|{r['input'] for r in selected}),p,lo,hi,a,b,selected))
        reciprocal=[]
        if options:
            _,_,p,lo,hi,a,b,selected=min(options,key=lambda x:x[:3]);remaining=[]
        else:
            p=case['pivot'];lo,hi,rows=guards(outputs,p)
            excluded=set().union(*(set(r['excluded']) for r in rows));target=sum(1<<q for q in excluded)
            selected=cover(rows,target);assert selected is not None
            a,b=anchors(outputs,p,lo,hi,selected);remaining=sorted(set(range(9))-{p}-excluded)
            for q in remaining:
                qlo,qhi,qrows=guards(outputs,q);g=next(r for r in qrows if p in r['excluded'])
                qa,qb=anchors(outputs,q,qlo,qhi,[g])
                reciprocal.append(dict(pivot=q,low=qlo,high=qhi,low_input=qa,high_input=qb,guard=g))
        records.append(dict(case=case['case'],number=case['number'],pivot=p,low=lo,high=hi,
                            low_input=a,high_input=b,guards=selected,remaining=remaining,reciprocal=reciprocal))
    data=dict(status='FIXED_THRESHOLD_CERTIFICATE',capacity=4,original_certificate_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),records=records)
    (root/'results/h9-feedback-round5-partner-certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    proof='''# Rank-threshold partners: a reusable ending lemma

This general lemma compresses the47 ending arguments of the
[H9 case `02 14 56`](h9_feedback_round5_021456.md). It uses the same
fifteen concrete inputs; the accepted endpoint tables and certificate
remain unchanged. The compression is an alternate certificate, not a
new coverage claim.

## 1. The arbitrary-width lemma

Consider any comparator prefix on n inputs, followed by one matching Q
and then d further layers. Put c=2^d. Choose any finite bank of input
permutations of ranks0 through n−1. At the prefix cut let x_i denote
wire i on a bank run x, and let l_i,h_i be its smallest and largest
observed ranks.

**Threshold partner lemma.** If h_i−l_i≥c, Q must use i. Any Q partner
j must obey both rules on every bank run x:

* if x_i≤h_i−c, then x_j≥h_i−c+1;
* if x_i≥l_i+c, then x_j≤l_i+c−1.

For the first rule, some anchor run gives the comparison's maximum at
least h_i. If both inputs on another run were at most h_i−c, its maximum
would differ by at least c between the two runs. For the second, an
anchor gives the minimum at most l_i; both inputs at least l_i+c on
another run again give a gap of c. The attainable-rank interval lemma
then supplies at least c+1 ranks at that Q output, but its d remaining
layers can reach at most c final positions. The same argument applied
to an idle wire proves the mandatory-use assertion.

The interval lemma holds for every comparator prefix on arbitrary real
inputs: swaps of consecutive rank values connect the input permutations,
and each such swap changes any fixed output by at most one. Identifying
the two values proves that last assertion because a monotone value map
commutes with every comparator. Thus intermediate ranks are attained.

For each i, let C(i) be the set of other wires satisfying both threshold
rules. Every possible Q edge ij requires j∈C(i) **and** i∈C(j).
This reciprocity is essential: a partner may have a smaller low endpoint
or a larger high endpoint than the original pivot.

In fact, reciprocal compatibility exactly captures the endpoint-range
test on the chosen finite bank. The minimum output's observed low is
min(l_i,l_j), and the maximum output's observed high is max(h_i,h_j).
A forbidden minimum gap is witnessed by both inputs reaching at least
min(l_i,l_j)+c; apply the high rule at an endpoint attaining that smaller
low. A forbidden maximum gap is witnessed by both inputs being at most
max(h_i,h_j)−c; apply the low rule at an endpoint attaining that larger
high. These are also sufficient to witness the corresponding range gap.
Compatibility is only a necessary condition for a sorting completion.

This defines a general partner graph: retain ij exactly when both
membership conditions hold. Q must be a matching in this graph covering
every vertex with observed span at least c. An isolated mandatory vertex
is impossible. More generally, an independent set of mandatory vertices
with fewer neighbors than vertices is impossible by the matching bound.
The statement applies to every n and d, without a perfect-Q assumption.

## 2. Forty-seven short partner intersections

Here d=2 and c=4. Input letters refer to the unchanged fifteen-input
bank in the [original appendix](h9_feedback_round5_tables.md#4-fifteen-concrete-inputs).
An endpoint entry `A:2–B:7` gives the pivot's observed low and high.
A guard `C lo:012` excludes those listed partners because both their
values and the pivot value on input C are at most h−4. A `hi` guard
uses values at least l+4. The listed guards' union removes all partners
except those explicitly named in the remainder column. Every pivot's
endpoint gap is at least four, so leaving it idle is also impossible.

Forty-four rows have empty remainder immediately. For the other three,
the reciprocal table below applies the same lemma from each remaining
partner's side. Thus all47 ending forms are excluded without a table
of423 separate partner/output endpoint pairs.

| Label | Pivot | Endpoints | Guards and excluded partners | Remainder |
|---|---:|---|---|---|
'''
    lines=[proof.rstrip()]
    for r in records:
        guards_cell='; '.join(guard_text(g) for g in r['guards']);remainder=''.join(map(str,r['remaining'])) or 'empty'
        lines.append(f"| {r['case']}.{r['number']} | {r['pivot']} | {endpoint_text(r)} | {guards_cell} | {remainder} |")
    lines += ['','The remaining directed memberships fail as follows. Each guard excludes the original pivot, so reciprocity forbids that edge.','',
              '| Label | Original pivot | Candidate partner | Partner endpoints | Partner guard |','|---|---:|---:|---|---|']
    for r in records:
        for q in r['reciprocal']:
            lines.append(f"| {r['case']}.{r['number']} | {r['pivot']} | {q['pivot']} | {endpoint_text(q)} | {guard_text(q['guard'])} |")
    lines += ['','## 3. Verification','',
              'The [independent checker](verify/h9_feedback_round5_partner_proof.py) checks the original certificate hash, evaluates only the fixed fifteen inputs, reads back these printed rows, and verifies every threshold exclusion and reciprocal membership.',
              'It also cross-checks the exact equivalence with the finite-bank minimum/maximum range test. No matching enumeration, solver, or additional input search is used.',
              'The [audit](results/h9-feedback-round5-partner-proof.json) records the counts and source hashes.','']
    (root/'h9_feedback_round5_rank_partner.md').write_text('\n'.join(lines))
    print('direct',sum(not r['remaining'] for r in records),'reciprocal forms',sum(bool(r['remaining']) for r in records),
          'own guards',sum(len(r['guards']) for r in records),'reciprocal guards',sum(len(r['reciprocal']) for r in records))


if __name__=='__main__':main()
