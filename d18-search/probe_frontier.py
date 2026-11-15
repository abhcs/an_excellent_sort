#!/usr/bin/env python3
"""Exact probe-support necessary conditions at a cut before a sorting suffix.

Enumerate every adjacent pair of binary INPUTS, map both through the fixed
prefix, and deduplicate. Through any comparator they differ on one wire. If
there are s layers after the cut, all such differences of a given weight must
lie in a common output cone of size at most 2**s. UNSAT refutes the prefix;
SAT only satisfies this necessary condition.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from pysat.card import CardEnc, EncType
from netsat import Model, neg, window, apply_layers, prefix_images


class ProbeModel(Model):
    def simulate_to_cut(self, x, free):
        a, e = window(x, self.n)
        cur = {k: bool((x >> k)&1) for k in range(self.n)}
        for t in range(free):
            new = {k: self.new_var() if a<=k<=e else cur[k] for k in range(self.n)}
            for k in range(a,e+1):
                self.add([neg(cur[k]),new[k],self.Down(t,k,e)])
                self.add([cur[k],neg(new[k]),self.Up(t,a,k)])
            for (i,j), g in self.g[t].items():
                if not (a<=i<j<=e):
                    continue
                oi,oj,ni,nj = cur[i],cur[j],new[i],new[j]
                self.add([-g,neg(oi),nj])
                self.add([-g,oi,oj,neg(nj)])
                self.add([-g,neg(oi),neg(oj),ni])
                self.add([-g,oj,neg(ni)])
            cur = new
        return cur


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--result',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--cut',type=int,default=6)
    ap.add_argument('--depth',type=int)
    ap.add_argument('--solver',default='cadical195')
    ap.add_argument('--both',action='store_true',help='also bound ranks per channel by the forward cone')
    ap.add_argument('--route',action='store_true',help='all probe supports must route through the same last two matchings')
    ap.add_argument('--checker',type=Path,help='export DRAT and verify UNSAT independently')
    ap.add_argument('--witness',type=Path,help='fix the free layers to a known full sorter as a positive control')
    args = ap.parse_args()
    original = json.loads(args.result.read_text())
    prefix,n = original['prefix'],len(original['output_permutation'])
    depth = args.depth or original['depth']
    free = args.cut-len(prefix)
    assert 0<free<depth-len(prefix)
    if args.route:
        assert depth-args.cut==2
    started = time.monotonic()
    images = [apply_layers(prefix,x) for x in range(1<<n)]
    universe = sorted(set(images))
    probes = sorted({(images[x],images[x|(1<<i)]) for x in range(1<<n)
                     for i in range(n) if not x&(1<<i)})
    assert all((x^y).bit_count()==1 and x&y==x for x,y in probes)
    if args.checker:
        import netsat
        from prefix_drat import RecordingSolver
        netsat.Solver=RecordingSolver
    # Last-layer variables are unused here. End constraints are omitted;
    # full-prefix redundancy elimination remains a valid normal form.
    m = ProbeModel(n,depth-len(prefix),universe,phi=args.route,solver=args.solver)
    if args.witness:
        from netsat import verify_all
        witness=json.loads(args.witness.read_text())['network']
        assert len(witness)==depth and witness[:len(prefix)]==prefix and verify_all(n,witness)
        for t,layer in enumerate(witness[len(prefix):]):
            chosen=set(map(tuple,layer))
            assert chosen<=set(m.g[t])
            for edge,v in m.g[t].items():
                m.add([v if edge in chosen else -v])
    states = {x:m.simulate_to_cut(x,free) for x in universe}
    supports = [[m.new_var() for _ in range(n)] for _ in range(n)]
    for x,y in probes:
        rank = n-y.bit_count()
        for k in range(n):
            # Difference (0,1) forces k into this rank's support.
            m.add([states[x][k],neg(states[y][k]),supports[rank][k]])
    bounded_rows=[('rank',i,row) for i,row in enumerate(supports)]
    if args.both:
        bounded_rows += [('channel',i,list(column)) for i,column in enumerate(zip(*supports))]
    bound_groups=[]
    for kind,index,row in bounded_rows:
        begin=m.ncl
        enc = CardEnc.atmost(row,2**(depth-args.cut),top_id=m.nv,encoding=EncType.seqcounter)
        m.nv = max(m.nv,enc.nv)
        for clause in enc.clauses:
            m.add(clause)
        bound_groups.append(dict(kind=kind,index=index,clause_begin=begin,clause_end=m.ncl))
    if args.route:
        pen,last=m.g[-2:]
        def gate(layer,a,b):
            return layer.get((min(a,b),max(a,b)),False) if a!=b else True
        for rank in range(n):
            for channel in range(n):
                if rank==channel:
                    continue
                paths=[gate(pen,channel,rank),gate(last,channel,rank)]
                for middle in (rank-1,rank+1):
                    if not 0<=middle<n or middle==channel:
                        continue
                    a,b=gate(pen,channel,middle),gate(last,middle,rank)
                    if a is False or b is False:
                        continue
                    v=m.new_var()
                    m.add([-v,a]); m.add([-v,b]); m.add([v,neg(a),neg(b)])
                    paths.append(v)
                m.add([-supports[rank][channel],*paths])
    result = dict(case_id=original['case_id'],depth=depth,cut=args.cut,
                  scope='Probe positions only; no data comparisons in the ending',both_directions=args.both,
                  shared_ending_routing=args.route,
                  prefix=prefix,inputs=len(universe),probes=len(probes),
                  variables=m.nv,clauses=m.ncl,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  independently_proof_checked=False,status='BUILT')
    if args.checker:
        certificate=args.out.with_suffix('')
        certificate.mkdir(parents=True,exist_ok=True)
        cnf=certificate/'problem.cnf'
        with cnf.open('w') as f:
            f.write(f'p cnf {m.nv} {len(m.S.clauses)}\n')
            for clause in m.S.clauses:
                f.write(' '.join(map(str,clause))+' 0\n')
        (certificate/'bound-groups.json').write_text(json.dumps(bound_groups,indent=2)+'\n')
        result['cnf_sha256']=hashlib.sha256(cnf.read_bytes()).hexdigest()
        result['certificate_directory']=str(certificate)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='prefix'}),flush=True)
    try:
        ok = m.S.solve()
        result['status']='SURVIVOR' if ok else 'UNSAT'
        if ok:
            layers=m.network(m.S.get_model())[:free]
            reached=[set() for _ in range(n)]
            for x,y in probes:
                a,b=apply_layers(layers,x),apply_layers(layers,y)
                assert (a^b).bit_count()==1
                reached[n-y.bit_count()].add((a^b).bit_length()-1)
            assert max(map(len,reached))<=2**(depth-args.cut)
            if args.both:
                assert max(sum(k in s for s in reached) for k in range(n))<=2**(depth-args.cut)
            if args.route:
                ending=m.network(m.S.get_model())[-2:]
                for rank,channels in enumerate(reached):
                    cone={rank}
                    for layer in reversed(ending):
                        cone=cone|{v for a,b in layer if a in cone or b in cone for v in (a,b)}
                    assert channels<=cone
                result['ending_matchings']=ending
            result.update(free_layers=layers,supports=[sorted(s) for s in reached])
        result['seconds']=round(time.monotonic()-started,3)
        if not ok and args.checker:
            proof=certificate/'proof.drat'
            proof.write_text('\n'.join(m.S.get_proof())+'\n')
            result['proof_sha256']=hashlib.sha256(proof.read_bytes()).hexdigest()
            check_start=time.monotonic()
            check=subprocess.run([str(args.checker.resolve()),str(cnf.resolve()),str(proof.resolve()),
                                  '-c',str((certificate/'core.cnf').resolve()),'-t','120'],
                                  capture_output=True,text=True,timeout=130)
            (certificate/'check.log').write_text(check.stdout+check.stderr)
            result.update(check_seconds=round(time.monotonic()-check_start,3),checker_returncode=check.returncode,
                          checker_sha256=hashlib.sha256(args.checker.read_bytes()).hexdigest(),
                          independently_proof_checked=check.returncode==0 and 's VERIFIED' in check.stdout)
            assert result['independently_proof_checked'],check.stdout[-2000:]+check.stderr
        args.out.write_text(json.dumps(result,indent=2)+'\n')
        print(result['status'],result['seconds'],flush=True)
    finally:
        m.S.delete()


if __name__=='__main__':
    main()
